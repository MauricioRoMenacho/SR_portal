from django.db import models

# MODELO DE UNIDADES - VERSIÓN SIMPLE
class Unidad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'app1_unidad'
        verbose_name = 'Unidad'
        verbose_name_plural = 'Unidades'
        ordering = ['nombre']


class ProductoAlmacen(models.Model):

    UBICACION_CHOICES = [
        ('AG', 'Almacén General'),
        ('AD', 'Almacén de Deporte'),
        ('IU', 'Almacén de Útiles'),  
    ]

    ESTADO_CHOICES = [
        ('DISP', 'Disponible'),
        ('AGOT', 'Agotado'),
        ('BAJO', 'Stock Bajo'),
    ]

    id_producto = models.AutoField(primary_key=True)
    codigo_almacen = models.CharField(max_length=2, editable=False)
    codigo_producto = models.CharField(max_length=50, unique=True, db_index=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255, blank=True)
    ubicacion_almacen = models.CharField(max_length=2, choices=UBICACION_CHOICES)
    estante = models.CharField(max_length=50, blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=0)
    unidad = models.ForeignKey(
        Unidad,
        on_delete=models.PROTECT,
        related_name='productos'
    )
    estado = models.CharField(max_length=4, choices=ESTADO_CHOICES, default='DISP')
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    observaciones = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.codigo_almacen:
            codigos = {
                'AG': '01',
                'AD': '02',
                'IU': '03',
            }
            self.codigo_almacen = codigos.get(self.ubicacion_almacen, '00')
        
        if not self.codigo_producto:
            ultimo_producto = ProductoAlmacen.objects.filter(
                ubicacion_almacen=self.ubicacion_almacen
            ).order_by('-id_producto').first()
            
            if ultimo_producto and ultimo_producto.codigo_producto:
                try:
                    ultimo_numero = int(ultimo_producto.codigo_producto.split('-')[1])
                    nuevo_numero = ultimo_numero + 1
                except:
                    nuevo_numero = 1
            else:
                nuevo_numero = 1
            
            self.codigo_producto = f"{self.codigo_almacen}-{nuevo_numero:04d}"
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo_producto} - {self.nombre} ({self.cantidad} {self.unidad.abreviatura if self.unidad.abreviatura else self.unidad.nombre})"
    
    class Meta:
        db_table = 'app1_productoalmacen'
        verbose_name = 'Producto de Almacén'
        verbose_name_plural = 'Productos de Almacén'


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('PRESTAMO', 'Préstamo'),
        ('DEVOLUCION', 'Devolución'),
        ('AJUSTE', 'Ajuste'),
    ]

    producto = models.ForeignKey(ProductoAlmacen, on_delete=models.CASCADE, related_name='movimientos')
    tipo_movimiento = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    cantidad_anterior = models.PositiveIntegerField()
    cantidad_nueva = models.PositiveIntegerField()
    estante_anterior = models.CharField(max_length=50, blank=True, null=True)
    estante_nuevo = models.CharField(max_length=50, blank=True, null=True)
    fecha_movimiento = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    usuario = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.nombre} ({self.cantidad}) - {self.fecha_movimiento}"

    class Meta:
        db_table = 'app1_movimientoinventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento']


class PedidoCompra(models.Model):
    ESTADO_CHOICES = [
        ('PEND', 'Pendiente'),
        ('COMP', 'Completado'),
        ('ENTR', 'Entregado'),
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    archivo = models.FileField(upload_to='pedidos_compra/', null=True, blank=True)  # Ahora opcional
    estado = models.CharField(max_length=4, choices=ESTADO_CHOICES, default='PEND')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    # Documento de entrega (cuando estado = ENTR)
    documento_entrega = models.FileField(upload_to='documentos_entrega/', null=True, blank=True)
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"PC-{self.id_pedido:04d} - {self.nombre}"
    
    def total_cotizaciones(self):
        return self.cotizaciones.count()
    
    def cotizacion_seleccionada(self):
        return self.cotizaciones.filter(estado='SELEC').first()
    
    def total_items(self):
        return self.items.count()
    
    def total_general(self):
        """Calcula el total general del pedido basado en los items"""
        total = 0
        for item in self.items.all():
            total += item.subtotal()
        return total
    
    class Meta:
        db_table = 'pedidos_compra'
        verbose_name = 'Pedido de Compra'
        verbose_name_plural = 'Pedidos de Compra'
        ordering = ['-fecha_creacion']


class ItemPedido(models.Model):
    """Items/Productos dentro de un pedido de compra"""
    id_item = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(ProductoAlmacen, on_delete=models.PROTECT, related_name='items_pedido')
    cantidad_solicitada = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observaciones = models.TextField(blank=True, null=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    def subtotal(self):
        return self.cantidad_solicitada * self.precio_unitario
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad_solicitada}"
    
    class Meta:
        db_table = 'items_pedido'
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
        ordering = ['fecha_agregado']


class Cotizacion(models.Model):
    ESTADO_CHOICES = [
        ('PEND', 'Pendiente'),
        ('SELEC', 'Seleccionada'),
        ('RECH', 'Rechazada'),
    ]
    
    id_cotizacion = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name='cotizaciones')
    proveedor = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True, null=True)
    documento = models.FileField(upload_to='cotizaciones/', null=False, blank=False)
    estado = models.CharField(max_length=5, choices=ESTADO_CHOICES, default='PEND')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"COT-{self.id_cotizacion:04d} - {self.proveedor} - ${self.monto}"
    
    class Meta:
        db_table = 'cotizaciones'
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'
        ordering = ['-fecha_creacion']