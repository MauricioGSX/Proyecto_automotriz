from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from base.views import Logueo
from django.contrib.auth.views import LogoutView
from base.views import *
from django.contrib.auth.decorators import user_passes_test


def es_usuario(user):
    return user.groups.filter(name='Usuario').exists()

def es_recepcionista(user):
    return user.groups.filter(name='Recepcionista').exists()

user_passes_test_es_usuario = user_passes_test(es_usuario, login_url='menu_recepcionista')
user_passes_test_es_recepcionista = user_passes_test(es_recepcionista, login_url='menu_usuario')

urlpatterns = [
     path('', CustomLoginView.as_view(), name='login'),
     path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
     path('registro/', registro.as_view(), name='registro'),
     path('lista_vehiculos_usuario/', lista_vehiculos_usuario, name='lista_vehiculos_usuario'),
     path('registrar_vehiculo/', registrar_vehiculo , name='registrar_vehiculo'),
     path('eliminar_vehiculo/<int:pk>/', EliminarVehiculo.as_view(), name='eliminar_vehiculo'),
     path('crear_cita/', crear_cita, name='crear_cita'),
     path('listar_citas/', listar_citas, name='listar_citas'),
     path('editar_trabajo/<int:pk>/', TrabajoUpdateView.as_view(), name='editar_trabajo'),
     path('detalles_cita/<int:cita_id>/', detalles_cita, name='detalles_cita'),
     path('agregar_checklist/<int:cita_id>/', agregar_checklist, name='agregar_checklist'),
     path('menu_usuario/', user_passes_test_es_usuario(menu_usuario), name='menu_usuario'),
     path('menu_recepcionista/', user_passes_test_es_recepcionista(menu_recepcionista), name='menu_recepcionista'),
     path('listar_citas_recepcion/', listar_citas_recepcion , name='listar_citas_recepcion'),
     path('detalles_cita_recepcion/<int:cita_id>/', detalles_cita_recepcion, name='detalles_cita_recepcion'),
     path('agregar_trabajo/<int:cita_id>/', agregar_trabajo, name='agregar_trabajo'),
     path('vehiculos-en-taller/', vehiculos_en_taller , name='vehiculos_en_taller'),
     path('agenda-diaria/', agenda_diaria, name='agenda_diaria'),
     path('ver-y-editar-perfil/', ver_y_editar_perfil, name='ver_y_editar_perfil'),
     path('perfil/<int:usuario_id>/', detalle_perfil, name='detalle_perfil'),
     path('cambiar-contraseña/', cambiar_contraseña, name='cambiar_contraseña'),
     path('mecanicos/', lista_mecanicos, name='lista_mecanicos'),
    path('mecanicos/agregar/', agregar_mecanico, name='agregar_mecanico'),
    path('mecanicos/eliminar/<int:mec_id>/', eliminar_mecanico, name='eliminar_mecanico'),
    path('admin/', admin.site.urls),
     ]