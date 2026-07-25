from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from company.db.models import Company
from review.db.models import Post, PostComment, PostNestedComment

User = get_user_model()


class PostTests(APITestCase):

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

        # Create a post
        self.post = Post.objects.create(
            content="Initial post content text",
            user=self.creator,
            company=self.company
        )

        # Create a comment
        self.comment = PostComment.objects.create(
            comment="This is a test comment on the post",
            user=self.user,
            post=self.post
        )

        # Create a nested comment
        self.nested_comment = PostNestedComment.objects.create(
            comment_title="Nested post comment reply",
            parent_comment=self.comment,
            user=self.user,
            parent_comment_author=self.user
        )

    def test_create_post_success(self):
        url = reverse('create-post')
        data = {
            "content": "A brand new post content",
            "company_id": self.company.id,
            "user_id": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.filter(content="A brand new post content").count(), 1)

    def test_update_post(self):
        url = reverse('update-post', kwargs={'post_id': self.post.id})
        data = {
            "content": "Updated post content",
            "company_id": self.company.id,
            "user_id": self.creator.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.content, "Updated post content")

    def test_get_posts(self):
        url = reverse('get-posts')
        response = self.client.get(f"{url}?page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_by_id(self):
        url = reverse('get-post-by-id', kwargs={'post_id': self.post.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], self.post.content)

    def test_get_posts_by_user_success(self):
        url = reverse('get-posts-by-user', kwargs={'user_id': self.creator.id})
        response = self.client.get(f"{url}?page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["posts"]), 1)
        self.assertEqual(response.data["posts"][0]["id"], self.post.id)

    def test_get_posts_by_user_not_found(self):
        url = reverse('get-posts-by-user', kwargs={'user_id': 9999})
        response = self.client.get(f"{url}?page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_post(self):
        url = reverse('delete-post', kwargs={'post_id': self.post.id})
        data = {"user_id": self.creator.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    # Post Comments
    def test_create_post_comment(self):
        url = reverse('create-post-comment')
        data = {
            "comment": "Nice post!",
            "post_id": self.post.id,
            "user_id": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_post_comment(self):
        url = reverse('update-post-comment', kwargs={'comment_id': self.comment.id})
        data = {
            "comment": "Nice post, updated comment",
            "post_id": self.post.id,
            "user_id": self.user.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_comments_by_post(self):
        url = reverse('get-comments-by-post')
        response = self.client.get(f"{url}?post_id={self.post.id}&page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_post_comment(self):
        url = reverse('delete-post-comment', kwargs={'comment_id': self.comment.id})
        data = {"user_id": self.user.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # Post Nested Comments
    def test_create_post_nested_comment(self):
        url = reverse('create-post-nested-comment')
        data = {
            "comment_title": "Reply to post comment",
            "parent_comment_id": self.comment.id,
            "user_id": self.user.id,
            "parent_comment_author_id": self.user.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_post_nested_comment(self):
        url = reverse('update-post-nested-comment', kwargs={'comment_id': self.nested_comment.id})
        data = {
            "comment_title": "Reply to post comment updated",
            "parent_comment_id": self.comment.id,
            "user_id": self.user.id,
            "parent_comment_author_id": self.user.id
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_post_nested_comments_by_parent(self):
        url = reverse('get-post-nested-comments-by-parent')
        response = self.client.get(f"{url}?parent_comment_id={self.comment.id}&page=1&page_size=10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_post_nested_comment(self):
        url = reverse('delete-post-nested-comment', kwargs={'comment_id': self.nested_comment.id})
        data = {"user_id": self.user.id}
        response = self.client.delete(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


from review.tasks import update_trending_categories_task, REDIS_KEY_TRENDING_CATEGORIES
from core.redis_client import get_redis_client
import json
from django.utils import timezone
from datetime import timedelta

class TrendingCategoriesTasksTests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            username="trending_creator",
            email="trending_creator@example.com",
            password="creatorpassword",
            age=30,
            country="USA",
            first_name="Trending",
            last_name="Creator"
        )
        self.redis_client = get_redis_client()
        self.redis_client.delete(REDIS_KEY_TRENDING_CATEGORIES)

    def tearDown(self):
        self.redis_client.delete(REDIS_KEY_TRENDING_CATEGORIES)

    def test_update_trending_categories_task(self):
        # Create categories count to rank them:
        # SALARIES: 5, CULTURE: 4, MANAGEMENT: 3, POLICIES: 2, GROWTH: 1, INTERVIEWS: 1
        # Ignore: old SALARIES (created 8 days ago) - count shouldn't include it.
        
        # 1. Old Salaries post
        Post.objects.create(
            content="Old salary post",
            user=self.creator,
            category="SALARIES",
            creation=timezone.now() - timedelta(days=8)
        )
        
        # 2. Category creation for past week
        categories_data = [
            ("SALARIES", 5),
            ("CULTURE", 4),
            ("MANAGEMENT", 3),
            ("POLICIES", 2),
            ("GROWTH", 1),
            ("INTERVIEWS", 1),
        ]
        
        for category, count in categories_data:
            for i in range(count):
                Post.objects.create(
                    content=f"Post {i} for {category}",
                    user=self.creator,
                    category=category,
                    creation=timezone.now() - timedelta(days=1)
                )

        # Run task
        result = update_trending_categories_task.call_local()
        self.assertEqual(result, 6)
        
        # Check Redis payload
        cached_data = self.redis_client.get(REDIS_KEY_TRENDING_CATEGORIES)
        self.assertIsNotNone(cached_data)
        
        cached_list = json.loads(cached_data)
        self.assertEqual(len(cached_list), 6)
        
        # Check ordering (SALARIES count 5, CULTURE count 4, etc.)
        self.assertEqual(cached_list[0]["category"], "SALARIES")
        self.assertEqual(cached_list[0]["count"], 5)
        
        self.assertEqual(cached_list[1]["category"], "CULTURE")
        self.assertEqual(cached_list[1]["count"], 4)
        
        self.assertEqual(cached_list[2]["category"], "MANAGEMENT")
        self.assertEqual(cached_list[2]["count"], 3)

    def test_get_trending_topics_endpoint_from_redis(self):
        # Create categories count to rank them:
        # SALARIES: 5, CULTURE: 4
        categories_data = [
            ("SALARIES", 5),
            ("CULTURE", 4),
        ]
        for category, count in categories_data:
            for i in range(count):
                Post.objects.create(
                    content=f"Post {i} for {category}",
                    user=self.creator,
                    category=category,
                    creation=timezone.now() - timedelta(days=1)
                )

        update_trending_categories_task.call_local()

        # Delete from DB to prove we read from Redis
        Post.objects.all().delete()

        url = reverse('get-trending-topics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["category"], "SALARIES")
        self.assertEqual(data[0]["count"], 5)

    def test_get_trending_topics_endpoint_falls_back_to_db_on_empty_redis(self):
        # Create categories count to rank them:
        # SALARIES: 5
        for i in range(5):
            Post.objects.create(
                content=f"Post {i} for SALARIES",
                user=self.creator,
                category="SALARIES",
                creation=timezone.now() - timedelta(days=1)
            )

        # Redis is empty. The endpoint should query DB directly
        url = reverse('get-trending-topics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["category"], "SALARIES")
        self.assertEqual(data[0]["count"], 5)


from review.tasks import update_feeds_posts_cache_task

class FeedsPostsCachingTests(APITestCase):

    def setUp(self):
        self.creator = User.objects.create_user(
            username="feeds_creator",
            email="feeds_creator@example.com",
            password="creatorpassword",
            age=30,
            country="USA",
            first_name="Feeds",
            last_name="Creator"
        )
        self.company = Company.objects.create(
            name="Feeds Company",
            address="123 Main St",
            industry="Software",
            user=self.creator
        )
        self.redis_client = get_redis_client()
        self.redis_key = "post:feeds:recent"
        self.redis_client.delete(self.redis_key)

    def tearDown(self):
        self.redis_client.delete(self.redis_key)

    def test_create_and_delete_post_updates_feeds_cache(self):
        from review.services.post import PostServices

        # 1. Create a post
        post = PostServices.create_post({
            "content": "Test feeds post 1",
            "user_id": self.creator.id,
            "company_id": self.company.id
        })

        # Run task to populate Redis cache
        update_feeds_posts_cache_task.call_local()

        # Verify Redis has the post
        cached_data = self.redis_client.get(self.redis_key)
        self.assertIsNotNone(cached_data)
        cached_list = json.loads(cached_data)
        self.assertEqual(len(cached_list), 1)
        self.assertEqual(cached_list[0]["content"], "Test feeds post 1")

        # Now get the first page of posts via API
        url = reverse('get-posts')
        # Delete from DB to ensure it is fetched from Redis
        Post.objects.all().delete()

        response = self.client.get(url, {"page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["posts"]), 1)
        self.assertEqual(response.data["posts"][0]["content"], "Test feeds post 1")

    def test_get_posts_page_2_retrieved_from_db(self):
        from review.services.post import PostServices

        # Create 12 posts
        for i in range(12):
            PostServices.create_post({
                "content": f"Post {i}",
                "user_id": self.creator.id,
                "company_id": self.company.id
            })

        update_feeds_posts_cache_task.call_local()

        url = reverse('get-posts')
        
        # Request page 2 - should query DB, not cache
        response = self.client.get(url, {"page": 2, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Total posts is 12, page 2 with page_size=10 should return the remaining 2 posts
        self.assertEqual(len(response.data["posts"]), 2)



