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
        
        self.update_rate_url = reverse('create-company-rate')
        self.get_rate_url = reverse('get-company-rate')
        self.client.force_authenticate(user=self.user)

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


from company.tasks import update_top_rated_companies, REDIS_KEY_TOP_RATED
from core.redis_client import get_redis_client
import json

class CompanyTasksTests(APITestCase):

    def setUp(self):
        # Create a test user for company creator
        self.creator = User.objects.create_user(
            username="task_creator",
            email="task_creator@example.com",
            password="creatorpassword",
            age=30,
            country="USA",
            first_name="Task",
            last_name="Creator"
        )
        
        # Clean up Redis key before each test
        self.redis_client = get_redis_client()
        self.redis_client.delete(REDIS_KEY_TOP_RATED)

    def tearDown(self):
        # Clean up Redis key after each test
        self.redis_client.delete(REDIS_KEY_TOP_RATED)

    def test_update_top_rated_companies_task(self):
        # Create 12 companies with different ratings to verify sorting and limit of 10
        companies = []
        for i in range(12):
            company = Company.objects.create(
                name=f"Company {i}",
                address=f"Address {i}",
                industry="Software",
                user=self.creator,
                current_rate=float(i)  # ratings from 0.0 to 11.0
            )
            companies.append(company)
            
        # Run the task directly
        result_count = update_top_rated_companies.call_local()
        self.assertEqual(result_count, 10)
        
        # Verify the Redis cache content
        cached_data = self.redis_client.get(REDIS_KEY_TOP_RATED)
        self.assertIsNotNone(cached_data)
        
        cached_list = json.loads(cached_data)
        self.assertEqual(len(cached_list), 10)
        
        # Verify companies are sorted by rating descending (11.0 down to 2.0)
        for idx, cached_company in enumerate(cached_list):
            expected_rate = float(11 - idx)
            self.assertEqual(cached_company['current_rate'], expected_rate)
            self.assertEqual(cached_company['name'], f"Company {11 - idx}")
            self.assertIn('id', cached_company)
            self.assertIn('creation', cached_company)
            self.assertIn('industry', cached_company)
            self.assertIn('logo', cached_company)

    def test_update_top_rated_companies_clears_old_data(self):
        # Seed dummy old data in Redis
        self.redis_client.set(REDIS_KEY_TOP_RATED, "old_stale_data")
        
        # Create one company
        Company.objects.create(
            name="Only Company",
            address="Only Address",
            industry="Hardware",
            user=self.creator,
            current_rate=4.0
        )
        
        # Run the task
        update_top_rated_companies.call_local()
        
        # Verify old data is gone and new data is loaded
        cached_data = self.redis_client.get(REDIS_KEY_TOP_RATED)
        cached_list = json.loads(cached_data)
        self.assertEqual(len(cached_list), 1)
        self.assertEqual(cached_list[0]['name'], "Only Company")


class CompanyViewCachingTests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            username="view_creator",
            email="view_creator@example.com",
            password="creatorpassword",
            age=30,
            country="USA",
            first_name="View",
            last_name="Creator"
        )
        self.redis_client = get_redis_client()
        self.redis_client.delete(REDIS_KEY_TOP_RATED)
        self.url = reverse('get-companies')

    def tearDown(self):
        self.redis_client.delete(REDIS_KEY_TOP_RATED)

    def test_get_companies_page_1_gets_from_redis(self):
        # Create 12 companies
        for i in range(12):
            Company.objects.create(
                name=f"Company {i}",
                address=f"Address {i}",
                industry="Software",
                user=self.creator,
                current_rate=float(i)
            )

        # Run task to cache top 10 companies
        update_top_rated_companies.call_local()

        # Delete all companies in DB to prove we're hitting Redis
        Company.objects.all().delete()

        response = self.client.get(self.url, {"page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        companies_returned = response.data["companies"]
        self.assertEqual(len(companies_returned), 10)
        # It should return the names from Redis cache ("Company 11", etc.), not DB "Database Name"
        self.assertEqual(companies_returned[0]["name"], "Company 11")

    def test_get_companies_page_2_gets_from_db(self):
        # Create 12 companies
        for i in range(12):
            Company.objects.create(
                name=f"Company {i}",
                address=f"Address {i}",
                industry="Software",
                user=self.creator,
                current_rate=float(i)
            )

        update_top_rated_companies.call_local()

        # Page 2 should bypass Redis and get remaining 2 companies from DB (ordered by current_rate desc)
        # DB has ratings from 0 to 11. Sorted desc:
        # Page 1: 11 down to 2
        # Page 2: 1 and 0 (Company 1 and Company 0)
        response = self.client.get(self.url, {"page": 2, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        companies_returned = response.data["companies"]
        self.assertEqual(len(companies_returned), 2)
        # Since it hits DB, the names will match the DB values
        self.assertEqual(companies_returned[0]["name"], "Company 1")
        self.assertEqual(companies_returned[1]["name"], "Company 0")

    def test_get_companies_with_filter_bypasses_redis(self):
        # Create 12 companies
        for i in range(12):
            Company.objects.create(
                name=f"Company {i}",
                address=f"Address {i}",
                industry="Software",
                user=self.creator,
                current_rate=float(i)
            )

        update_top_rated_companies.call_local()

        # Filtering should bypass Redis cache even on page 1
        response = self.client.get(self.url, {"page": 1, "page_size": 10, "name_search": "Company 5"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        companies_returned = response.data["companies"]
        self.assertEqual(len(companies_returned), 1)
        self.assertEqual(companies_returned[0]["name"], "Company 5")

    def test_get_companies_falls_back_to_db_on_empty_redis(self):
        # Create 12 companies in DB, Redis is empty
        for i in range(12):
            Company.objects.create(
                name=f"Company {i}",
                address=f"Address {i}",
                industry="Software",
                user=self.creator,
                current_rate=float(i)
            )

        response = self.client.get(self.url, {"page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        companies_returned = response.data["companies"]
        self.assertEqual(len(companies_returned), 10)
        # Should return top 10 from DB
        self.assertEqual(companies_returned[0]["name"], "Company 11")



