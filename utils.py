"""
Funciones utilitarias comunes para toda la aplicación
"""

from usuarios.models import TipoUsuario


def es_nutricionista_o_admin(user):
    """Verifica si el usuario es nutricionista o administrador"""
    return (
        user.is_authenticated and 
        hasattr(user, 'tipo_usuario') and 
        user.tipo_usuario in [TipoUsuario.NUTRICIONISTA, TipoUsuario.ADMINISTRADOR]
    )
