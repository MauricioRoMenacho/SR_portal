from django.db import models
from django.utils import timezone

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
    archivo = models.FileField(upload_to='pedidos_compra/', null=True, blank=True)
    estado = models.CharField(max_length=4, choices=ESTADO_CHOICES, default='PEND')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    
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


class Salon(models.Model):
    TURNO_CHOICES = [
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
    ]

    GRADO_CHOICES = [
        (1, '1° Grado'),
        (2, '2° Grado'),
        (3, '3° Grado'),
        (4, '4° Grado'),
        (5, '5° Grado'),
        (6, '6° Grado'),
    ]

    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=10, unique=True)
    profesora = models.CharField(max_length=150)
    grado = models.IntegerField(choices=GRADO_CHOICES)
    turno = models.CharField(max_length=10, choices=TURNO_CHOICES, default='Mañana')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Salón'
        verbose_name_plural = 'Salones'

    def __str__(self):
        return self.nombre

    @property
    def profesora_iniciales(self):
        partes = self.profesora.split()
        return ''.join([p[0].upper() for p in partes if p])[:2]

    @property
    def total_alumnos(self):
        return self.alumnos.count()

    @property
    def total_entregados(self):
        completos = 0
        for alumno in self.alumnos.all():
            if alumno.estado_entrega == 'completo':
                completos += 1
        return completos

    @property
    def total_parciales(self):
        parciales = 0
        for alumno in self.alumnos.all():
            if alumno.estado_entrega == 'parcial':
                parciales += 1
        return parciales

    @property
    def total_pendientes(self):
        pendientes = 0
        for alumno in self.alumnos.all():
            if alumno.estado_entrega == 'no_entrego':
                pendientes += 1
        return pendientes


class Alumno(models.Model):
    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ]

    salon = models.ForeignKey(
        'Salon',
        on_delete=models.CASCADE,
        related_name='alumnos'
    )
    nombre = models.CharField(max_length=150)
    dni = models.CharField(max_length=10, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, blank=True, default='')
    email = models.EmailField(blank=True, null=True)

    entrega_completada = models.BooleanField(default=False)
    fecha_entrega = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Alumno'
        verbose_name_plural = 'Alumnos'

    def __str__(self):
        return f"{self.nombre} — {self.salon.nombre}"

    @property
    def estado_entrega(self):
        """
        Estados posibles:
        - sin_lista: No tiene útiles asignados
        - no_entrego: Tiene útiles pero cantidad_entregada total es 0
        - parcial: Tiene algo entregado pero no todo
        - completo: Todas las cantidades entregadas igualan a las pedidas
        """
        entregas = self.entregas.all().select_related('util')
        
        if not entregas.exists():
            return 'sin_lista'

        total_pedido = 0
        total_entregado = 0

        for entrega in entregas:
            total_pedido += entrega.util.cantidad
            total_entregado += entrega.cantidad_entregada

        if total_entregado == 0:
            return 'no_entrego'
        elif total_entregado < total_pedido:
            return 'parcial'
        return 'completo'

    @property
    def progreso_entrega(self):
        """
        Retorna progreso como 'X/Y' donde:
        X = suma de todas las cantidades entregadas
        Y = suma de todas las cantidades pedidas
        Ejemplo: 3 hojas (cantidad 3) + 3 lápices (cantidad 3) → 0/6 al inicio
        """
        entregas = self.entregas.all().select_related('util')

        if not entregas.exists():
            return '0/0'

        total_pedido = 0
        total_entregado = 0

        for entrega in entregas:
            total_pedido += entrega.util.cantidad
            total_entregado += entrega.cantidad_entregada

        return f'{total_entregado}/{total_pedido}'


class UtilEscolar(models.Model):
    salon = models.ForeignKey(
        Salon,
        on_delete=models.CASCADE,
        related_name='utiles'
    )
    nombre = models.CharField(max_length=200)
    cantidad = models.IntegerField(default=1)
    descripcion = models.TextField(blank=True, null=True)
    orden = models.IntegerField(default=0)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Útil Escolar'
        verbose_name_plural = 'Útiles Escolares'

    def __str__(self):
        return f"{self.nombre} ({self.cantidad}) - {self.salon.nombre}"


class EntregaUtil(models.Model):
    alumno = models.ForeignKey(
        Alumno,
        on_delete=models.CASCADE,
        related_name='entregas'
    )
    util = models.ForeignKey(
        UtilEscolar,
        on_delete=models.CASCADE,
        related_name='entregas'
    )
    
    cantidad_entregada = models.IntegerField(default=0)
    
    # DEPRECADO: se mantiene por compatibilidad, se actualiza en save()
    entregado = models.BooleanField(default=False)
    
    fecha_entrega = models.DateTimeField(blank=True, null=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['util__orden', 'util__nombre']
        verbose_name = 'Entrega de Útil'
        verbose_name_plural = 'Entregas de Útiles'
        unique_together = ['alumno', 'util']

    def __str__(self):
        estado = f"{self.cantidad_entregada}/{self.util.cantidad}"
        return f"{estado} {self.util.nombre} - {self.alumno.nombre}"

    @property
    def esta_completo(self):
        return self.cantidad_entregada >= self.util.cantidad

    def save(self, *args, **kwargs):
        self.entregado = self.cantidad_entregada >= self.util.cantidad
        
        if self.cantidad_entregada > 0 and not self.fecha_entrega:
            self.fecha_entrega = timezone.now()
        elif self.cantidad_entregada == 0:
            self.fecha_entrega = None
            
        super().save(*args, **kwargs)


class HistorialEntrega(models.Model):
    entrega = models.ForeignKey(
        EntregaUtil,
        on_delete=models.CASCADE,
        related_name='historial'
    )
    accion = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Historial de Entrega'
        verbose_name_plural = 'Historial de Entregas'

    def __str__(self):
        return f"{self.accion} - {self.entrega.alumno.nombre} - {self.fecha}"