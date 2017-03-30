from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url
from .import views
from django.contrib.auth.views import login_required


from Pedidoapp.views import home, Cant_ingresar, ListAll, ListEspeci, Cant_update, Update_stock, PedidoExtra, ExtraView, Cant_upex, Update_stockex, Completar, ReportePedidosPDF, ReporteTotalPDF, ReporteTotalFarmacia, ReporteTotalEcono, Reset, Acces_open, Acces_close, VistaAsigna, Asigna, DeletePedido

admin.autodiscover()

urlpatterns = [

url(r'^home/$', login_required(home), name="home"),

url(r'^lista_super/(?P<id_especialidad>\d+)/$', login_required(ListAll), name='lita_todo'),
url(r'^lista_active/(?P<id_especialidad>\d+)/$', login_required(ListEspeci), name='lita_active'),
url(r'^ingresar/(?P<id_pedido>\d+)/(?P<id_especialidad>\d+)/$', Cant_ingresar, name="cant_ingresar"),
url(r'^modificar/(?P<id_pedido>\d+)/(?P<id_especialidad>\d+)/$', Cant_update, name="cant_update"),
url(r'^entregar/(?P<id_pedido>\d+)/(?P<id_especialidad>\d+)/(?P<cod_experto>[^/]+)/$', Update_stock, name="entregado"),
url(r'^pedido-extra/(?P<id_especialidad>\d+)/$', PedidoExtra , name='pedido_extra'),
url(r'^pedidos-extra/$', ExtraView , name='ped_ex'),
url(r'^modificar/(?P<id_pedido_ex>\d+)/$', Cant_upex, name="cant_extra"),
url(r'^entregar/(?P<id_pedido_ex>\d+)/(?P<cod_experto>[^/]+)/$', Update_stockex, name="entregado_ex"),
url(r'^completar/(?P<id_especialidad>\d+)/$', Completar, name='completar'),
url(r'^reset-estadistica/$', Reset , name='reset'),
url(r'^reporte_pedidos_pdf/(?P<id_especialidad>\d+)/$', login_required(ReportePedidosPDF.as_view()), name="reporte_pedidos_pdf"),
url(r'^reporte_insumo_pdf/$', login_required(ReporteTotalPDF.as_view()), name="reporte_insumo_pdf"),
url(r'^reporte_farmacia_pdf/$', login_required(ReporteTotalFarmacia.as_view()), name="reporte_farma_pdf"),
url(r'^reporte_economato_pdf/$', login_required(ReporteTotalEcono.as_view()), name="reporte_econo_pdf"),
url(r'^reset-estadis/$', login_required(Reset), name="reset"),
url(r'^acces-open/$', login_required(Acces_open), name="open"),
url(r'^acces-close/$', login_required(Acces_close), name="close"),
url(r'^asignar-nuevo/(?P<id_especialidad>\d+)/$', login_required(VistaAsigna), name='vista_asigna'),
url(r'^btn-asigna/(?P<id_especialidad>\d+)/(?P<cod_experto>[^/]+)/$', Asigna, name="asignar"),
url(r'^delete-pedido/(?P<id_pedido>\d+)/(?P<id_especialidad>\d+)/(?P<cod_experto>[^/]+)/$', DeletePedido, name="confirm_delete_pedido"),



]   + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)      
