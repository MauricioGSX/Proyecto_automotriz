from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.utils import timezone

# Definición de opciones para el horario de la cita.
HORARIO_CHOICES = (
    ('AM', 'AM'),
    ('PM', 'PM'),
)

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    numero_telefono = models.CharField(max_length=15, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    puntos_acumulados = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.usuario.username 
#  receiver que se activa después de guardar un objeto User
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=instance)
    instance.perfilusuario.save()


class Vehiculo(models.Model):
    cliente = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    placa = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.marca} {self.modelo} - {self.placa}"

class Mecanico(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre

class Cita(models.Model):

    ESTADO_CHOICES = (
    ('En proceso', 'En proceso'),
    ('Completada', 'Completada'),
    ('Cancelada', 'Cancelada'),
    )

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    fecha = models.DateField(null=True)
    horario = models.CharField(max_length=2, choices=HORARIO_CHOICES, default='AM')
    mecanico = models.ForeignKey(Mecanico, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='En proceso')
    
    def clean(self):
        existing_cita = Cita.objects.filter(mecanico=self.mecanico, fecha=self.fecha, horario=self.horario).exclude(pk=self.pk).first()

        if existing_cita:
            raise ValidationError("Este mecánico ya tiene una cita en este horario.")
        
    def __str__(self):
         return f"Cita para el vehículo {self.vehiculo} el {self.fecha} en horario {self.get_horario_display()}"

#Receptor (receiver) que se activa antes de guardar un objeto Cita.
@receiver(pre_save, sender=Cita)
def validate_unique_horario(sender, instance, **kwargs):
    existing_cita = Cita.objects.filter(mecanico=instance.mecanico, fecha=instance.fecha, horario=instance.horario).exclude(pk=instance.pk).first()

    if existing_cita:
        raise ValidationError("Este mecánico ya tiene una cita en este horario.")
    def __str__(self):
        return f"Cita para {self.vehiculo} el {self.fecha} ({self.horario})"

class Trabajo(models.Model):
    ESTADO_TRABAJO_CHOICES = (
        ('En proceso', 'En proceso'),
        ('Espera de repuestos', 'Espera de repuestos'),
        ('Completado', 'Completado'),
    )
    
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, choices=ESTADO_TRABAJO_CHOICES, default='En proceso')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Punto(models.Model):
    cliente = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,)
    puntos = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f" {self.cliente} - Puntos: {self.puntos}"

class Checklist(models.Model):
    cita = models.OneToOneField(Cita, on_delete=models.CASCADE, related_name='checklist')
    Choque_Delantero = models.BooleanField(default=False)
    Choque_Trasero = models.BooleanField(default=False)
    Choque_Lateral_Izquierdo = models.BooleanField(default=False)
    Choque_Lateral_Derecho = models.BooleanField(default=False)
    Extintor = models.BooleanField(default=False)
    Botiquin = models.BooleanField(default=False)
    Triangulos = models.BooleanField(default=False)
    Gata = models.BooleanField(default=False)
    Rueda_de_Repuesto = models.BooleanField(default=False)

    def __str__(self):
        return f"Checklist para cita {self.cita.id}"
    
class Noticias(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen_url = models.TextField()
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title + (' - ') + self.user.username
    
    def tiempo_transcurrido(self):
        now = timezone.now()
        time_diff = now - self.created

        if time_diff.days > 365:
            years = time_diff.days // 365
            return f"Creado hace {years} {'años' if years > 1 else 'Año'}"
        elif time_diff.days > 30:
            months = time_diff.days // 30
            return f"Creado hace {months} {'meses' if months > 1 else 'Mes'}"
        elif time_diff.days > 0:
            return f"Creado hace {time_diff.days} {'días' if time_diff.days > 1 else 'Día'}"
        else:
            hours, remainder = divmod(time_diff.seconds, 3600)  # Dividir los segundos en horas y minutos
            minutes, _ = divmod(remainder, 60)  # Dividir los segundos restantes en minutos
            if hours > 0:
                return f"Creado hace {hours} {'horas' if hours > 1 else 'Hora'} y {minutes} {'minutos' if minutes > 1 else 'Minuto'}"
            else:
                return f"Creado hace {minutes} {'minutos' if minutes > 1 else 'Minuto'}"