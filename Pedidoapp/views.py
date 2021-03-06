#!/usr/bin/env python
#-*- coding: utf-8 -*- 

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from Pedidoapp.models import Pedido, Especialidad, Encargado, Articulo, Bodega, Pedido_Extra
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import Context
from datetime import datetime
from Pedidoapp.forms import PedidoEditForm,PedAdminEditForm, EstadisticaForm, ExtraForm
from django.template.context import RequestContext
from django.template import RequestContext
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.shortcuts import get_list_or_404, get_object_or_404
from django.db import models
from django.db.models import Count
from django.core.urlresolvers import reverse
import datetime
from django.utils import timezone
from django.views.generic import CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import psycopg2
import sys
import json

from django.contrib.auth.views import login


#modificar filtracion de las especialidades no es necesario mostrar numero de articulos, aun asi, si el numero de entregados
#o el numero de pendientes filtrar por estos camopos: esp = Especialida
def home(request):
    user = request.user
    if user.is_superuser:
      especialidad = Especialidad.objects.filter(estado="pendiente")
      acceso = Especialidad.objects.filter(acceso=0)
      count = Especialidad.objects.filter(estado="pendiente").count()
      count2 = Especialidad.objects.filter(estado="entregado").count()
      count3 = Especialidad.objects.all().count()
      count4 = Especialidad.objects.filter(estado="completado").count() 

      page = request.GET.get('page', 1)

      paginator = Paginator(especialidad, 5)
      try:
            especialidad = paginator.page(page)
      except PageNotAnInteger:
            especialidad = paginator.page(1)
      except EmptyPage:
            especialidad = paginator.page(paginator.num_pages)

      return render(request, "indexadmin.html", {'especialidad':especialidad, 'count':count, 'count2':count2, 'count3':count3, 'acceso':acceso})

    elif user.is_active: 
      especialidad  = Especialidad.objects.filter(encargado__usuario=user.id)
      template2 = "index3.html"
      return render(request, template2, { 'especialidad':especialidad })



def Ped_entregados(request):
    user = request.user
    if user.is_superuser:
      especialidad = Especialidad.objects.filter(estado="entregado").order_by('nombre')
      acceso = Especialidad.objects.filter(acceso=0)
      count = Especialidad.objects.filter(estado="pendiente").count()
      count2 = Especialidad.objects.filter(estado="entregado").count()
      count3 = Especialidad.objects.all().count()
      template = "indexadmin.html"
      page = request.GET.get('page', 1)

      paginator = Paginator(especialidad, 5)
      try:
            especialidad = paginator.page(page)
      except PageNotAnInteger:
            especialidad = paginator.page(1)
      except EmptyPage:
            especialidad = paginator.page(paginator.num_pages)

      return render(request, template, {'especialidad':especialidad, 'count':count, 'count2':count2, 'count3':count3, 'acceso':acceso})


def Esp_total(request):
      user = request.user
      if user.is_superuser:
         especialidad = Especialidad.objects.all().order_by('nombre')
         acceso = Especialidad.objects.filter(acceso=0)
         count = Especialidad.objects.filter(estado="pendiente").count()
         count2 = Especialidad.objects.filter(estado="entregado").count()
         count3 = Especialidad.objects.all().count()
         template = "indexadmin.html"
         page = request.GET.get('page', 1)

         paginator = Paginator(especialidad, 5)
         try:
                  especialidad = paginator.page(page)
         except PageNotAnInteger:
                  especialidad = paginator.page(1)
         except EmptyPage:
                  especialidad = paginator.page(paginator.num_pages)

         return render(request, template, {'especialidad':especialidad, 'count':count, 'count2':count2, 'count3':count3, 'acceso':acceso})


#LISTA ADMIN PENDIENTES
@cache_page(1000)
@login_required
def ListAll(request, id_especialidad):
  especialidad = Especialidad.objects.get(id=id_especialidad)
  if request.method == 'GET':
        pedido = Pedido.objects.filter(especialidad=especialidad).filter(estado='pendiente').order_by('-estado').order_by('articulo')
        template  = 'admindata.html'
        return render(request, template, {'pedido':pedido, 'especialidad':especialidad})

