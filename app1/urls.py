from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('almacenes/', views.almacenes, name='almacenes'),

    #Inventario general
    path('almacenes/InventarioAG/', views.InventrioAG, name='InventarioAG'),
    path('almacenes/agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('almacenes/crear-unidad/', views.crear_unidad, name='crear_unidad'),
    path('importar-excel/', views.importar_excel, name='importar_excel'),
    path('descargar-plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
    #Pedido de compra
    path('pedidos-compra/', views.PedidosCompra, name='PedidosCompra'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),
]