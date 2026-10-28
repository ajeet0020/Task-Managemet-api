from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def root_health_view(request):
    """
    Health check and root API directory view.
    """
    return JsonResponse(
        {
            "status": "healthy",
            "project": "Task Management API",
            "version": "1.0.0",
            "endpoints": {
                "register": "/api/register/",
                "login": "/api/login/",
                "token_refresh": "/api/token/refresh/",
                "projects": "/api/projects/",
                "tasks": "/api/tasks/",
                "admin": "/admin/",
            },
        }
    )


urlpatterns = [
    path('', root_health_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('tasks.urls')),
]