#LISTA ADMIN ENTREGADOS
@cache_page(1000)
@login_required
def ListAllEnt(request, id_especialidad):
  especialidad = Especialidad.objects.get(id=id_especialidad)
  if request.method == 'GET':
        pedido = Pedido.objects.filter(especialidad=especialidad).filter(estado='entregado').order_by('articulo')
        template  = 'admindata2.html'
        return render(request, template, {'pedido':pedido, 'especialidad':especialidad})



#LISTA ACTIVO
@cache_page(1000)
@login_required
def ListEspeci(request, id_especialidad):
      especialidad = Especialidad.objects.get(id=id_especialidad)
      pedido2 = Pedido.objects.filter(especialidad=especialidad).filter(estado='pendiente').order_by('-articulo')
      pedido3 = Pedido.objects.filter(especialidad=especialidad).filter(estado='entregado').order_by('-articulo')
      pedido = Pedido.objects.filter(especialidad=especialidad)
      if request.method == 'GET':
            form = EstadisticaForm(instance=especialidad)
      else:
            form = EstadisticaForm(request.POST, instance=especialidad)
            if form.is_valid():
                  form.save()
            return HttpResponseRedirect('/solicitar/lista_active/%s/' % id_especialidad)
      return render(request, 'index2.html', { 'form':form, 'pedido':pedido, 'pedido2':pedido2, 'pedido3':pedido3, 'especialidad':especialidad})
 


#BTN INGRESAR ACTIVO
@login_required
@cache_page(1000)
def Cant_ingresar(request, id_pedido, id_especialidad):
    especialidad = Especialidad.objects.get(id=id_especialidad)
    pedido = Pedido.objects.get(id=id_pedido)
    
    if request.method == 'GET':
      form = PedidoEditForm(instance=pedido)
    else:
      form = PedidoEditForm(request.POST, instance=pedido)
      if form.is_valid():
          form.save()
          pedido2 = Pedido.objects.filter(id=id_pedido).update(estado="pendiente", fecha_pedido=timezone.now())
          Especialidad.objects.filter(id=id_especialidad).update(estado="pendiente")
      return HttpResponseRedirect('/solicitar/lista_active/%s/' % id_especialidad)
    return render(request, 'form.html', {'form':form, 'pedido':pedido, 'especialidad':especialidad, 'pedido':pedido}) 


#BTN MODIFICAR ADMIN
@login_required
@cache_page(1000)
def Cant_update(request, id_pedido, id_especialidad):
    especialidad = Especialidad.objects.get(id=id_especialidad)
    pedido = Pedido.objects.get(id=id_pedido)
    if request.method == 'GET':
      form = PedAdminEditForm(instance=pedido)
    else:
      form = PedAdminEditForm(request.POST, instance=pedido)
      if form.is_valid():
          form.save()
          pedido.estado_update = 'modificado'
          pedido.save()
      return HttpResponseRedirect('/solicitar/lista_super/%s/' % id_especialidad)
    return render(request, 'form3.html', {'form':form, 'pedido':pedido, 'especialidad':especialidad})



from django.views.generic import ListView, DetailView
   

class PedidoDetailView(DetailView):
    model = Pedido
    def get_template_names(self):
        return render('index.html')


#BTN ENTREGADO
@login_required
def Entregar(request, id_especialidad):
    especialidad = Especialidad.objects.get(id=id_especialidad)
    pedido3 = Pedido.objects.filter(especialidad=especialidad).filter(estado='pendiente').update(fecha_entrega=timezone.now())
    for ped in Pedido.objects.filter(especialidad=especialidad).filter(estado='pendiente'):
      ped.estado = "entregado"
      ped.save()
      if ped.estado_update == "modificado":
            ped.articulo.stock -= ped.cantidad_update
      else: 
            ped.articulo.stock -= ped.cantidad
            ped.save()
    especialidad.estado = 'entregado'
    especialidad.save()
    return HttpResponseRedirect('/solicitar/reporte_pedidos_pdf/%s/' % id_especialidad)



