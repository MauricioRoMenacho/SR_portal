from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include  
from .view import views, Entregautiles

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
    path('crear-pedido-compra/', views.CrearPedidoCompra, name='CrearPedidoCompra'),
    path('generar-pdf-pedido/', views.GenerarPDFPedido, name='GenerarPDFPedido'),
    path('detalle-pedido-compra/<int:id_pedido>/', views.DetallePedido, name='DetallePedido'),
    path('editar-pedido-compra/<int:id_pedido>/', views.EditarPedido, name='EditarPedido'),
    path('eliminar-pedido-compra/<int:id_pedido>/', views.EliminarPedido, name='EliminarPedido'),
    path('api/ultimo-producto/', views.api_ultimo_producto, name='api_ultimo_producto'),
    
    # Items del pedido
    path('pedidos-compra/<int:id_pedido>/agregar-item/', views.AgregarItemPedido, name='AgregarItemPedido'),
    path('pedidos-compra/<int:id_pedido>/editar-item/', views.EditarItemPedido, name='EditarItemPedido'),
    path('pedidos-compra/item/<int:item_id>/obtener/', views.ObtenerItemPedido, name='ObtenerItemPedido'),
    path('pedidos-compra/item/<int:item_id>/eliminar/', views.EliminarItemPedido, name='EliminarItemPedido'),
    
    # Cotizaciones
    path('cotizaciones-pedido/<int:id_pedido>/', views.CotizacionesPedido, name='CotizacionesPedido'),
    path('agregar-cotizacion/<int:id_pedido>/', views.AgregarCotizacion, name='AgregarCotizacion'),
    path('seleccionar-cotizacion/<int:id_cotizacion>/', views.SeleccionarCotizacion, name='SeleccionarCotizacion'),
    
    # Vista para visualizar documentos
    path('documento/<int:cotizacion_id>/', views.ver_documento, name='ver_documento'),

    # Entrega
    path('marcar-entregado/<int:id_pedido>/', views.MarcarEntregado, name='MarcarEntregado'),

    # Otras rutas
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),

    # ── Entrega de útiles ──
    path('entrega-utiles/',                                 Entregautiles.SalonesList.as_view(),    name='entrega_utiles'),
    path('crear-salon/',                                    Entregautiles.crear_salon,              name='crear_salon'),
    path('editar-salon/<int:pk>/',                          Entregautiles.editar_salon,             name='editar_salon'),
    path('salones/eliminar/<int:pk>/',                      Entregautiles.eliminar_salon,           name='eliminar_salon'),
    path('salon/<int:pk>/',                                 Entregautiles.detalle_salon,            name='detalle_salon'),
    path('salon/<int:pk>/importar-excel/',                  Entregautiles.importar_excel_alumnos,   name='importar_excel_alumnos'),

    # ── API alumnos ──
    path('api/salones/<int:salon_id>/alumnos/',             Entregautiles.api_alumnos_salon,        name='api_alumnos_salon'),
    path('api/alumnos/<int:alumno_id>/toggle-entrega/',     Entregautiles.api_toggle_entrega,       name='api_toggle_entrega'),
    path('api/alumnos/<int:alumno_id>/eliminar/',           Entregautiles.api_eliminar_alumno,      name='api_eliminar_alumno'),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)