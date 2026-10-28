from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    """
    Test suite for User Registration, Authentication (JWT), and Token Refresh.
    """

    def setUp(self):
        self.register_url = reverse('users:register')
        self.login_url = reverse('users:login')
        self.refresh_url = reverse('users:token_refresh')
        self.user_data = {
            'username': 'testdeveloper',
            'email': 'developer@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }

    def test_user_registration_success(self):
        """Verify successful registration with proper password confirmation."""
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testdeveloper')
        self.assertEqual(response.data['user']['email'], 'developer@example.com')

        # Verify password is not saved in plain text
        user = User.objects.get(username='testdeveloper')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_user_registration_password_mismatch(self):
        """Verify registration failure when passwords do not match."""
        data = self.user_data.copy()
        data['password2'] = 'MismatchPassword999!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_user_registration_duplicate_email(self):
        """Verify registration failure on duplicate email."""
        self.client.post(self.register_url, self.user_data)
        dup_data = {
            'username': 'developer2',
            'email': 'developer@example.com',
            'password': 'StrongPassword123!',
            'password2': 'StrongPassword123!',
        }
        response = self.client.post(self.register_url, dup_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_jwt_login_success(self):
        """Verify successful login returns valid JWT access and refresh tokens."""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
        )
        login_payload = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }
        response = self.client.post(self.login_url, login_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_jwt_login_invalid_credentials(self):
        """Verify login failure with incorrect credentials."""
        login_payload = {
            'username': 'nonexistent',
            'password': 'WrongPassword123!',
        }
        response = self.client.post(self.login_url, login_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_jwt_token_refresh(self):
        """Verify obtaining new access token via refresh token."""
        User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password'],
        )
        login_payload = {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }
        login_res = self.client.post(self.login_url, login_payload)
        refresh_token = login_res.data['refresh']

        refresh_res = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_res.data)
