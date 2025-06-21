from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware para agregar headers de seguridad"""
    
    def process_response(self, request, response):
        # Prevenir caché de cookies en navegadores
        if request.path == '/auth/logout/' or 'logout' in request.path:
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            response['Clear-Site-Data'] = '"cache", "cookies", "storage"'
            
            # Eliminar cookie de sesión explícitamente
            if hasattr(response, 'delete_cookie'):
                response.delete_cookie('sessionid')
                response.delete_cookie('csrftoken')
        
        return response

