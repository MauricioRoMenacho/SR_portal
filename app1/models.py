from django.db import models

class Unidad(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    abreviatura = models.CharField(max_length=10, blank=True)
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
        ('ID', 'Imprenta Deportes'),
    ]

    ESTADO_CHOICES = [
        ('DISP', 'Disponible'),
        ('AGOT', 'Agotado'),
        ('BAJO', 'Stock Bajo'),
    ]

    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)  # ← NUEVO CAMPO
    descripcion = models.CharField(max_length=255)
    ubicacion_almacen = models.CharField(
        max_length=2,
        choices=UBICACION_CHOICES
    )
    estante = models.CharField(max_length=50)
    cantidad = models.PositiveIntegerField()
    unidad = models.CharField(max_length=50)
    estado = models.CharField(
        max_length=4,
        choices=ESTADO_CHOICES
    )
    fecha_ingreso = models.DateField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)
    observaciones = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.descripcion} ({self.cantidad} {self.unidad})"
    
    class Meta:
        db_table = 'app1_productoalmacen'
        verbose_name = 'Producto de Almacén'
        verbose_name_plural = 'Productos de Almacén'