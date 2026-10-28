from datetime import timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from tasks.models import Project, Task


class TaskManagementAPITests(APITestCase):
    """
    Comprehensive test suite covering CRUD, Permissions & Tenant Isolation,
    Filtering, Search, Ordering, and Pagination.
    """

    def setUp(self):
        # Create User 1 and User 2
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='Password123!'
        )
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='Password123!'
        )

        # Authenticate as user1 by default
        self.client.force_authenticate(user=self.user1)

        # URLs
        self.project_list_url = reverse('tasks:project-list')
        self.task_list_url = reverse('tasks:task-list')

        # Base project for user1
        self.project1 = Project.objects.create(
            name='Alpha Project',
            description='Main project for Alice',
            owner=self.user1,
        )

        # Base project for user2
        self.project2 = Project.objects.create(
            name='Beta Project',
            description='Private project for Bob',
            owner=self.user2,
        )

        # Base tasks for user1
        self.now = timezone.now()
        self.task1 = Task.objects.create(
            title='Setup database schema',
            description='PostgreSQL & SQLite integration',
            status=Task.StatusChoices.DONE,
            priority=Task.PriorityChoices.HIGH,
            due_date=self.now + timedelta(days=1),
            project=self.project1,
        )
        self.task2 = Task.objects.create(
            title='Write unit tests',
            description='Cover authentication and permissions',
            status=Task.StatusChoices.IN_PROGRESS,
            priority=Task.PriorityChoices.MEDIUM,
            due_date=self.now + timedelta(days=3),
            project=self.project1,
        )

        # Base task for user2
        self.task3 = Task.objects.create(
            title='Bob confidential task',
            description='Secret work for Bob',
            status=Task.StatusChoices.TODO,
            priority=Task.PriorityChoices.LOW,
            due_date=self.now + timedelta(days=5),
            project=self.project2,
        )

    # ==========================
    # 1. PROJECT CRUD & NESTED
    # ==========================
    def test_create_project(self):
        """User can create a project and is automatically assigned as owner."""
        payload = {'name': 'New Roadmap', 'description': 'Q3 development roadmap'}
        response = self.client.post(self.project_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Roadmap')
        self.assertEqual(response.data['owner'], self.user1.username)

    def test_list_projects_shows_task_count(self):
        """Project list and detail endpoints show aggregated task_count."""
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only return user1's project
        self.assertEqual(response.data['count'], 1)
        project_data = response.data['results'][0]
        self.assertEqual(project_data['id'], self.project1.id)
        # project1 has task1 and task2
        self.assertEqual(project_data['task_count'], 2)

    def test_update_project(self):
        """User can update their own project."""
        detail_url = reverse('tasks:project-detail', args=[self.project1.id])
        response = self.client.patch(detail_url, {'name': 'Alpha Project Renamed'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project1.refresh_from_db()
        self.assertEqual(self.project1.name, 'Alpha Project Renamed')

    def test_delete_project(self):
        """User can delete their own project."""
        detail_url = reverse('tasks:project-detail', args=[self.project1.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project1.id).exists())

    # ==========================
    # 2. TASK CRUD
    # ==========================
    def test_create_task_success(self):
        """User can create a task inside their own project."""
        payload = {
            'title': 'Deploy to Render',
            'description': 'Configure build and start commands',
            'status': 'todo',
            'priority': 'high',
            'project': self.project1.id,
        }
        response = self.client.post(self.task_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Deploy to Render')
        self.assertEqual(response.data['project'], self.project1.id)

    def test_update_task(self):
        """User can update a task in their project."""
        detail_url = reverse('tasks:task-detail', args=[self.task1.id])
        response = self.client.patch(detail_url, {'status': 'done'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'done')

    def test_delete_task(self):
        """User can delete their task."""
        detail_url = reverse('tasks:task-detail', args=[self.task1.id])
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())

    # ==================================================
    # 3. PERMISSION ISOLATION (MULTI-TENANT SECURITY)
    # ==================================================
    def test_user_cannot_view_or_access_other_users_projects(self):
        """Bob cannot access or view Alice's project."""
        self.client.force_authenticate(user=self.user2)
        # In list: Bob should only see his own project (count 1)
        response = self.client.get(self.project_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.project2.id)

        # Direct access to Alice's project yields 404
        alice_project_url = reverse('tasks:project-detail', args=[self.project1.id])
        res_get = self.client.get(alice_project_url)
        self.assertEqual(res_get.status_code, status.HTTP_404_NOT_FOUND)

        # Bob cannot modify Alice's project
        res_patch = self.client.patch(alice_project_url, {'name': 'Hacked Name'})
        self.assertEqual(res_patch.status_code, status.HTTP_404_NOT_FOUND)

        # Bob cannot delete Alice's project
        res_del = self.client.delete(alice_project_url)
        self.assertEqual(res_del.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_view_or_access_other_users_tasks(self):
        """Bob cannot access or view Alice's tasks."""
        self.client.force_authenticate(user=self.user2)
        # In list: Bob only sees his own tasks
        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.task3.id)

        # Direct access to Alice's task yields 404
        alice_task_url = reverse('tasks:task-detail', args=[self.task1.id])
        res_get = self.client.get(alice_task_url)
        self.assertEqual(res_get.status_code, status.HTTP_404_NOT_FOUND)

        # Modifying Alice's task yields 404
        res_patch = self.client.patch(alice_task_url, {'status': 'done'})
        self.assertEqual(res_patch.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_create_task_in_another_users_project(self):
        """Serializer validation blocks Bob from creating a task inside Alice's project."""
        self.client.force_authenticate(user=self.user2)
        payload = {
            'title': 'Intrusion task',
            'project': self.project1.id,  # Owned by Alice!
        }
        response = self.client.post(self.task_list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('project', response.data)
        self.assertIn("cannot associate a task with a project you do not own", str(response.data['project']))

    # ==========================
    # 4. FILTERING, SEARCH & ORDERING
    # ==========================
    def test_task_filtering_by_status_and_priority_and_project(self):
        """Filter tasks by ?status=done&priority=high&project=ID."""
        # Query matching task1: status=done, priority=high, project=project1.id
        url = f"{self.task_list_url}?status=done&priority=high&project={self.project1.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.task1.id)

        # Filter with no matching records
        no_match_url = f"{self.task_list_url}?status=todo&priority=high"
        res_none = self.client.get(no_match_url)
        self.assertEqual(res_none.status_code, status.HTTP_200_OK)
        self.assertEqual(res_none.data['count'], 0)

    def test_task_search(self):
        """Full text search on title & description via ?search=."""
        url = f"{self.task_list_url}?search=database"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Setup database schema')

    def test_task_ordering(self):
        """Ordering tasks by ?ordering=due_date."""
        url = f"{self.task_list_url}?ordering=due_date"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        # task1 is due earlier than task2
        self.assertEqual(results[0]['id'], self.task1.id)
        self.assertEqual(results[1]['id'], self.task2.id)

    # ==========================
    # 5. PAGINATION
    # ==========================
    def test_pagination_page_size_10(self):
        """Verify that page size defaults to 10."""
        # Create 12 additional tasks for project 1
        for i in range(12):
            Task.objects.create(
                title=f'Batch task {i}',
                project=self.project1,
            )

        response = self.client.get(self.task_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Total tasks for Alice: 2 initial + 12 new = 14
        self.assertEqual(response.data['count'], 14)
        # Page size limit: 10 items
        self.assertEqual(len(response.data['results']), 10)
        self.assertIsNotNone(response.data['next'])
