from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.decorators.http import require_GET, require_POST
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
import openpyxl

from ..models import Salon, Alumno, UtilEscolar, EntregaUtil, HistorialEntrega
from ..forms import SalonForm, UtilEscolarForm, EntregaUtilForm


# ═════════════════════════════════════════════════════════════════════
# SALONES
# ═════════════════════════════════════════════════════════════════════

class SalonesList(ListView):
    model = Salon
    template_name = 'almacenes/almutiles/Entregautiles.html'
    context_object_name = 'salones'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_alumnos = Alumno.objects.count()
        
        # ✨ NUEVO: Contar por estados individuales
        completos = 0
        parciales = 0
        pendientes = 0
        sin_lista = 0
        
        for alumno in Alumno.objects.all():
            estado = alumno.estado_entrega  # Usa la property del modelo
            if estado == 'completo':
                completos += 1
            elif estado == 'parcial':
                parciales += 1
            elif estado == 'no_entrego':
                pendientes += 1
            else:  # sin_lista
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
            messages.success(request, 'Salón creado exitosamente.')
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
            messages.success(request, 'Salón actualizado exitosamente.')
            return redirect('entrega_utiles')
    else:
        form = SalonForm(instance=salon)
    return render(request, 'almacenes/almutiles/Entrega_Utiles/editar_salon.html', {
        'form': form,
        'salon': salon,
    })


def eliminar_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    salon.delete()
    messages.success(request, 'Salón eliminado exitosamente.')
    return redirect('entrega_utiles')


def detalle_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    alumnos = salon.alumnos.all().order_by('nombre')
    utiles = salon.utiles.all()
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/detalle_salon.html', {
        'salon': salon,
        'alumnos': alumnos,
        'utiles': utiles,
        'total_utiles': utiles.count()
    })


def importar_excel_alumnos(request, pk):
    salon = get_object_or_404(Salon, pk=pk)

    if request.method != 'POST' or 'archivo_excel' not in request.FILES:
        messages.error(request, 'No se envió archivo.')
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
            
            # Crear entregas automáticamente para cada útil del salón
            for util in salon.utiles.all():
                EntregaUtil.objects.create(
                    alumno=alumno,
                    util=util,
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


# ═════════════════════════════════════════════════════════════════════
# ÚTILES ESCOLARES
# ═════════════════════════════════════════════════════════════════════

def lista_utiles(request, salon_id):
    """
    Vista para gestionar la lista de útiles del salón
    """
    salon = get_object_or_404(Salon, pk=salon_id)
    utiles = salon.utiles.all()
    
    if request.method == 'POST':
        form = UtilEscolarForm(request.POST)
        if form.is_valid():
            util = form.save(commit=False)
            util.salon = salon
            util.orden = salon.utiles.count() + 1
            util.save()
            
            # Crear entregas para todos los alumnos del salón
            for alumno in salon.alumnos.all():
                EntregaUtil.objects.create(
                    alumno=alumno,
                    util=util,
                    entregado=False
                )
            
            messages.success(request, f'Útil "{util.nombre}" agregado exitosamente.')
            return redirect('lista_utiles', salon_id=salon.pk)
    else:
        form = UtilEscolarForm()
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/lista_utiles.html', {
        'salon': salon,
        'utiles': utiles,
        'form': form
    })


def eliminar_util(request, util_id):
    """
    Eliminar un útil de la lista del salón
    """
    util = get_object_or_404(UtilEscolar, pk=util_id)
    salon_id = util.salon.pk
    util.delete()
    messages.success(request, f'Útil "{util.nombre}" eliminado exitosamente.')
    return redirect('lista_utiles', salon_id=salon_id)


# ═════════════════════════════════════════════════════════════════════
# ENTREGAS DE ALUMNOS
# ═════════════════════════════════════════════════════════════════════

def detalle_alumno(request, alumno_id):
    """
    Vista detallada de las entregas de un alumno específico
    """
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    entregas = alumno.entregas.all().select_related('util')
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/detalle_alumno.html', {
        'alumno': alumno,
        'entregas': entregas,
        'salon': alumno.salon
    })


def editar_entregas_alumno(request, alumno_id):
    """
    Vista para editar las entregas de un alumno
    """
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    entregas = alumno.entregas.all().select_related('util')
    
    if request.method == 'POST':
        for entrega in entregas:
            field_name = f'entregado_{entrega.pk}'
            obs_name = f'obs_{entrega.pk}'
            
            nuevo_estado = field_name in request.POST
            observacion = request.POST.get(obs_name, '').strip()
            
            if entrega.entregado != nuevo_estado:
                entrega.entregado = nuevo_estado
                
                if nuevo_estado:
                    entrega.fecha_entrega = timezone.now()
                    accion = f'Marcado como entregado: {entrega.util.nombre}'
                else:
                    entrega.fecha_entrega = None
                    accion = f'Marcado como pendiente: {entrega.util.nombre}'
                
                entrega.save()
                
                HistorialEntrega.objects.create(
                    entrega=entrega,
                    accion=accion,
                    observacion=observacion
                )
            
            if observacion and observacion != entrega.observaciones:
                entrega.observaciones = observacion
                entrega.save()
        
        messages.success(request, 'Entregas actualizadas exitosamente.')
        return redirect('detalle_salon', pk=alumno.salon.pk)
    
    return render(request, 'almacenes/almutiles/Entrega_Utiles/editar_entregas_alumno.html', {
        'alumno': alumno,
        'entregas': entregas,
        'salon': alumno.salon
    })


# ═════════════════════════════════════════════════════════════════════
# API ENDPOINTS (AJAX)
# ═════════════════════════════════════════════════════════════════════

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
    API para marcar/desmarcar entrega de un útil específico
    """
    entrega = get_object_or_404(EntregaUtil, pk=entrega_id)
    entrega.entregado = not entrega.entregado
    
    if entrega.entregado:
        entrega.fecha_entrega = timezone.now()
    else:
        entrega.fecha_entrega = None
    
    entrega.save()
    
    return JsonResponse({
        'ok': True,
        'entregado': entrega.entregado,
        'fecha_entrega': entrega.fecha_entrega.strftime('%d/%m/%Y %H:%M') if entrega.fecha_entrega else None
    })


@require_GET
def api_estado_alumno(request, alumno_id):
    """
    API para obtener el estado actualizado de un alumno
    """
    alumno = get_object_or_404(Alumno, pk=alumno_id)
    
    return JsonResponse({
        'ok': True,
        'alumno_id': alumno.pk,
        'estado': alumno.estado_entrega,
        'porcentaje': alumno.porcentaje_entrega,
    })