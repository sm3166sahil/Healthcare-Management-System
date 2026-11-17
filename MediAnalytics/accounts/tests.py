from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile


class AccountsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            email='test@example.com'
        )

    def test_user_profile_auto_created(self):
        """Test that a UserProfile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'analyst')

    def test_profile_str(self):
        """Test the string representation of UserProfile."""
        self.assertEqual(str(self.user.profile), 'testuser (Data Analyst)')
