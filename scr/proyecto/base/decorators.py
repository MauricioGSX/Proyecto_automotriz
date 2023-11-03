from functools import wraps
from django.http import HttpResponseForbidden

def group_required(group_name):
    def decorator(view_func):
        #Este decorador se utiliza para preservar los metadatos de la funcion original 
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verifica si el usuario actual pertenece al grupo especificado
            if not request.user.groups.filter(name=group_name).exists():
                # Si no pertenece al grupo, se devuelve una respuesta Forbidden
                return HttpResponseForbidden("No tienes permiso para acceder a esta página.")
            # Si el usuario pertenece al grupo, se llama a la vista original
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
