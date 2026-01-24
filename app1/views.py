from django.shortcuts import render, redirect
from django.contrib.auth import logout

def inicio(request):
    return render(request, 'home.html')

def almacenes(request):
    return render(request, 'almacenes.html')

def InventrioAG(request):
    return render(request, 'almacenes/almgeneral/InventarioAG.html')

def agregar(request):
    return render(request, 'almacenes/almgeneral/agregar.html')

def perfil(request):
    return render(request, 'perfil.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def logout_view(request):
    logout(request)
    return redirect('inicio')  