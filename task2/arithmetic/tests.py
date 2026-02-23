from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


class AuthArithmeticAPITestCase(APITestCase):

    def setUp(self):
        self.register_url = reverse("arithmetic:register")
        self.login_url = reverse("arithmetic:login")
        self.logout_url = reverse("arithmetic:user-logout")
        self.refresh_url = reverse("arithmetic:token_refresh")

        self.user_data = {
            "email": "test@example.com",
            "password": "StrongPass@123",
            "confirm_password": "StrongPass@123",
            "first_name": "Test",
            "last_name": "User"
        }

    # ---------------------------
    # AUTH TESTS
    # ---------------------------

    def register_user(self):
        return self.client.post(self.register_url, self.user_data)

    def login_user(self):
        return self.client.post(self.login_url, {
            "email": "test@example.com",
            "password": "StrongPass@123"
        })

    def authenticate(self):
        self.register_user()
        login_response = self.login_user()
        access = login_response.data["tokens"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return login_response.data

    def test_user_registration(self):
        response = self.register_user()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="test@example.com").exists())

    def test_user_login(self):
        self.register_user()
        response = self.login_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)

    def test_refresh_token(self):
        self.register_user()
        login_response = self.login_user()
        refresh = login_response.data["tokens"]["refresh"]

        response = self.client.post(self.refresh_url, {
            "refresh": refresh
        })

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout(self):
        login_data = self.authenticate()
        refresh = login_data["tokens"]["refresh"]

        response = self.client.post(self.logout_url, {
            "refresh_token": refresh
        })

        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

    # ---------------------------
    # ARITHMETIC TESTS
    # ---------------------------

    def test_add_authenticated(self):
        self.authenticate()
        url = reverse("arithmetic:calaculate-add", args=[10, 5])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"], 15)

    def test_subtract_authenticated(self):
        self.authenticate()
        url = reverse("arithmetic:calaculate-subtract", args=[10, 5])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"], 5)

    def test_multiply_authenticated(self):
        self.authenticate()
        url = reverse("arithmetic:calaculate-multiply", args=[10, 5])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"], 50)

    def test_divide_authenticated(self):
        self.authenticate()
        url = reverse("arithmetic:calaculate-divide", args=[10, 5])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["Result"], 2)

    def test_divide_by_zero(self):
        self.authenticate()
        url = reverse("arithmetic:calaculate-divide", args=[10, 0])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_arithmetic_unauthorized(self):
        url = reverse("arithmetic:calaculate-add", args=[10, 5])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)