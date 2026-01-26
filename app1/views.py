from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import ProductoAlmacen, Unidad

def inicio(request):
    return render(request, 'home.html')

def almacenes(request):
    return render(request, 'almacenes.html')

def InventrioAG(request):
    productos = ProductoAlmacen.objects.filter(ubicacion_almacen='AG').order_by('-fecha_ingreso')
    
    # DEBUG: Ver en consola cuántos productos hay
    print(f"Productos encontrados: {productos.count()}")
    for p in productos:
        print(f"- {p.nombre} ({p.ubicacion_almacen})")
    
    context = {
        'productos': productos,
        'total_productos': productos.count()
    }
    return render(request, 'almacenes/almgeneral/InventarioAG.html', context)

def agregar(request):
    # Esta vista está mal - deberías usar agregar_producto
    unidades = Unidad.objects.all().order_by('nombre')
    return render(request, 'almacenes/almgeneral/agregar.html', {'unidades': unidades})

def perfil(request):
    return render(request, 'perfil.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def logout_view(request):
    logout(request)
    return redirect('inicio')

@require_POST
def crear_unidad(request):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre', '').strip()
        abreviatura = data.get('abreviatura', '').strip()
        
        if not nombre:
            return JsonResponse({'success': False, 'error': 'El nombre es requerido'})
        
        # Verificar si ya existe
        if Unidad.objects.filter(nombre__iexact=nombre).exists():
            return JsonResponse({'success': False, 'error': 'Esta unidad ya existe'})
        
        unidad = Unidad.objects.create(
            nombre=nombre,
            abreviatura=abreviatura
        )
        
        return JsonResponse({
            'success': True,
            'unidad': {
                'id': unidad.id,
                'nombre': unidad.nombre,
                'abreviatura': unidad.abreviatura
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def agregar_producto(request):
    if request.method == 'POST':
        try:
            # DEBUG: Ver qué datos llegan
            print("=== DATOS RECIBIDOS ===")
            print(f"Nombre: {request.POST.get('nombre')}")
            print(f"Descripción: {request.POST.get('descripcion')}")
            print(f"Ubicación: {request.POST.get('ubicacion_almacen')}")
            print(f"Estante: {request.POST.get('estante')}")
            print(f"Cantidad: {request.POST.get('cantidad')}")
            print(f"Unidad: {request.POST.get('unidad')}")
            print(f"Estado: {request.POST.get('estado')}")
            
            producto = ProductoAlmacen.objects.create(
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion'),
                ubicacion_almacen=request.POST.get('ubicacion_almacen'),
                estante=request.POST.get('estante'),
                cantidad=request.POST.get('cantidad'),
                unidad=request.POST.get('unidad'),
                estado=request.POST.get('estado'),
                observaciones=request.POST.get('observaciones', '')
            )
            
            print(f"✓ Producto creado: {producto.id_producto} - {producto.nombre}")
            messages.success(request, f'Producto "{producto.nombre}" agregado exitosamente')
            return redirect('InventarioAG')  # ← IMPORTANTE: debe coincidir con el name en urls.py
            
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            messages.error(request, f'Error al agregar producto: {str(e)}')
    
    unidades = Unidad.objects.all().order_by('nombre')
    context = {
        'unidades': unidades
    }
    return render(request, 'almacenes/almgeneral/agregar_producto.html', context)