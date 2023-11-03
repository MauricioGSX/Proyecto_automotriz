from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.views import (
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.urls import reverse_lazy, reverse
from .decorators import group_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.models import Group
from .forms import *
from .models import Vehiculo, Cita, Trabajo, Checklist, Noticias
from datetime import date
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

# Sistema de Logeo - Deslogueo y registro de usuario y validacion de redireccion a menu


class CustomLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user  # Obtiene el usuario que hizo la solicitud.
        # Si el usuario pertenece al grupo 'Usuario', redirige a la página 'menu_usuario'.
        if user.groups.filter(name="Usuario").exists():
            return reverse_lazy("menu_usuario")
        # Si el usuario pertenece al grupo 'Recepcionista', redirige a la página 'menu_recepcionista'.
        elif user.groups.filter(name="Recepcionista").exists():
            return reverse_lazy("menu_recepcionista")
        # Si el usuario no pertenece a ninguno de los grupos anteriores, usa la URL predeterminada.
        else:
            return super().get_success_url()

    def form_valid(self, form):
        remember_me = form.cleaned_data.get(
            "remember_me"
        )  # Obtiene el valor del campo remember_me del formulario.
        # Si remember_me es False establece la expiración de la sesión actual en 0 (0 es un valor nominal genera que el sistema no deslogue si lo cambias el sistema te expulsa a los segundos asignados).
        if not remember_me:
            self.request.session.set_expiry(0)
        # Llama al método form_valid en la superclase para realizar el comportamiento predeterminado después de la validación exitosa.
        return super().form_valid(form)


class Logueo(LoginView):
    template_name = "login.html"
    field = "__all__"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("index")


class registro(FormView):
    template_name = "registro.html"
    # Clase del formulario personalizado utilizado para recopilar datos de registro de usuario.
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True

    # URL a la que se redirigirá al usuario después de un registro exitoso.
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        # Guarda el usuario recién registrado utilizando los datos del formulario.
        user = form.save()
        # Obtiene el grupo deseado Usuario desde la base de datos.
        grupo_deseado = Group.objects.get(name="Usuario")
        # Asigna el usuario al grupo deseado
        user.groups.add(grupo_deseado)
        return super().form_valid(form)


def es_usuario(user):
    return user.groups.filter(name="Usuario").exists()


def es_recepcionista(user):
    return user.groups.filter(name="Recepcionista").exists()


@login_required
def ver_y_editar_perfil(request):
    # Intenta obtener un objeto PerfilUsuario asociado request.user
    # Si existe, se asigna a la variable perfil de lo contrario se crea un nuevo objeto PerfilUsuario.
    perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)

    if request.method == "POST":
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect("ver_y_editar_perfil")
    else:
        form = PerfilUsuarioForm(instance=perfil)

    return render(request, "perfil/ver_y_editar_perfil.html", {"form": form})


@login_required
@user_passes_test(es_usuario, login_url="menu_recepcionista")
def menu_usuario(request):
    user = request.user
    noticias = Noticias.objects.order_by('-created')
    context = {
        'noticias': noticias,
        'user': user,
    }
    return render(request, "menu_usuario.html", context)


@login_required
@user_passes_test(es_recepcionista, login_url="menu_usuario")
def menu_recepcionista(request):
    user = request.user
    noticias = Noticias.objects.order_by('-created')
    context = {
        'noticias': noticias,
        'user': user,
    }
    return render(request, "menu_recepcionista.html", context)


# Sistemas diseñados para el grupo de usuario


@login_required
@group_required("Usuario")
def lista_vehiculos_usuario(request):
    vehiculos = Vehiculo.objects.filter(cliente=request.user)
    return render(
        request,
        "usuario/vehiculo/lista_vehiculos_usuario.html",
        {"vehiculos": vehiculos},
    )


@login_required
@group_required("Usuario")
def registrar_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            vehiculo.cliente = request.user
            form.save()
            return redirect("lista_vehiculos_usuario")
    else:
        form = VehiculoForm()

    return render(request, "usuario/vehiculo/registro_vehiculo.html", {"form": form})


@method_decorator(
    [login_required, group_required("Usuario")], name="dispatch"
)  # dispatch es el punto de entrada principal para procesar una solicitud HTTP
class EliminarVehiculo(DeleteView):
    model = Vehiculo
    template_name = "usuario/vehiculo/borrar_vehiculo.html"
    success_url = reverse_lazy(
        "lista_vehiculos_usuario"
    )  # reverse_lazy se usa para evitar problemas de importación circular


@login_required
@group_required("Usuario")
def crear_cita(request):
    if request.method == "POST":
        form = CitaForm(request.user, request.POST)
        if form.is_valid():
            nueva_cita = form.save()

            # Después de crear la cita, crea un nuevo Checklist asociado a esa cita
            checklist = Checklist(cita=nueva_cita)
            checklist.save()

            return redirect("listar_citas")
    else:
        form = CitaForm(user=request.user)

    context = {"form": form}
    return render(request, "usuario/citas/crear_cita.html", context)


@login_required
@group_required("Usuario")
def listar_citas(request):
    citas = Cita.objects.filter(vehiculo__cliente=request.user, estado="En proceso")
    context = {"citas": citas}
    return render(request, "usuario/citas/listar_citas.html", context)


