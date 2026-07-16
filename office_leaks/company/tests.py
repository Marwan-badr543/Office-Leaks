from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from company.db.models import Company, CompanyRate

User = get_user_model()

class CompanyRateTests(APITestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            age=25,
            country="USA",
            first_name="Test",
            last_name="User"
        )
        
        # Create a company creator user
        self.creator = User.objects.create_user(
            username="creator",
            email="creator@example.com",
            password="creatorpassword",
            age=30,
            country="USA",
            first_name="Company",
            last_name="Creator"
        )
        
        # Create a test company
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St",
            industry="Software",
            user=self.creator
        )
        
        self.update_rate_url = reverse('update-company-rate')
        self.get_rate_url = reverse('get-company-rate')

    def test_update_company_rate_creates_if_not_exists(self):
        data = {
            "user_id": self.user.id,
            "company_id": self.company.id,
            "rate": 3.5
        }
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("created successfully", response.data)
        
        # Check that the Company's current_rate was updated
        self.company.refresh_from_db()
        self.assertEqual(self.company.current_rate, 3.5)

    def test_update_company_rate_updates_if_exists(self):
        # Create first
        data = {
            "user_id": self.user.id,
            "company_id": self.company.id,
            "rate": 3.0
        }
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Update it
        data["rate"] = 4.0
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("updated successfully", response.data)

        # Company current_rate should be recalculated
        self.company.refresh_from_db()
        self.assertEqual(self.company.current_rate, 4.0)

    def test_get_company_rate_success(self):
        # Create rate
        CompanyRate.objects.create(user=self.user, company=self.company, rate=3.5)
        
        response = self.client.get(f"{self.get_rate_url}?user_id={self.user.id}&company_id={self.company.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["rate"], 3.5)
        self.assertEqual(response.data["user_id"], self.user.id)
        self.assertEqual(response.data["company_id"], self.company.id)

    def test_get_company_rate_not_found(self):
        # No rate exists yet
        response = self.client.get(f"{self.get_rate_url}?user_id={self.user.id}&company_id={self.company.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error']['type'], 'NotFoundError')

    def test_update_company_rate_out_of_range(self):
        data = {
            "user_id": self.user.id,
            "company_id": self.company.id,
            "rate": 5.0  # Max validator is 4.0
        }
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        data["rate"] = 0.5  # Min validator is 1.0
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_company_rate_company_not_found(self):
        data = {
            "user_id": self.user.id,
            "company_id": 9999,
            "rate": 3.0
        }
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error']['type'], 'NotFoundError')

    def test_update_company_rate_user_not_found(self):
        data = {
            "user_id": 9999,
            "company_id": self.company.id,
            "rate": 3.0
        }
        response = self.client.post(self.update_rate_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error']['type'], 'NotFoundError')

