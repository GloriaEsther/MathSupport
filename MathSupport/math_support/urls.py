from django.urls import path
#from .views import resolver_ecuacion, reconocer_ecuacion,index  # Importa las vistas
from . import views
urlpatterns = [
    #path('', views.index, name='index'),#rutas para que funcionen con la raiz
    path('bienvenida',views.bienvenida,name='bienvenida'),#'nombre',nombredelavista,name='nombredelavista'
    path('login',views.inicio_sesion,name='login'),
    path('registro',views.registro,name='registro'),
    path('home',views.home,name='home'),
   # path('resolver/', views.resolver_ecuacion, name='resolver_ecuacion'),por ahora no lqas voy a ocupar
   # path('reconocer/', views.reconocer_ecuacion, name='reconocer_ecuacion'),
]
