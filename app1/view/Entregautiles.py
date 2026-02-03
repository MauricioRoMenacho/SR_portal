import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import openpyxl
import pandas as pd
from django.db import models
from ..models import Salon, Alumno, UtilEscolar, EntregaUtil, HistorialEntrega, ProductoAlmacen, Unidad, MovimientoInventario
from ..forms import SalonForm, UtilEscolarForm, EntregaUtilForm

# INVENTARIO DE UTILES - USANDO ProductoAlmacen (igual que AG)

def inventario_utiles(request):
    """Vista de inventario del Almacen de Utiles - Filtra por ubicacion_almacen='IU'"""
    productos = ProductoAlmacen.objects.filter(ubicacion_almacen='IU').order_by('-fecha_ingreso')
    context = {
        'productos': productos,
        'total_productos': productos.count()
    }
    return render(request, 'almacenes/almutiles/inventarioutiles.html', context)


def agregar_producto_utiles(request):
    """Agregar producto al Almacen de Utiles (IU)"""
    if request.method == 'POST':
        try:
            producto = ProductoAlmacen.objects.create(
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion'),
                ubicacion_almacen='IU',
                estante=request.POST.get('estante'),
                cantidad=request.POST.get('cantidad'),
                unidad_id=request.POST.get('unidad'),
                estado=request.POST.get('estado'),
                observaciones=request.POST.get('observaciones', '')
            )
            
            messages.success(request, f'Producto "{producto.nombre}" agregado exitosamente al Almacen de Utiles')
            return redirect('inventario_utiles')
            
        except Exception as e:
            messages.error(request, f'Error al agregar producto: {str(e)}')
    
    unidades = Unidad.objects.filter(activo=True).order_by('nombre')
    context = {
        'unidades': unidades
    }
    return render(request, 'almacenes/almutiles/agregar_producto_utiles.html', context)


def eliminar_producto_utiles(request, id_producto):
    """Eliminar producto del Almacen de Utiles"""
    producto = get_object_or_404(ProductoAlmacen, id_producto=id_producto, ubicacion_almacen='IU')
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f'Producto "{nombre}" eliminado exitosamente')
    return redirect('inventario_utiles')


# SALONES

class SalonesList(ListView):
    model = Salon
    template_name = 'almacenes/almutiles/Entregautiles.html'
    context_object_name = 'salones'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_alumnos = Alumno.objects.count()
        
        completos = 0
        parciales = 0
        pendientes = 0
        sin_lista = 0
        
        for alumno in Alumno.objects.all():
            estado = alumno.estado_entrega
            if estado == 'completo':
                completos += 1
            elif estado == 'parcial':
                parciales += 1
            elif estado == 'no_entrego':
                pendientes += 1
            else:
                sin_lista += 1
        
        context['total_salones'] = Salon.objects.count()
        context['total_alumnos'] = total_alumnos
        context['entregas_completas'] = completos
        context['entregas_parciales'] = parciales
        context['pendientes'] = pendientes
        context['sin_lista'] = sin_lista    
        return context
    
def crear_salon(request):
    if request.method == 'POST':
        form = SalonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salon creado exitosamente.')
            return redirect('entrega_utiles')
    else:
        form = SalonForm()
    return render(request, 'almacenes/almutiles/Entrega_Utiles/crear_salon.html', {'form': form})


def editar_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    if request.method == 'POST':
        form = SalonForm(request.POST, instance=salon)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salon actualizado exitosamente.')
            return redirect('entrega_utiles')
    else:
        form = SalonForm(instance=salon)
    return render(request, 'almacenes/almutiles/Entrega_Utiles/Editarsalon.html', {
        'form': form,
        'salon': salon,
    })


def eliminar_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    salon.delete()
    messages.success(request, 'Salon eliminado exitosamente.')
    return redirect('entrega_utiles')


def detalle_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    alumnos = salon.alumnos.all().order_by('nombre')
    utiles = salon.utiles.all()
    
    # Preparar datos de entregas para cada alumno (para filtros JS)
    alumnos_con_entregas = []
    for alumno in alumnos:
        entregas_data = []
        for entrega in alumno.entregas.all().select_related('util'):
            entregas_data.append({
                'util_id': entrega.util.pk,
                'util_nombre': entrega.util.nombre,
                'cantidad_entregada': entrega.cantidad_entregada,
                'cantidad_total': entrega.util.cantidad
            })
        
        alumno.entregas_json = json.dumps(entregas_data)
        alumnos_con_entregas.append(alumno)
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/detalle_salon.html', {
        'salon': salon,
        'alumnos': alumnos_con_entregas,
        'utiles': utiles,
        'total_utiles': utiles.count()
    })


