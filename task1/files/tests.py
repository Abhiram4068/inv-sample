from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework_simplejwt.tokens import RefreshToken
from .models import File


User = get_user_model()


# =====================================================
# BASE CLASS FOR AUTHENTICATED TESTS
# =====================================================

class BaseAuthenticatedTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}"
        )

"""
test for authentication
"""
class AuthTests(APITestCase):

    def test_user_registration(self):
        url = reverse("files:user-register")

        data = {
        "username": "newuser",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "New",
        "last_name": "User"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_user_login(self):
        User.objects.create_user(
            username="loginuser",
            password="loginpass123"
        )

        url = reverse("files:user-login")

        data = {
            "username": "loginuser",
            "password": "loginpass123"
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("tokens", response.data)


"""
test cases 
"""

class FileTests(BaseAuthenticatedTest):

    def create_test_file(self, name="testfile.txt", content=b"Hello World"):
        return SimpleUploadedFile(
            name,
            content,
            content_type="text/plain"
        )

    """
    file create
    """
    def test_file_upload(self):
        url = reverse("files:file-create")

        file = self.create_test_file()

        data = {
            "files": [file],
            "description": "Test file"
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(File.objects.count(), 1)
    """
    file list
    """

    def test_file_list(self):
        file = self.create_test_file()

        File.objects.create(
            user=self.user,
            file=file,
            original_name="testfile.txt",
            file_size=file.size,
            content_type="text/plain",
            checksum="dummychecksum"
        )

        url = reverse("files:file-read")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
    """
    file single view
    """
    def test_file_detail(self):
        file = self.create_test_file()

        file_obj = File.objects.create(
            user=self.user,
            file=file,
            original_name="testfile.txt",
            file_size=file.size,
            content_type="text/plain",
            checksum="dummychecksum"
        )

        url = reverse("files:file-detail", args=[file_obj.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["original_name"], "testfile.txt")

    """
    file update
    """
    def test_file_update_description(self):
        file = self.create_test_file()

        file_obj = File.objects.create(
            user=self.user,
            file=file,
            original_name="testfile.txt",
            file_size=file.size,
            content_type="text/plain",
            checksum="dummychecksum"
        )

        url = reverse("files:file-update", args=[file_obj.id])

        data = {
            "description": "Updated description"
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        file_obj.refresh_from_db()
        self.assertEqual(file_obj.description, "Updated description")

    """
    file delete
    """
    def test_file_delete(self):
        file = self.create_test_file()

        file_obj = File.objects.create(
            user=self.user,
            file=file,
            original_name="testfile.txt",
            file_size=file.size,
            content_type="text/plain",
            checksum="dummychecksum"
        )

        url = reverse("files:file-delete", args=[file_obj.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        file_obj.refresh_from_db()
        self.assertTrue(file_obj.is_deleted)

    """
    file download
    """
    def test_file_download(self):
        content = b"Download test content"

        file = SimpleUploadedFile(
            "download.txt",
            content,
            content_type="text/plain"
        )

        file_obj = File.objects.create(
            user=self.user,
            file=file,
            original_name="download.txt",
            file_size=len(content),
            content_type="text/plain",
            checksum="dummychecksum"
        )

        url = reverse("files:file-download", args=[file_obj.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/plain")