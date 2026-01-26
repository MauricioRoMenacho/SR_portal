from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('almacenes/', views.almacenes, name='almacenes'),
    path('almacenes/InventarioAG/', views.InventrioAG, name='InventarioAG'),
    path('almacenes/agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('almacenes/crear-unidad/', views.crear_unidad, name='crear_unidad'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),
]