def importar_excel_alumnos(request, pk):
    salon = get_object_or_404(Salon, pk=pk)

    if request.method != 'POST' or 'archivo_excel' not in request.FILES:
        messages.error(request, 'No se envio archivo.')
        return redirect('detalle_salon', pk=salon.pk)

    archivo = request.FILES['archivo_excel']

    if not archivo.name.endswith(('.xlsx', '.xls')):
        messages.error(request, 'Solo se permiten archivos Excel (.xlsx, .xls).')
        return redirect('detalle_salon', pk=salon.pk)

    try:
        wb = openpyxl.load_workbook(archivo)
        ws = wb.active

        creados = 0
        duplicados = 0
        ignorados = 0

        for row_idx, row in enumerate(ws.iter_rows(min_row=6, values_only=True), start=6):
            if not row or len(row) < 12:
                ignorados += 1
                continue

            aula = str(row[4]).strip().upper() if row[4] else ''
            nombre = str(row[8]).strip() if row[8] else ''
            dni = str(row[10]).strip() if row[10] else ''
            sexo = str(row[11]).strip().upper() if row[11] else ''

            if aula != salon.nombre.upper():
                ignorados += 1
                continue

            if not nombre or not dni:
                ignorados += 1
                continue

            if sexo not in ('M', 'F'):
                sexo = ''

            if Alumno.objects.filter(dni=dni).exists():
                duplicados += 1
                continue

            alumno = Alumno.objects.create(
                salon=salon,
                nombre=nombre,
                dni=dni,
                sexo=sexo,
            )
            
            # Crear entregas con cantidad_entregada = 0
            for util in salon.utiles.all():
                EntregaUtil.objects.create(
                    alumno=alumno,
                    util=util,
                    cantidad_entregada=0,
                    entregado=False
                )
            
            creados += 1

        wb.close()

        msg_parts = []
        if creados:
            msg_parts.append(f'{creados} alumno{"s" if creados != 1 else ""} importado{"s" if creados != 1 else ""}')
        if duplicados:
            msg_parts.append(f'{duplicados} duplicado{"s" if duplicados != 1 else ""} ignorado{"s" if duplicados != 1 else ""}')
        if ignorados:
            msg_parts.append(f'{ignorados} fila{"s" if ignorados != 1 else ""} ignorada{"s" if ignorados != 1 else ""}')

        if creados > 0:
            messages.success(request, ' | '.join(msg_parts))
        else:
            messages.warning(request, f'No se importaron alumnos. {" | ".join(msg_parts)}')

    except Exception as e:
        messages.error(request, f'Error al procesar el archivo: {str(e)}')

    return redirect('detalle_salon', pk=salon.pk)


# UTILES ESCOLARES

def lista_utiles(request, salon_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    utiles = salon.utiles.all()
    
    # Obtener productos del Almacen de Utiles
    productos_inventario = ProductoAlmacen.objects.filter(
        ubicacion_almacen='IU'
    ).select_related('unidad').order_by('nombre')
    
    if request.method == 'POST':
        tipo_agregar = request.POST.get('tipo_agregar')
        
        if tipo_agregar == 'inventario':
            producto_id = request.POST.get('producto_id')
            cantidad = request.POST.get('cantidad', 1)
            
            try:
                producto = ProductoAlmacen.objects.get(id_producto=producto_id, ubicacion_almacen='IU')
                
                util = UtilEscolar.objects.create(
                    salon=salon,
                    nombre=producto.nombre,
                    cantidad=int(cantidad),
                    descripcion=producto.descripcion,
                    orden=salon.utiles.count() + 1
                )
                
                # Crear entregas para todos los alumnos
                for alumno in salon.alumnos.all():
                    EntregaUtil.objects.create(
                        alumno=alumno,
                        util=util,
                        cantidad_entregada=0,
                        entregado=False
                    )
                
                messages.success(request, f'Util "{util.nombre}" agregado exitosamente desde inventario.')
                return redirect('lista_utiles', salon_id=salon.pk)
                
            except ProductoAlmacen.DoesNotExist:
                messages.error(request, 'Producto no encontrado en el inventario.')
            except Exception as e:
                messages.error(request, f'Error al agregar util: {str(e)}')
        
        else:
            # Agregar personalizado
            form = UtilEscolarForm(request.POST)
            if form.is_valid():
                util = form.save(commit=False)
                util.salon = salon
                util.orden = salon.utiles.count() + 1
                util.save()
                
                # Crear entregas para todos los alumnos
                for alumno in salon.alumnos.all():
                    EntregaUtil.objects.create(
                        alumno=alumno,
                        util=util,
                        cantidad_entregada=0,
                        entregado=False
                    )
                
                messages.success(request, f'Util "{util.nombre}" agregado exitosamente.')
                return redirect('lista_utiles', salon_id=salon.pk)
    else:
        form = UtilEscolarForm()
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/lista_utiles.html', {
        'salon': salon,
        'utiles': utiles,
        'form': form,
        'productos_inventario': productos_inventario
    })