#Ingresar cantidad de articulo extra
@login_required
def PedidoExtra(request, id_especialidad):
    especialidad = Especialidad.objects.get(id=id_especialidad)
    if request.method == 'GET':
      form = ExtraForm()
    else:
      form = ExtraForm(request.POST)
      if form.is_valid():
        esp = form.save(commit=False)
        esp.especialidad_ex = especialidad
        esp.save()
        form.save()
      return HttpResponseRedirect('/solicitar/home/')
    return render(request, 'form2.html', {'form':form, 'especialidad':especialidad})

#vista para admin y activo de extras
@login_required
def ExtraView(request):
      user = request.user
      if user.is_superuser:
        extra = Pedido_Extra.objects.filter(estado_ex='pendiente')
        return render(request, 'extra.html', {'extra':extra, 'user':user})
      else:
        extra = Pedido_Extra.objects.filter(especialidad_ex__encargado__usuario=user.id)
        return render(request, 'extra.html', {'extra':extra, 'user':user})

#admin modifica cantidad extra
@login_required
def Cant_upex(request, id_pedido_ex):
    extra = Pedido_Extra.objects.get(id=id_pedido_ex)
    if request.method == 'GET':
      form = ExtraForm(instance=extra)
    else:
      form = ExtraForm(request.POST, instance=extra)
      if form.is_valid():
          form.save()
          extra.save()
      return HttpResponseRedirect('/solicitar/pedidos-extra/')
    return render(request, 'form2.html', {'form':form, 'extra':extra})

#BTN ENTREGAR. ADMIN
@login_required
def Update_stockex(request, id_pedido_ex, cod_experto):
  if request.method == 'GET':
    pedido = Pedido_Extra.objects.get(id=id_pedido_ex)
    articulo = Articulo.objects.get(pk=cod_experto)
    articulo.stock -= pedido.cantidad_ex
    articulo.total_pedido += pedido.cantidad_ex
    articulo.save()
    pedido.estado_ex = 'entregado'
    pedido.fecha_entrega_ex = timezone.now()
    pedido.save()
    return HttpResponseRedirect('/solicitar/pedidos-extra/')

def Reset(request):
    estadis = Especialidad.objects.all().update(estadistica= 0, estado="")
    return HttpResponseRedirect('/solicitar/home/')

def Acces_close(request):
  acceso = Especialidad.objects.all().update(acceso=0)
  return HttpResponseRedirect('/solicitar/home/')

def Acces_open(request):
  acceso = Especialidad.objects.all().update(acceso=1)
  especialidad = Especialidad.objects.all().update(estado="completado")
  pedido = Pedido.objects.all().update(cantidad=0, estado="", fecha_pedido=None, fecha_entrega=None, estado_update="", cantidad_update=0)
  articulo = Articulo.objects.all().update(total_pedido=0)
  return HttpResponseRedirect('/solicitar/home/')

@cache_page(3000)
def VistaAsigna(request, id_especialidad):
  if request.method == 'GET':
    especialidad = Especialidad.objects.get(id=id_especialidad)
    articulo    = Articulo.objects.all()
    template     = 'asignar.html'
    return render(request, template, {'articulo':articulo, 'especialidad':especialidad})


def Asigna(request, id_especialidad, cod_experto):
  especialidad = Especialidad.objects.get(id=id_especialidad)
  articulo = Articulo.objects.get(pk=cod_experto)
  if request.method == 'GET':
    pedido = Pedido(articulo=articulo, especialidad=especialidad)
    pedido.save()
    return HttpResponseRedirect('/solicitar/ver_todo/%s/' % id_especialidad)

def VerTodo(request, id_especialidad):
  especialidad = Especialidad.objects.get(id=id_especialidad)
  if request.method == 'GET':
      pedido = Pedido.objects.filter(especialidad=especialidad).order_by('-estado').order_by('articulo')
      template  = 'addmod.html'
      return render(request, template, {'pedido':pedido, 'especialidad':especialidad})


