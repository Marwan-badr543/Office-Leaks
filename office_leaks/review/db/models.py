from django.db import models
from django.utils import timezone

class Review(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    review = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    likes_number = models.IntegerField(default=0)
    comments_number = models.IntegerField(default=0)

    # relationships
    # Author of the review (FK to user app, lazy string to avoid circular import)
    user = models.ForeignKey( 
        'user.User',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    # The company this review is about (one Company -> many Reviews)
    company = models.ForeignKey( 
        'company.Company',
        on_delete=models.CASCADE,
        related_name='reviews',
    )


class Post(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True, null=True)
    likes_number = models.IntegerField(default=0)
    comments_number = models.IntegerField(default=0)

    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='posts',
    )

    review = models.ForeignKey(
        'review.Review',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review'],
                name='uniq_user_review_post',
            ),
        ]


class ReviewComment(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    likes_number = models.IntegerField(default=0)

    # relationships
    # Author of the comment (FK to user app, lazy string to avoid circular import)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_comments',
    )
    # The review this comment belongs to (one Review -> many Comments)
    review = models.ForeignKey(
        'review.Review',
        on_delete=models.CASCADE,
        related_name='review_comments',
    )
    

class PostComment(models.Model):
    creation = models.DateTimeField(default=timezone.now)
    comment = models.TextField()
    likes_number = models.IntegerField(default=0)

    # relationships
    # Author of the comment (FK to user app, lazy string to avoid circular import)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_comments',
    )
    # The post this comment belongs to (one Post -> many Comments)
    post = models.ForeignKey(
        'review.Post',
        on_delete=models.CASCADE,
        related_name='post_comments',
    )



class ReviewLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    # relationships
    # User who liked (FK to user app, lazy string to avoid circular import)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='review_likes',
    )
    # The review that was liked (one Review -> many Likes)
    review = models.ForeignKey(
        'review.Review',
        on_delete=models.CASCADE,
        related_name='review_likes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review'],
                name='uniq_user_review_like',
            ),
        ]



class ReviewCommentLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    # relationships
    # User who liked (FK to user app, lazy string to avoid circular import)
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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'review_comment'],
                name='uniq_user_review_comment_like',
            ),
        ]


class PostLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    # relationships
    # User who liked (FK to user app, lazy string to avoid circular import)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_likes',
    )
    # The post that was liked (one Post -> many Likes)
    post = models.ForeignKey(
        'review.Post',
        on_delete=models.CASCADE,
        related_name='post_likes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='uniq_user_post_like',
            ),
        ]


class PostCommentLike(models.Model):
    creation = models.DateTimeField(default=timezone.now)

    # relationships
    # User who liked (FK to user app, lazy string to avoid circular import)
    user = models.ForeignKey(
        'user.User',
        on_delete=models.CASCADE,
        related_name='post_comment_likes',
    )
    # The post comment that was liked
    post_comment = models.ForeignKey(
        'review.PostComment',
        on_delete=models.CASCADE,
        related_name='post_comment_likes',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post_comment'],
                name='uniq_user_post_comment_like',
            ),
        ]


