import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    """
    FilterSet for Task model supporting exact status, priority, and project filtering.
    Example: /api/tasks/?status=done&priority=high&project=1
    """
    status = django_filters.ChoiceFilter(
        choices=Task.StatusChoices.choices,
        help_text='Filter by task status (todo, in_progress, done)'
    )
    priority = django_filters.ChoiceFilter(
        choices=Task.PriorityChoices.choices,
        help_text='Filter by task priority (low, medium, high)'
    )
    project = django_filters.NumberFilter(
        field_name='project__id',
        help_text='Filter tasks belonging to a specific project ID'
    )

    class Meta:
        model = Task
        fields = ['status', 'priority', 'project']
