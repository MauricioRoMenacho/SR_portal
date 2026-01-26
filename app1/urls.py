from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('almacenes/', views.almacenes, name='almacenes'),
    path('almacenes/InventarioAG/', views.InventrioAG, name='InventarioAG'),
    path('almacenes/agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('almacenes/crear-unidad/', views.crear_unidad, name='crear_unidad'),
    path('importar-excel/', views.importar_excel, name='importar_excel'),
    path('descargar-plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),
]