@login_required
@group_required("Usuario")
def detalles_cita(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    context = {"cita": cita}
    return render(request, "usuario/trabajo/detalles_cita.html", context)


# Sistema Diseñado para el Recepcionista


@login_required
@group_required("Recepcionista")
def listar_citas_recepcion(request):
    citas = Cita.objects.all()
    context = {"citas": citas}
    return render(request, "recepcionista/citas/listar_citas.html", context)


@login_required
@group_required("Recepcionista")
def detalles_cita_recepcion(request, cita_id):
    # Obtiene la instancia de la Cita con el ID proporcionado o muestra una página 404 si no se encuentra.
    cita = get_object_or_404(Cita, pk=cita_id)
    context = {"cita": cita}
    return render(request, "recepcionista/trabajo/detalles_cita.html", context)


@login_required
@group_required("Recepcionista")
def agregar_trabajo(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)

    if request.method == "POST":
        trabajo_form = TrabajoForm(request.POST)
        checklist_form = ChecklistForm(request.POST)

        if trabajo_form.is_valid() and checklist_form.is_valid():
            trabajo = trabajo_form.save(commit=False)
            trabajo.cita = cita
            trabajo.save()

            return redirect("listar_citas_recepcion")
    else:
        trabajo_form = TrabajoForm()

    return render(
        request,
        "recepcionista/trabajo/agregar_trabajo.html",
        {
            "cita": cita,
            "trabajo_form": trabajo_form,
        },
    )


@login_required
@group_required("Recepcionista")
def agregar_checklist(request, cita_id):
    cita = get_object_or_404(Cita, pk=cita_id)
    checklist, created = Checklist.objects.get_or_create(cita=cita)

    if request.method == "POST":
        checklist_form = ChecklistForm(request.POST, instance=checklist)
        if checklist_form.is_valid():
            checklist_form.save()
            return redirect("listar_citas_recepcion")
    else:
        checklist_form = ChecklistForm(instance=checklist)

    return render(
        request,
        "recepcionista/trabajo/agregar_checklist.html",
        {
            "cita": cita,
            "checklist_form": checklist_form,
        },
    )


@method_decorator([login_required, group_required("Recepcionista")], name="dispatch")
class TrabajoUpdateView(UpdateView):
    model = Trabajo
    fields = ["descripcion", "estado"]
    template_name = "recepcionista/trabajo/editar_trabajo.html"

    def get_success_url(self):
        return reverse("detalles_cita_recepcion", kwargs={"cita_id": self.object.cita_id})


@login_required
@group_required("Recepcionista")
def vehiculos_en_taller(request):
    citas_en_proceso = Cita.objects.filter(estado="En proceso")
    vehiculos_en_taller = [cita.vehiculo for cita in citas_en_proceso]
    return render(
        request,
        "recepcionista/citas/taller_vehiculos.html",
        {"vehiculos_en_taller": vehiculos_en_taller},
    )


@login_required
@group_required("Recepcionista")
def agenda_diaria(request):
    today = date.today()
    citas_hoy = Cita.objects.filter(fecha=today)
    return render(
        request, "recepcionista/agenda/agenda_diaria.html", {"citas_hoy": citas_hoy}
    )


@login_required
@group_required("Recepcionista")
def detalle_perfil(request, usuario_id):
    # Obtiene la instancia del usuario con el ID proporcionado o muestra una página 404 si no se encuentra.
    usuario = get_object_or_404(User, pk=usuario_id)
    # Obtiene la instancia del PerfilUsuario asociado a ese usuario o muestra una página 404 si no se encuentra.
    perfil = get_object_or_404(PerfilUsuario, usuario=usuario)
    # Comprueba si ciertos campos del perfil tienen valores para determinar si se han modificado.
    datos_modificados = (
        perfil.numero_telefono is not None and perfil.numero_telefono != "",
        perfil.direccion is not None and perfil.direccion != "",
        perfil.fecha_nacimiento is not None,
    )
    return render(
        request,
        "perfil/detalle_perfil.html",
        {
            "usuario": usuario,
            "perfil": perfil,
            "datos_modificados": any(datos_modificados),
        },
    )


@login_required
def cambiar_contraseña(request):
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar la sesión de autenticación del usuario para evitar la desconexión después del cambio de contraseña.
            update_session_auth_hash(request, user)
            return redirect("perfil")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, "perfil/cambio_contraseña.html", {"form": form})


@login_required
@group_required("Recepcionista")
def eliminar_mecanico(request, mec_id):
    mecánico = get_object_or_404(Mecanico, id=mec_id)
    mecánico.delete()
    return redirect("lista_mecanicos")


@login_required
@group_required("Recepcionista")
def agregar_mecanico(request):
    if request.method == "POST":
        form = MecanicoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_mecanicos")
    else:
        form = MecanicoForm()

    mecanicos = Mecanico.objects.all()
    return render(
        request,
        "recepcionista/mecanico/agregar_mecanico.html",
        {"form": form, "mecanicos": mecanicos},
    )


@login_required
@group_required("Recepcionista")
def lista_mecanicos(request):
    mecanicos = Mecanico.objects.filter()
    return render(
        request, "recepcionista/mecanico/lista_mecanicos.html", {"mecanicos": mecanicos}
    )