@cache_page(3000)
def DeletePedido(request, id_pedido, id_especialidad, cod_experto):
  articulo      = Articulo.objects.get(pk=cod_experto)
  especialidad = Especialidad.objects.get(id=id_especialidad)
  pedido       = Pedido.objects.get(id=id_pedido)
  if request.method == 'POST':
    pedido.delete()
    return HttpResponseRedirect('/solicitar/ver_todo/%s/' % id_especialidad)
  return render(request, 'delete.html', {'especialidad':especialidad, 'articulo':articulo, 'pedido':pedido})


def IngresarExtra(request, id_especialidad, cod_experto):
  especialidad = Especialidad.objects.get(id=id_especialidad)
  articulo = Articulo.objects.get(pk=cod_experto)
  if request.method == 'GET':
      form = ExtraForm()
  else:
      form = ExtraForm(request.POST)
      if form.is_valid():
          ped = form.save()
          ped.id
          ped_ex = Pedido_Extra.objects.filter(id=ped.id).update(articulo_ex=articulo, especialidad_ex=especialidad)
      return HttpResponseRedirect('/solicitar/pedidos-extra/')
  return render(request, 'form2.html', {'form':form, 'especialidad':especialidad, 'articulo':articulo})





from reportlab.pdfgen import canvas
from io import BytesIO
from django.views.generic import View
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter,A4,A5, A3, A2, A1, A0
from reportlab.platypus import (BaseDocTemplate, Frame, Paragraph, NextPageTemplate, PageBreak, PageTemplate)
from reportlab.platypus.tables import Table, TableStyle
import datetime
mylist = []
today = datetime.date.today()
mylist.append(today)

#PARA ESPECIALIDADES
class ReportePedidosPDF(View): 

    def cabecera(self,pdf, id_especialidad):
        especialidad = Especialidad.objects.get(id=id_especialidad)
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 20)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(500, 1600, u"REPORTE CAE")
        pdf.setFont("Helvetica", 18)
        pdf.drawString(430, 1570, u"PEDIDO POR: " + str(especialidad.nombre))
        pdf.setFont("Helvetica", 16)
        pdf.drawString(500, 1530, u"ESTADISTICA: " + str(especialidad.estadistica))
        pdf.drawString(830, 1500, u"FECHA: " + str(datetime.date.today()))
        pdf.setFont("Helvetica", 16)
        pdf.drawString(150, 1500, u"POR: " + str(especialidad.encargado.nombre))
        


    def tabla(self,pdf,y, id_especialidad):
        especialidad = Especialidad.objects.get(id=id_especialidad)
        count = Pedido.objects.filter(especialidad=especialidad).filter(estado="entregado").count()
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Codigo Experto', 'Nombre Articulo', 'Cantidad', 'Cantidad MFD',  'Estado', 'Estado 2')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(pedido.articulo.cod_experto, pedido.articulo.nombre, pedido.cantidad, pedido.cantidad_update, pedido.estado, pedido.estado_update) for pedido in Pedido.objects.filter(especialidad=especialidad).filter(estado="entregado")]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[5 * cm, 10 * cm, 2 * cm , 3 * cm, 2 * cm, 2 * cm, 2 * cm])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        if count <=10:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 1250)
        elif count >10 and count <=30:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 900)
        elif count >30 and count <=50:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 600)
        elif count >50 and count <=70:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 400)
        elif count >70 and count <=90:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 100)
        elif count >90 and count <=110:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 50)
        elif count >110 and count <=130:
              #Definimos la coordenada donde se dibujará la tabla
              detalle_orden.drawOn(pdf, 250, 0)

    def get(self, request, id_especialidad, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        #Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer, pagesize = A2)
        #Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf, id_especialidad)
        y = 900
        self.tabla(pdf, y, id_especialidad)
        #Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
#FIN REPORTE

#PARA COMPRA. TOTAL PEDIDOS
class ReporteTotalPDF(View): 

    def cabecera(self,pdf ):
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 18)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(450, 1600, u"REPORTE ARTICULOS CAE")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(430, 1570, u"TOTAL DE CANTIDADES SOLICITADAS")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(700, 1530, u"FECHA: " + str(datetime.date.today()))
        pdf.setFont("Helvetica", 14)
        pdf.drawString(300, 1530, u"DE BODEGA: INSUMO")
   

    #PRIMERA TABLA INSUMO
    def tabla1(self,pdf,y):
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Codigo Experto', 'Nombre Articulo', 'Stock', 'Bodega', 'Total Pedido')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(art.cod_experto, art.nombre, art.stock, art.info_bodega, art.total_pedido) for art in Articulo.objects.filter(cod_experto__range=["AA-0001", "CP-0071"]).filter(info_bodega=1).filter(total_pedido__gt=0).order_by('cod_experto')]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 10 * cm, 2 * cm, 2 * cm, 2 * cm])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        #Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 600, 20)

