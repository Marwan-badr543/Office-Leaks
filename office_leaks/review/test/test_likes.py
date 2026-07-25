from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from company.db.models import Company
from review.db.models import (
    Post, PostComment, PostNestedComment,
    Review, ReviewComment, ReviewNestedComment
)

User = get_user_model()


class LikesTests(APITestCase):

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

        # Create Post and Comment data
        self.post = Post.objects.create(
            content="Test post content",
            user=self.creator,
            company=self.company
        )
        self.post_comment = PostComment.objects.create(
            comment="Post parent comment",
            user=self.user,
            post=self.post
        )
        self.post_nested_comment = PostNestedComment.objects.create(
            comment_title="Post nested comment title",
            parent_comment=self.post_comment,
            user=self.user,
            parent_comment_author=self.user
        )

        # Create Review and Comment data
        self.review = Review.objects.create(
            review="Test review",
            user=self.creator,
            company=self.company
        )
        self.review_comment = ReviewComment.objects.create(
            comment="Review parent comment",
            user=self.user,
            review=self.review
        )
        self.review_nested_comment = ReviewNestedComment.objects.create(
            comment_title="Review nested comment title",
            parent_comment=self.review_comment,
            user=self.user,
            parent_comment_author=self.user
        )

        # Clear Redis buffers in setUp to prevent cross-test leakage
        from core.redis_client import get_redis_client
        r = get_redis_client()
        r.delete('global_post_likes_buffer')
        r.delete('global_post_comment_likes_buffer')
        r.delete('global_post_nested_comment_likes_buffer')
        r.delete('global_review_likes_buffer')
        r.delete('global_review_comment_likes_buffer')
        r.delete('global_review_nested_comment_likes_buffer')

    # 1. POST LIKES
    def test_post_like_flow(self):
        self.assertEqual(self.post.likes_number, 0)
        url = reverse('create-post-like')
        data = {"user_id": self.user.id, "post_id": self.post.id}

        # Like
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Flush
        from review.services.post_like import PostLikeServices
        PostLikeServices.flush_likes_to_db()

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_number, 1)

        # Unlike
        delete_url = reverse('delete-post-like', kwargs={'post_id': self.post.id})
        delete_data = {"user_id": self.user.id}
        response = self.client.delete(delete_url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertEqual(self.post.likes_number, 0)

    # 2. POST COMMENT LIKES
    def test_post_comment_like_flow(self):
        self.assertEqual(self.post_comment.likes_number, 0)
        url = reverse('create-post-comment-like')
        data = {"user_id": self.user.id, "post_comment_id": self.post_comment.id}

        # Like
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Flush
        from review.services.post_comment_like import PostCommentLikeServices
        PostCommentLikeServices.flush_likes_to_db()

        self.post_comment.refresh_from_db()
        self.assertEqual(self.post_comment.likes_number, 1)

        # Unlike
        delete_url = reverse('delete-post-comment-like', kwargs={'post_comment_id': self.post_comment.id})
        delete_data = {"user_id": self.user.id}
        response = self.client.delete(delete_url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post_comment.refresh_from_db()
        self.assertEqual(self.post_comment.likes_number, 0)

    # 3. POST NESTED COMMENT LIKES
    def test_post_nested_comment_like_flow(self):
        self.assertEqual(self.post_nested_comment.likes_number, 0)
        url = reverse('create-post-nested-comment-like')
        data = {"user_id": self.user.id, "post_nested_comment_id": self.post_nested_comment.id}

        # Like
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Flush
        from review.services.post_nested_comment_like import PostNestedCommentLikeServices
        PostNestedCommentLikeServices.flush_likes_to_db()

        self.post_nested_comment.refresh_from_db()
        self.assertEqual(self.post_nested_comment.likes_number, 1)

        # Unlike
        delete_url = reverse('delete-post-nested-comment-like', kwargs={'post_nested_comment_id': self.post_nested_comment.id})
        delete_data = {"user_id": self.user.id}
        response = self.client.delete(delete_url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post_nested_comment.refresh_from_db()
        self.assertEqual(self.post_nested_comment.likes_number, 0)

    # 4. REVIEW LIKES
    def test_review_like_flow(self):
        self.assertEqual(self.review.likes_number, 0)
        url = reverse('create-review-like')
        data = {"user_id": self.user.id, "review_id": self.review.id}

        # Like
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Flush
        from review.services.review_like import ReviewLikeServices
        ReviewLikeServices.flush_likes_to_db()

        self.review.refresh_from_db()
        self.assertEqual(self.review.likes_number, 1)

        # Unlike
        delete_url = reverse('delete-review-like', kwargs={'review_id': self.review.id})
        delete_data = {"user_id": self.user.id}
        response = self.client.delete(delete_url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review.refresh_from_db()
        self.assertEqual(self.review.likes_number, 0)

    # 5. REVIEW COMMENT LIKES
    def test_review_comment_like_flow(self):
        self.assertEqual(self.review_comment.likes_number, 0)
        url = reverse('create-review-comment-like')
        data = {"user_id": self.user.id, "review_comment_id": self.review_comment.id}

        # Like
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Flush
        from review.services.review_comment_like import ReviewCommentLikeServices
        ReviewCommentLikeServices.flush_likes_to_db()

        self.review_comment.refresh_from_db()
        self.assertEqual(self.review_comment.likes_number, 1)

        # Unlike
        delete_url = reverse('delete-review-comment-like', kwargs={'review_comment_id': self.review_comment.id})
        delete_data = {"user_id": self.user.id}
        response = self.client.delete(delete_url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review_comment.refresh_from_db()
        self.assertEqual(self.review_comment.likes_number, 0)

    # 6. REVIEW NESTED COMMENT LIKES
    def test_review_nested_comment_like_flow(self):
        self.assertEqual(self.review_nested_comment.likes_number, 0)
        url = reverse('create-review-nested-comment-like')
        data = {"user_id": self.user.id, "review_nested_comment_id": self.review_nested_comment.id}

        # Like
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Duplicate
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

        # Flush
        from review.services.review_nested_comment_like import ReviewNestedCommentLikeServices
        ReviewNestedCommentLikeServices.flush_likes_to_db()

        self.review_nested_comment.refresh_from_db()
        self.assertEqual(self.review_nested_comment.likes_number, 1)

        # Unlike
        delete_url = reverse('delete-review-nested-comment-like', kwargs={'review_nested_comment_id': self.review_nested_comment.id})
        delete_data = {"user_id": self.user.id}
        response = self.client.delete(delete_url, delete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.review_nested_comment.refresh_from_db()
        self.assertEqual(self.review_nested_comment.likes_number, 0)

    def test_has_liked_and_counts_decorations(self):
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Let's perform likes on all entities via API (which buffers in Redis)
        # 1. Post
        self.client.post(reverse('create-post-like'), {"user_id": self.user.id, "post_id": self.post.id}, format='json')
        # 2. Post comment
        self.client.post(reverse('create-post-comment-like'), {"user_id": self.user.id, "post_comment_id": self.post_comment.id}, format='json')
        # 3. Post nested comment
        self.client.post(reverse('create-post-nested-comment-like'), {"user_id": self.user.id, "post_nested_comment_id": self.post_nested_comment.id}, format='json')
        # 4. Review comment
        self.client.post(reverse('create-review-comment-like'), {"user_id": self.user.id, "review_comment_id": self.review_comment.id}, format='json')
        # 5. Review nested comment
        self.client.post(reverse('create-review-nested-comment-like'), {"user_id": self.user.id, "review_nested_comment_id": self.review_nested_comment.id}, format='json')

        # Now GET them and verify has_liked is True, and likes count is 1 (due to Redis buffer adjustment)
        # 1. Post
        response = self.client.get(reverse('get-post-by-id', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['has_liked'])
        self.assertEqual(response.data['likes_number'], 1)

        # 2. Post comments
        response = self.client.get(reverse('get-comments-by-post'), {"post_id": self.post.id, "page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment_data = response.data['comments'][0]
        self.assertTrue(comment_data['has_liked'])
        self.assertEqual(comment_data['likes_number'], 1)

        # 3. Post nested comments
        response = self.client.get(reverse('get-post-nested-comments-by-parent'), {"parent_comment_id": self.post_comment.id, "page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nested_data = response.data['comments'][0]
        self.assertTrue(nested_data['has_liked'])
        self.assertEqual(nested_data['likes_number'], 1)

        # 4. Review comments
        response = self.client.get(reverse('get-comments-by-review'), {"review_id": self.review.id, "page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rev_comment_data = response.data['comments'][0]
        self.assertTrue(rev_comment_data['has_liked'])
        self.assertEqual(rev_comment_data['likes_number'], 1)

        # 5. Review nested comments
        response = self.client.get(reverse('get-review-nested-comments-by-parent'), {"parent_comment_id": self.review_comment.id, "page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rev_nested_data = response.data['comments'][0]
        self.assertTrue(rev_nested_data['has_liked'])
        self.assertEqual(rev_nested_data['likes_number'], 1)

        # Now test with another user who has NOT liked anything
        other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="otherpassword",
            age=22,
            country="USA"
        )
        self.client.force_authenticate(user=other_user)

        # 1. Post
        response = self.client.get(reverse('get-post-by-id', kwargs={'post_id': self.post.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['has_liked'])
        self.assertEqual(response.data['likes_number'], 1)

        # 2. Post comments
        response = self.client.get(reverse('get-comments-by-post'), {"post_id": self.post.id, "page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment_data = response.data['comments'][0]
        self.assertFalse(comment_data['has_liked'])
        self.assertEqual(comment_data['likes_number'], 1)
