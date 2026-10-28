from django.db.models import Count
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsOwner
from .filters import TaskFilter
from .pagination import StandardResultsSetPagination


class ProjectViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Project resource.
    - Restricted to authenticated users.
    - Filtered to current user's projects only (data isolation).
    - Checks IsOwner object permissions.
    - Annotates task_count for optimized performance without extra DB queries.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name', 'task_count']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return only the projects owned by the currently authenticated user.
        Pre-computes task_count with SQL COUNT aggregation.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Project.objects.none()
        return (
            Project.objects.filter(owner=user)
            .annotate(task_count=Count('tasks'))
            .order_by('-created_at')
        )

    def perform_create(self, serializer):
        """
        Automatically bind current authenticated user as project owner on creation.
        """
        serializer.save(owner=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD ViewSet for Task resource.
    - Restricted to authenticated users.
    - Users can only see and manipulate tasks belonging to their projects.
    - Supports status, priority, and project filtering via django-filter.
    - Supports full text search on title & description.
    - Supports ordering by due_date, created_at, status, priority.
    - Prevents N+1 queries via select_related.
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = StandardResultsSetPagination
    filterset_class = TaskFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'created_at', 'status', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return only tasks belonging to projects owned by the currently authenticated user.
        Optimized with select_related for project and assigned_to.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Task.objects.none()
        return (
            Task.objects.filter(project__owner=user)
            .select_related('project', 'assigned_to')
            .order_by('-created_at')
        )
