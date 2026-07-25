from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from company.db.models import Company
from review.db.models import Review, ReviewComment, ReviewNestedComment

User = get_user_model()


class ReviewTests(APITestCase):

    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword",
            age=25,
            country="USA",
            first_name="Test",
            last_name="User"
        )
        self.creator = User.objects.create_user(
            username="creator",
            email="creator@example.com",
            password="creatorpassword",
            age=30,
            country="USA",
            first_name="Post",
            last_name="Creator"
        )
        self.client.force_authenticate(user=self.user)

        # Create a company
        self.company = Company.objects.create(
            name="Test Company",
            address="123 Test St",
            industry="Software",
            user=self.creator
        )

        # Create a review
        self.review = Review.objects.create(
            review="Excellent company review text",
            user=self.creator,
            company=self.company
        )

        # Create a comment
        self.comment = ReviewComment.objects.create(
            comment="This is a test comment on the review",
            user=self.user,
            review=self.review
        )

        # Create a nested comment
        self.nested_comment = ReviewNestedComment.objects.create(
            comment_title="Nested comment reply",
            parent_comment=self.comment,
            user=self.user,
            parent_comment_author=self.user
        )

    def test_create_review_success(self):
        url = reverse('create-review')
        data = {
            "review": "Another review text",
            "company_id": self.company.id,
            "user_id": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.filter(review="Another review text").count(), 1)

    def test_update_review(self):
        url = reverse('update-review', kwargs={'review_id': self.review.id})
        data = {
            "review": "Updated review text",
            "company_id": self.company.id,
            "user_id": self.creator.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review.refresh_from_db()
        self.assertEqual(self.review.review, "Updated review text")

    def test_get_review_by_id(self):
        url = reverse('get-review-by-id', kwargs={'review_id': self.review.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['review'], self.review.review)

    def test_get_reviews_by_company(self):
        url = reverse('get-reviews-by-company')
        response = self.client.get(f"{url}?company_id={self.company.id}&page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data['reviews']) >= 1)

    def test_delete_review(self):
        url = reverse('delete-review', kwargs={'review_id': self.review.id})
        data = {"user_id": self.creator.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())

    # Review Comments
    def test_create_review_comment(self):
        url = reverse('create-comment')
        data = {
            "comment": "Nice review!",
            "review_id": self.review.id,
            "user_id": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_review_comment(self):
        url = reverse('update-comment', kwargs={'comment_id': self.comment.id})
        data = {
            "comment": "Nice review, updated comment",
            "review_id": self.review.id,
            "user_id": self.user.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_by_review(self):
        url = reverse('get-comments-by-review')
        response = self.client.get(f"{url}?review_id={self.review.id}&page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_review_comment(self):
        url = reverse('delete-comment', kwargs={'comment_id': self.comment.id})
        data = {"user_id": self.user.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Review Nested Comments
    def test_create_review_nested_comment(self):
        url = reverse('create-review-nested-comment')
        data = {
            "comment_title": "Reply to reply",
            "parent_comment_id": self.comment.id,
            "user_id": self.user.id,
            "parent_comment_author_id": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_review_nested_comment(self):
        url = reverse('update-review-nested-comment', kwargs={'comment_id': self.nested_comment.id})
        data = {
            "comment_title": "Reply to reply updated",
            "parent_comment_id": self.comment.id,
            "user_id": self.user.id,
            "parent_comment_author_id": self.user.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_review_nested_comments_by_parent(self):
        url = reverse('get-review-nested-comments-by-parent')
        response = self.client.get(f"{url}?parent_comment_id={self.comment.id}&page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_review_nested_comment(self):
        url = reverse('delete-review-nested-comment', kwargs={'comment_id': self.nested_comment.id})
        data = {"user_id": self.user.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
