from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include  
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('almacenes/', views.almacenes, name='almacenes'),

    # Inventario general
    path('almacenes/InventarioAG/', views.InventrioAG, name='InventarioAG'),
    path('almacenes/agregar_producto/', views.agregar_producto, name='agregar_producto'),
    path('almacenes/crear-unidad/', views.crear_unidad, name='crear_unidad'),
    path('importar-excel/', views.importar_excel, name='importar_excel'),
    path('descargar-plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
    
    # Pedido de compra
    path('pedidos-compra/', views.PedidosCompra, name='PedidosCompra'),
    path('crear-pedido-compra/', views.CrearPedidoCompra, name='CrearPedidoCompra'),  # NUEVO
    path('generar-pdf-pedido/', views.GenerarPDFPedido, name='GenerarPDFPedido'),      # NUEVO
    path('detalle-pedido-compra/<int:id_pedido>/', views.DetallePedido, name='DetallePedido'),
    path('editar-pedido-compra/<int:id_pedido>/', views.EditarPedido, name='EditarPedido'),
    path('eliminar-pedido-compra/<int:id_pedido>/', views.EliminarPedido, name='EliminarPedido'),
    path('api/ultimo-producto/', views.api_ultimo_producto, name='api_ultimo_producto'),
    # Cotizaciones
    path('cotizaciones-pedido/<int:id_pedido>/', views.CotizacionesPedido, name='CotizacionesPedido'),
    path('agregar-cotizacion/<int:id_pedido>/', views.AgregarCotizacion, name='AgregarCotizacion'),
    path('seleccionar-cotizacion/<int:id_cotizacion>/', views.SeleccionarCotizacion, name='SeleccionarCotizacion'),
    
    # Vista para visualizar documentos (PDF, DOC, DOCX)
    path('documento/<int:cotizacion_id>/', views.ver_documento, name='ver_documento'),

    # Entrega
    path('marcar-entregado/<int:id_pedido>/', views.MarcarEntregado, name='MarcarEntregado'),

    # Otras rutas
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)