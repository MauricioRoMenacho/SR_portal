from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.contrib import messages
import openpyxl

from ..models import Salon, Alumno
from ..forms import SalonForm


# ─────────────────────────────────────────────────────────────────────
# LISTADO DE SALONES
# ─────────────────────────────────────────────────────────────────────

class SalonesList(ListView):
    model = Salon
    template_name = 'almacenes/almutiles/Entregautiles.html'
    context_object_name = 'salones'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total_alumnos = Alumno.objects.count()
        entregas_completas = Alumno.objects.filter(entrega_completada=True).count()
        context['total_salones'] = Salon.objects.count()
        context['total_alumnos'] = total_alumnos
        context['entregas_completas'] = entregas_completas
        context['pendientes'] = total_alumnos - entregas_completas
        return context


# ─────────────────────────────────────────────────────────────────────
# CREAR SALÓN
# ─────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────
# EDITAR SALÓN
# ─────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────
# ELIMINAR SALÓN
# ─────────────────────────────────────────────────────────────────────

def eliminar_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    salon.delete()
    messages.success(request, 'Salón eliminado exitosamente.')
    return redirect('entrega_utiles')


# ─────────────────────────────────────────────────────────────────────
# DETALLE DEL SALÓN (tabla de alumnos + importar excel)
# ─────────────────────────────────────────────────────────────────────

def detalle_salon(request, pk):
    salon = get_object_or_404(Salon, pk=pk)
    alumnos = salon.alumnos.all().order_by('nombre')
    return render(request, 'almacenes/almutiles/Entrega_Utiles/detalle_salon.html', {
        'salon': salon,
        'alumnos': alumnos,
    })


# ─────────────────────────────────────────────────────────────────────
# IMPORTAR EXCEL DE ALUMNOS
# ─────────────────────────────────────────────────────────────────────

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

            # Columnas del Excel
            aula = str(row[4]).strip().upper() if row[4] else ''  # Col E = AULA
            nombre = str(row[8]).strip() if row[8] else ''         # Col I = NOMBRE
            dni = str(row[10]).strip() if row[10] else ''          # Col K = DNI
            sexo = str(row[11]).strip().upper() if row[11] else '' # Col L = SEXO

            # 🔍 FILTRO: Comparar AULA del Excel con NOMBRE del Salón
            # Por ejemplo: si salon.nombre = "EULER", solo importa filas donde AULA = "EULER"
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

            Alumno.objects.create(
                salon=salon,
                nombre=nombre,
                dni=dni,
                sexo=sexo,
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
# ─────────────────────────────────────────────────────────────────────
# API — Alumnos de un salón (para el modal AJAX)
# ─────────────────────────────────────────────────────────────────────

@require_GET
def api_alumnos_salon(request, salon_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    alumnos = salon.alumnos.all().values(
        'nombre', 'dni', 'email', 'entrega_completada'
    )
    return JsonResponse({'alumnos': list(alumnos)})


# ─────────────────────────────────────────────────────────────────────
# API — Toggle entrega de un alumno
# ─────────────────────────────────────────────────────────────────────

def api_toggle_entrega(request, alumno_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    alumno = get_object_or_404(Alumno, pk=alumno_id)
    alumno.entrega_completada = not alumno.entrega_completada

    if alumno.entrega_completada:
        from django.utils import timezone
        alumno.fecha_entrega = timezone.now()
    else:
        alumno.fecha_entrega = None

    alumno.save()
    return JsonResponse({'entrega_completada': alumno.entrega_completada})


# ─────────────────────────────────────────────────────────────────────
# API — Eliminar un alumno
# ─────────────────────────────────────────────────────────────────────

def api_eliminar_alumno(request, alumno_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    alumno = get_object_or_404(Alumno, pk=alumno_id)
    alumno.delete()
    return JsonResponse({'ok': True})