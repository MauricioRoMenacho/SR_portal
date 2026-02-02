from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .view import views, Entregautiles

urlpatterns = [

    # ═════════════════════════════════════════════════════════════════════
    # INICIO / GENERALES
    # ═════════════════════════════════════════════════════════════════════
    path('', views.inicio, name='inicio'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),

    # ═════════════════════════════════════════════════════════════════════
    # ALMACENES
    # ═════════════════════════════════════════════════════════════════════
    path('almacenes/', views.almacenes, name='almacenes'),

    # ═════════════════════════════════════════════════════════════════════
    # INVENTARIO GENERAL
    # ═════════════════════════════════════════════════════════════════════
    path('almacenes/inventario/', views.InventrioAG, name='InventarioAG'),
    path('almacenes/agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('almacenes/crear-unidad/', views.crear_unidad, name='crear_unidad'),
    path('almacenes/importar-excel/', views.importar_excel, name='importar_excel'),
    path('almacenes/descargar-plantilla/', views.descargar_plantilla, name='descargar_plantilla'),
    path('api/ultimo-producto/', views.api_ultimo_producto, name='api_ultimo_producto'),

    # ═════════════════════════════════════════════════════════════════════
    # PEDIDOS DE COMPRA
    # ═════════════════════════════════════════════════════════════════════
    path('pedidos-compra/', views.PedidosCompra, name='PedidosCompra'),
    path('pedidos-compra/crear/', views.CrearPedidoCompra, name='CrearPedidoCompra'),
    path('pedidos-compra/<int:id_pedido>/', views.DetallePedido, name='DetallePedido'),
    path('pedidos-compra/<int:id_pedido>/editar/', views.EditarPedido, name='EditarPedido'),
    path('pedidos-compra/<int:id_pedido>/eliminar/', views.EliminarPedido, name='EliminarPedido'),
    path('pedidos-compra/<int:id_pedido>/generar-pdf/', views.GenerarPDFPedido, name='GenerarPDFPedido'),

    # Items del pedido
    path('pedidos-compra/<int:id_pedido>/items/agregar/', views.AgregarItemPedido, name='AgregarItemPedido'),
    path('pedidos-compra/items/<int:item_id>/', views.ObtenerItemPedido, name='ObtenerItemPedido'),
    path('pedidos-compra/items/<int:item_id>/editar/', views.EditarItemPedido, name='EditarItemPedido'),
    path('pedidos-compra/items/<int:item_id>/eliminar/', views.EliminarItemPedido, name='EliminarItemPedido'),

    # Cotizaciones
    path('pedidos-compra/<int:id_pedido>/cotizaciones/', views.CotizacionesPedido, name='CotizacionesPedido'),
    path('pedidos-compra/<int:id_pedido>/cotizaciones/agregar/', views.AgregarCotizacion, name='AgregarCotizacion'),
    path('cotizaciones/<int:id_cotizacion>/seleccionar/', views.SeleccionarCotizacion, name='SeleccionarCotizacion'),
    path('documento/<int:cotizacion_id>/', views.ver_documento, name='ver_documento'),

    # Entrega de pedidos
    path('pedidos-compra/<int:id_pedido>/marcar-entregado/', views.MarcarEntregado, name='MarcarEntregado'),

    # ═════════════════════════════════════════════════════════════════════
    # ENTREGA DE ÚTILES ESCOLARES - PRINCIPAL
    # ═════════════════════════════════════════════════════════════════════
    path('inventario-utiles/', Entregautiles.inventario_utiles, name='inventario_utiles'),
    path('entrega-utiles/', Entregautiles.SalonesList.as_view(), name='entrega_utiles'),

    # ═════════════════════════════════════════════════════════════════════
    # SALONES - CRUD
    # ═════════════════════════════════════════════════════════════════════
    path('entrega-utiles/salones/crear/', Entregautiles.crear_salon, name='crear_salon'),
    path('entrega-utiles/salones/<int:pk>/', Entregautiles.detalle_salon, name='detalle_salon'),
    path('entrega-utiles/salones/<int:pk>/editar/', Entregautiles.editar_salon, name='editar_salon'),
    path('entrega-utiles/salones/<int:pk>/eliminar/', Entregautiles.eliminar_salon, name='eliminar_salon'),
    path('entrega-utiles/salones/<int:pk>/importar-excel/', Entregautiles.importar_excel_alumnos, name='importar_excel_alumnos'),

    # ═════════════════════════════════════════════════════════════════════
    # GESTIÓN DE ÚTILES ESCOLARES
    # ═════════════════════════════════════════════════════════════════════
    path('entrega-utiles/salones/<int:salon_id>/utiles/', Entregautiles.lista_utiles, name='lista_utiles'),
    path('entrega-utiles/utiles/<int:util_id>/eliminar/', Entregautiles.eliminar_util, name='eliminar_util'),

    # ═════════════════════════════════════════════════════════════════════
    # GESTIÓN DE ENTREGAS POR ALUMNO
    # ═════════════════════════════════════════════════════════════════════
    path('entrega-utiles/alumnos/<int:alumno_id>/', Entregautiles.detalle_alumno, name='detalle_alumno'),
    path('entrega-utiles/alumnos/<int:alumno_id>/editar-entregas/', Entregautiles.editar_entregas_alumno, name='editar_entregas_alumno'),

    # ═════════════════════════════════════════════════════════════════════
    # API ENDPOINTS - ENTREGA DE ÚTILES
    # ═════════════════════════════════════════════════════════════════════
    path('api/salones/<int:salon_id>/alumnos/', Entregautiles.api_alumnos_salon, name='api_alumnos_salon'),
    path('api/alumnos/<int:alumno_id>/eliminar/', Entregautiles.api_eliminar_alumno, name='api_eliminar_alumno'),
    path('api/alumnos/<int:alumno_id>/estado/', Entregautiles.api_estado_alumno, name='api_estado_alumno'),
    path('api/entregas/<int:entrega_id>/toggle/', Entregautiles.api_toggle_entrega_util, name='api_toggle_entrega_util'),
]

# ═════════════════════════════════════════════════════════════════════
# ARCHIVOS MEDIA (DESARROLLO)
# ═════════════════════════════════════════════════════════════════════
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)