def eliminar_util(request, util_id):
    util = get_object_or_404(UtilEscolar, pk=util_id)
    salon_id = util.salon.pk
    util.delete()
    messages.success(request, f'Util "{util.nombre}" eliminado exitosamente.')
    return redirect('lista_utiles', salon_id=salon_id)


# ENTREGAS DE ALUMNOS

def detalle_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    entregas = alumno.entregas.all().select_related('util')
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/detalle_alumno.html', {
        'alumno': alumno,
        'entregas': entregas,
        'salon': alumno.salon
    })


def editar_entregas_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    entregas = alumno.entregas.all().select_related('util')
    
    if request.method == 'POST':
        for entrega in entregas:
            cantidad_field = f'cantidad_{entrega.pk}'
            obs_name = f'obs_{entrega.pk}'
            
            try:
                nueva_cantidad = int(request.POST.get(cantidad_field, 0))
                nueva_cantidad = max(0, nueva_cantidad)
            except (ValueError, TypeError):
                nueva_cantidad = 0
            
            observacion = request.POST.get(obs_name, '').strip()
            
            # Registrar cambio si hubo modificacion
            if entrega.cantidad_entregada != nueva_cantidad:
                cantidad_anterior = entrega.cantidad_entregada
                entrega.cantidad_entregada = nueva_cantidad
                entrega.save()
                
                accion = f'{entrega.util.nombre}: {cantidad_anterior} → {nueva_cantidad} de {entrega.util.cantidad}'
                
                HistorialEntrega.objects.create(
                    entrega=entrega,
                    accion=accion,
                    observacion=observacion
                )
            
            # Actualizar observaciones si cambiaron
            if observacion and observacion != entrega.observaciones:
                entrega.observaciones = observacion
                entrega.save()
        
        messages.success(request, 'Entregas actualizadas exitosamente.')
        return redirect(f"{reverse('detalle_salon', kwargs={'pk': alumno.salon.pk})}?actualizado={alumno.pk}")
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/editar_entregas_alumno.html', {
        'alumno': alumno,
        'entregas': entregas,
        'salon': alumno.salon
    })


# API ENDPOINTS (AJAX)

@require_GET
def api_alumnos_salon(request, salon_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    alumnos = salon.alumnos.all().values(
        'nombre', 'dni', 'email'
    )
    return JsonResponse({'alumnos': list(alumnos)})


@require_POST
def api_eliminar_alumno(request, alumno_id):
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    alumno.delete()
    return JsonResponse({'ok': True})


@require_POST
def api_toggle_entrega_util(request, entrega_id):
    """
    DEPRECADA: Mantener por compatibilidad pero ya no se usa activamente
    """
    entrega = get_object_or_404(EntregaUtil, pk=entrega_id)
    
    if entrega.cantidad_entregada >= entrega.util.cantidad:
        entrega.cantidad_entregada = 0
    else:
        entrega.cantidad_entregada = entrega.util.cantidad
    
    entrega.save()
    
    return JsonResponse({
        'ok': True,
        'cantidad_entregada': entrega.cantidad_entregada,
        'cantidad_total': entrega.util.cantidad,
        'fecha_entrega': entrega.fecha_entrega.strftime('%d/%m/%Y %H:%M') if entrega.fecha_entrega else None
    })


@require_GET
def api_estado_alumno(request, alumno_id):
    """
    Retorna estado y progreso como X/Y (suma de cantidades) + entregas JSON
    """
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    
    entregas_data = []
    for entrega in alumno.entregas.all().select_related('util'):
        entregas_data.append({
            'util_id': entrega.util.pk,
            'util_nombre': entrega.util.nombre,
            'cantidad_entregada': entrega.cantidad_entregada,
            'cantidad_total': entrega.util.cantidad
        })
    
    return JsonResponse({
        'ok': True,
        'alumno_id': alumno.pk,
        'estado': alumno.estado_entrega,
        'progreso': alumno.progreso_entrega,
        'entregas_json': json.dumps(entregas_data)
    })