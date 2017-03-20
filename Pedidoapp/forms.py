from django import forms
from django.forms import ModelForm
from .models import Pedido, Especialidad, Articulo, Pedido_Extra


class PedidoEditForm(forms.ModelForm):
    cantidad       = forms.IntegerField(label='Cantidad:', widget=forms.TextInput(attrs={'size':'10'}))

    class Meta:
        model = Pedido


        fields = [

        'cantidad',

        ]  

class EstadisticaForm(forms.ModelForm):
    estadistica    = forms.IntegerField(label='Estadistica Mensual:', widget=forms.TextInput(attrs={'placeholder':'Ingrese numero pacientes'}))  
    
    class Meta:
        model = Especialidad

        fields = [

        'estadistica',

        ]

class ExtraForm(forms.ModelForm):
    cantidad_ex       = forms.IntegerField(label='Cantidad:', widget=forms.TextInput(attrs={'size':'10'}))
    

    class Meta:
        model = Pedido_Extra


        fields = [

        'articulo_ex',
        'cantidad_ex',
        

        ]  
        labels = {

        'articulo_ex': 'Articulo',
        
        }
        widget = {

        'articulo_ex': forms.Select(attrs={'class':'form-control'}),

        }

