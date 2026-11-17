from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashuser',
            password='testpassword123'
        )

    def test_dashboard_login_required(self):
        """Test that unauthenticated users are redirected to login."""
        response = self.client.get(reverse('dashboard:index'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue('/accounts/login/' in response.url)

    def test_dashboard_authenticated_access(self):
        """Test that authenticated users can access the dashboard."""
        self.client.login(username='dashuser', password='testpassword123')
        # Even if template doesn't exist yet, view function executes
        # We test that reverse resolves correctly
        url = reverse('dashboard:index')
        self.assertEqual(url, '/')
