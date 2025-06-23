from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsTestCase(TestCase):
    """Tests for the accounts app"""

    def test_custom_user_model(self):
        """Test that the custom user model works"""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("testpass123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(email="admin@example.com", password="adminpass123")
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_string_representation(self):
        """Test the string representation of the user"""
        user = User.objects.create_user(email="test@example.com", password="testpass123")
        self.assertEqual(str(user), "test@example.com")