#SEGUNDA TABLA INSUMO
    def tabla2(self,pdf,y):
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Codigo Experto', 'Nombre Articulo', 'Stock', 'Bodega', 'Total Pedido')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(art.cod_experto, art.nombre, art.stock, art.info_bodega, art.total_pedido) for art in Articulo.objects.filter(cod_experto__range=["CP-0071", "VV-0122"]).filter(info_bodega=1).filter(total_pedido__gt=0).order_by('cod_experto')]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 10 * cm, 2 * cm, 2 * cm, 2 * cm])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        #Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 50, 20)
    
    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        #Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer, pagesize = A2)
        #Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        y = 900
        self.tabla1(pdf, y)
        self.tabla2(pdf, y)
        #Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
#FIN REPORTE

#PARA COMPRA. TOTAL FARMACIA
class ReporteTotalFarmacia(View): 

    def cabecera(self,pdf ):
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 18)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(450, 1600, u"REPORTE ARTICULOS CAE")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(430, 1570, u"TOTAL DE CANTIDADES SOLICITADAS")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(700, 1530, u"FECHA: " + str(datetime.date.today()))
        pdf.setFont("Helvetica", 14)
        pdf.drawString(300, 1530, u"DE BODEGA: FARMACIA")
   
    def tabla(self,pdf,y):
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Codigo Experto', 'Nombre Articulo', 'Stock', 'Bodega', 'Total Pedido')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(art.cod_experto, art.nombre, art.stock, art.info_bodega, art.total_pedido) for art in Articulo.objects.filter(info_bodega=2).filter(total_pedido__gt=0).order_by('cod_experto')]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 10 * cm, 2 * cm, 2 * cm, 2 * cm])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        #Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 300, 1200)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        #Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer, pagesize = A2)
        #Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        y = 900
        self.tabla(pdf, y)
        #Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
#FIN REPORTE

#PARA COMPRA. TOTAL ECONOMATO
class ReporteTotalEcono(View): 

    def cabecera(self,pdf ):
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 18)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(450, 1600, u"REPORTE ARTICULOS CAE")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(430, 1570, u"TOTAL DE CANTIDADES SOLICITADAS")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(700, 1520, u"FECHA: " + str(datetime.date.today()))
        pdf.setFont("Helvetica", 14)
        pdf.drawString(300, 1520, u"DE BODEGA: ECONOMATO")
   
    def tabla1(self,pdf,y):
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Codigo Experto', 'Nombre Articulo', 'Stock', 'Bodega', 'Total Pedido')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(art.cod_experto, art.nombre, art.stock, art.info_bodega, art.total_pedido) for art in Articulo.objects.filter(info_bodega=3).filter(cod_experto__range=["ASE-00024", "OFI-0047"]).filter(total_pedido__gt=0).order_by('cod_experto')]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 10 * cm, 2 * cm, 2 * cm, 2 * cm])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        #Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 50, 700)

    def tabla2(self,pdf,y):
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Codigo Experto', 'Nombre Articulo', 'Stock', 'Bodega', 'Total Pedido')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(art.cod_experto, art.nombre, art.stock, art.info_bodega, art.total_pedido) for art in Articulo.objects.filter(info_bodega=3).filter(cod_experto__range=["OFI-0048", "OFI-0579"]).filter(total_pedido__gt=0).order_by('cod_experto')]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[3 * cm, 10 * cm, 2 * cm, 2 * cm, 2 * cm])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        #Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 600, 700)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        #Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer, pagesize = A2)
        #Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        y = 900
        self.tabla1(pdf, y)
        self.tabla2(pdf, y)
        #Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
