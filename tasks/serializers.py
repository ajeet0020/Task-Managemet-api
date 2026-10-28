from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Project, Task


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    Includes task_count to provide nested analytical read metrics.
    """
    owner = serializers.ReadOnlyField(source='owner.username')
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = (
            'id',
            'name',
            'description',
            'owner',
            'task_count',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'owner', 'task_count', 'created_at', 'updated_at')

    def get_task_count(self, obj):
        # Optimization: use pre-annotated task_count if available, otherwise hit DB count
        if hasattr(obj, 'task_count'):
            return obj.task_count
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model.
    Validates ownership of the associated project to ensure multi-tenant security.
    """
    project_name = serializers.ReadOnlyField(source='project.name')
    assigned_to_username = serializers.ReadOnlyField(source='assigned_to.username')

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'status',
            'priority',
            'due_date',
            'project',
            'project_name',
            'assigned_to',
            'assigned_to_username',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'project_name', 'assigned_to_username', 'created_at', 'updated_at')

    def validate_project(self, value):
        """
        Validate that the project belongs to the authenticated user.
        Prevents unauthorized users from creating tasks inside another user's project.
        """
        request = self.context.get('request')
        if request and request.user and not request.user.is_anonymous:
            if value.owner != request.user:
                raise serializers.ValidationError(
                    "You cannot associate a task with a project you do not own."
                )
        return value

