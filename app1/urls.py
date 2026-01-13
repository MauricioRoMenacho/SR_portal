from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),  # ← Cambié 'home' por 'inicio'
    path('almacenes/', views.almacenes, name='almacenes'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.configuracion, name='configuracion'),
    path('logout/', views.logout_view, name='logout'),  # ← Agregué logout
]