#FIN REPORTE

#REPORTE PEDIDOS EXTRA
class ReportePedidoExtra(View): 

    def cabecera(self,pdf ):
        #Establecemos el tamaño de letra en 16 y el tipo de letra Helvetica
        pdf.setFont("Helvetica", 18)
        #Dibujamos una cadena en la ubicación X,Y especificada
        pdf.drawString(450, 1600, u"REPORTE PEDIDOS EXTRAS CAE")
        pdf.setFont("Helvetica", 16)
        pdf.drawString(470, 1570, u"REPORTE SEMANAL")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(700, 1530, u"FECHA: " + str(datetime.date.today()))
   
    def tabla(self,pdf,y):
        #Creamos una tupla de encabezados para neustra tabla
        encabezados = ('Servicio', 'Codigo Experto', 'Nombre Articulo','Cantidad', 'Stock', 'Fecha entrega')
        #Creamos una lista de tuplas que van a contener a las personas
        detalles = [(pedex.especialidad_ex, pedex.articulo_ex.cod_experto, pedex.articulo_ex.nombre, pedex.cantidad_ex, pedex.articulo_ex.stock, pedex.fecha_entrega_ex) for pedex in Pedido_Extra.objects.filter(estado_ex='entregado').order_by('fecha_pedido_ex')]
        #Establecemos el tamaño de cada una de las columnas de la tabla
        detalle_orden = Table([encabezados] + detalles, colWidths=[5 * cm, 5 * cm, 10 * cm, 2 * cm, 2 * cm,  5 * cm ])
        #Aplicamos estilos a las celdas de la tabla
        detalle_orden.setStyle(TableStyle(
            [
                #La primera fila(encabezados) va a estar centrada
                ('ALIGN',(0,0),(3,0),'CENTER'),
                #Los bordes de todas las celdas serán de color negro y con un grosor de 1
                ('GRID', (0, 0), (-1, -1), 1, colors.black), 
                #El tamaño de las letras de cada una de las celdas será de 10
                ('FONTSIZE', (0, 0), (-1, -1), 10),
            ]
        ))
        #Establecemos el tamaño de la hoja que ocupará la tabla 
        detalle_orden.wrapOn(pdf, 1000, 1000)
        #Definimos la coordenada donde se dibujará la tabla
        detalle_orden.drawOn(pdf, 100, 700)

    def get(self, request, *args, **kwargs):
        #Indicamos el tipo de contenido a devolver, en este caso un pdf
        response = HttpResponse(content_type='application/pdf')
        #La clase io.BytesIO permite tratar un array de bytes como un fichero binario, se utiliza como almacenamiento temporal
        buffer = BytesIO()
        #Canvas nos permite hacer el reporte con coordenadas X y Y
        pdf = canvas.Canvas(buffer, pagesize = A2)
        #Llamo al método cabecera donde están definidos los datos que aparecen en la cabecera del reporte.
        self.cabecera(pdf)
        y = 900
        self.tabla(pdf, y)
        #Con show page hacemos un corte de página para pasar a la siguiente
        pdf.showPage()
        pdf.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
#FIN REPORTE


from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
 
class CaseInsensitiveModelBackend(ModelBackend):
  def authenticate(self, username=None, password=None):
    try:
      user = User.objects.get(username__iexact=username)
      if user.check_password(password):
        return user
      return None
    except User.DoesNotExist:
      return None