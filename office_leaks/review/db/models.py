from django.db import models
from django.utils import timezone

class Review(models.Model):
    creation = models.DateTimeField(default=timezone.now, db_index=True)
    review = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    likes_number = models.IntegerField(default=0)
    comments_number = models.IntegerField(default=0)

    user = models.ForeignKey( 
        'user.User',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    company = models.ForeignKey( 
        'company.Company',
        on_delete=models.CASCADE,
        related_name='reviews',
    )


class PostCategory(models.TextChoices):
    SALARIES = 'SALARIES'
    CULTURE = 'CULTURE'
    MANAGEMENT = 'MANAGEMENT'
    POLICIES = 'POLICIES'
    GROWTH = 'GROWTH'
    INTERVIEWS = 'INTERVIEWS'
    ISSUES = 'ISSUES'
    OTHER = 'OTHER'

class Post(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True, null=True)
    is_anonymous = models.BooleanField(default=False)
    likes_number = models.IntegerField(default=0)
    comments_number = models.IntegerField(default=0)
    popularity_score = models.IntegerField(default=0)

    category = models.CharField(
            max_length=20,
            choices=PostCategory.choices,
            blank=True,
            null=True,
        )

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='posts',
    )

    company = models.ForeignKey(
        'company.Company',
        on_delete=models.CASCADE,
        related_name='posts',
        blank=True,
        null=True
    )

    review = models.ForeignKey(
        'review.Review',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )

    parent_post = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='reposts',
        blank=True,
        null=True
    )

    class Meta:
        indexes = [
            models.Index(fields=['-creation'], name='post_creation_idx'),
            models.Index(fields=['-popularity_score', '-creation'], name='post_pop_creation_idx'),
            models.Index(fields=['user'], name='post_user_idx'),
            models.Index(fields=['category'], name='post_category_idx'),
        ]


class ReviewComment(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    likes_number = models.IntegerField(default=0)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_comments',
    )
    review = models.ForeignKey(
        'review.Review',
        on_delete=models.CASCADE,
        related_name='review_comments',
    )

    class Meta:
        indexes = [
            models.Index(fields=['review'], name='reviewcomment_review_idx'),
        ]
    

class PostComment(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    likes_number = models.IntegerField(default=0)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_comments',
    )
    post = models.ForeignKey(
        'review.Post',
        on_delete=models.CASCADE,
        related_name='post_comments',
    )

    class Meta:
        indexes = [
            models.Index(fields=['post'], name='postcomment_post_idx'),
        ]


class ReviewNestedComment(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    comment_title = models.CharField(max_length=255)
    likes_number = models.IntegerField(default=0)

    parent_comment = models.ForeignKey(
        'review.ReviewComment',
        on_delete=models.CASCADE,
        related_name='nested_comments',
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_nested_comments',
    )
    parent_comment_author = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name='review_parent_nested_comments',
        null=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['parent_comment'], name='revnested_parent_idx'),
        ]


class PostNestedComment(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    comment_title = models.CharField(max_length=255)
    likes_number = models.IntegerField(default=0)

    parent_comment = models.ForeignKey(
        'review.PostComment',
        on_delete=models.CASCADE,
        related_name='nested_comments',
    )
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_nested_comments',
    )
    parent_comment_author = models.ForeignKey(
        'user.User',
        on_delete=models.SET_NULL,
        related_name='post_parent_nested_comments',
        null=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=['parent_comment'], name='postnested_parent_idx'),
        ]



class ReviewLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_likes',
    )
    review = models.ForeignKey(
        'review.Review',
        on_delete=models.CASCADE,
        related_name='review_likes',
    )



class ReviewCommentLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_comment_likes',
    )

    review_comment = models.ForeignKey(
        'review.ReviewComment',
        on_delete=models.CASCADE,
        related_name='review_comment_likes',
    )



class ReviewNestedCommentLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_nested_comment_likes',
    )
    review_nested_comment = models.ForeignKey(
        'review.ReviewNestedComment',
        on_delete=models.CASCADE,
        related_name='review_nested_comment_likes',
    )



class PostLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_likes',
    )
    post = models.ForeignKey(
        'review.Post',
        on_delete=models.CASCADE,
        related_name='post_likes',
    )


class PostCommentLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_comment_likes',
    )
    post_comment = models.ForeignKey(
        'review.PostComment',
        on_delete=models.CASCADE,
        related_name='post_comment_likes',
    )


class PostNestedCommentLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_nested_comment_likes',
    )
    post_nested_comment = models.ForeignKey(
        'review.PostNestedComment',
        on_delete=models.CASCADE,
        related_name='post_nested_comment_likes',
    )


