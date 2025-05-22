from django.urls import path
#from .views import resolver_ecuacion, reconocer_ecuacion,index  # Importa las vistas
from . import views
urlpatterns = [
    #path('', views.index, name='index'),#rutas para que funcionen con la raiz
    path('bienvenida',views.bienvenida,name='bienvenida'),#'nombre',nombredelavista,name='nombredelavista'
    path('login',views.inicio_sesion,name='login'),
    path('registro',views.registro,name='registro'),
    path('home',views.home,name='home'),
    path('ocr/', views.ocr_view, name='ocr_view'),
    path('resolver_ecuacion/', views.resolver_ecuacion, name='resolver_ecuacion'),#lo vas a ocupar :b
    #esto es prueba
    path('paso/', views.ver_paso,name="pasos"),
    path('paso/siguiente/', views.siguiente_paso),
    path('paso/anterior/', views.paso_anterior),
    path('grafica/', views.generar_grafica),
    path('maximizar/',views.maximizar,name="maximizar"),
    path('ver_paso/',views.ver_paso,name="ver_paso"),
    #path('agregar/', views.agregar_ecuacion, name='agregar_ecuacion'),
    #path('ver_ecuaciones/', views.ver_ecuaciones, name='ver_ecuaciones'),
   # path('reconocer/', views.reconocer_ecuacion, name='reconocer_ecuacion'),
]
