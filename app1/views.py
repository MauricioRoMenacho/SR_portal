from django.shortcuts import render, redirect
from django.contrib.auth import logout

def inicio(request):
    return render(request, 'home.html')

def almacen(request):
    return render(request, 'almacengeneral.html')

def perfil(request):
    return render(request, 'perfil.html')

def configuracion(request):
    return render(request, 'configuracion.html')

def logout_view(request):
    logout(request)
    return redirect('inicio')  