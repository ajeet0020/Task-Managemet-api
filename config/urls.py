from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.http import JsonResponse


def dashboard_view(request):
    """
    Renders the interactive Single Page Web Dashboard.
    """
    return render(request, 'dashboard.html')


def root_health_view(request):
    """
    Health check and root API directory view.
    """
    return JsonResponse(
        {
            "status": "healthy",
            "project": "Task Management API",
            "version": "1.0.0",
            "web_dashboard": "/dashboard/",
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
    path('', dashboard_view, name='home'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('health/', root_health_view, name='health'),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),  # DRF web browsable login
    path('api/', include('users.urls')),
    path('api/', include('tasks.urls')),
]
