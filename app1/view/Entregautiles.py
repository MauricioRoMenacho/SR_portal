from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from django.contrib import messages

from ..models import Salon, Alumno
from ..forms import SalonForm


# ─────────────────────────────────────────────────────────────────────
# LISTADO DE SALONES  (con stats + paginación)
# ─────────────────────────────────────────────────────────────────────

class SalonesList(ListView):
    model = Salon
    # ⬇️ esta ruta tiene que coincidir EXACTA con donde está tu archivo
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

    return render(request, 'almacenes/almutiles/Entrega_Utiles/Editarsalon.html', {
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
# API — Alumnos de un salón (para el modal AJAX)
# ─────────────────────────────────────────────────────────────────────

@require_GET
def api_alumnos_salon(request, salon_id):
    salon = get_object_or_404(Salon, pk=salon_id)
    alumnos = salon.alumnos.all().values(
        'nombre', 'dni', 'email', 'entrega_completada'
    )
    return JsonResponse({'alumnos': list(alumnos)})