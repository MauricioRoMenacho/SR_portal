from django.contrib import admin
from .models import ProductoAlmacen, MovimientoInventario, Unidad

# UNIDADES - SIN RESTRICCIONES POR AHORA
@admin.register(Unidad)
class UnidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'abreviatura', 'activo', 'fecha_creacion')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre', 'abreviatura')
    ordering = ('nombre',)
    
    # TODO: Aplicar restricciones de permisos cuando termines el template
    # def has_module_permission(self, request):
    #     return request.user.is_superuser or request.user.is_staff
    # def has_add_permission(self, request):
    #     return request.user.is_superuser
    # def has_change_permission(self, request, obj=None):
    #     return request.user.is_superuser
    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser


@admin.register(ProductoAlmacen)
class ProductoAlmacenAdmin(admin.ModelAdmin):
    list_display = ('codigo_producto', 'nombre', 'ubicacion_almacen', 'cantidad', 'unidad', 'estado', 'estante')
    list_filter = ('ubicacion_almacen', 'estado', 'unidad')
    search_fields = ('codigo_producto', 'nombre', 'descripcion')
    readonly_fields = ('codigo_almacen', 'fecha_ingreso', 'ultima_actualizacion')
    ordering = ('-fecha_ingreso',)


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'tipo_movimiento', 'cantidad', 'cantidad_anterior', 'cantidad_nueva', 'fecha_movimiento', 'usuario')
    list_filter = ('tipo_movimiento', 'fecha_movimiento')
    search_fields = ('producto__nombre', 'producto__codigo_producto', 'observacion')
    readonly_fields = ('fecha_movimiento',)
    ordering = ('-fecha_movimiento',)
    
    # TODO: Bloquear edición cuando termines el desarrollo
    # def has_add_permission(self, request):
    #     return False
    # def has_change_permission(self, request, obj=None):
    #     return False
    # def has_delete_permission(self, request, obj=None):
    #     return request.user.is_superuser