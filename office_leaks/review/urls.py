# pyrefly: ignore [missing-import]
from django.urls import path
from .views import review as review_views
from .views import post as post_views
from .views import review_comment as comment_views
from .views import post_comment as post_comment_views
from .views import review_like as review_like_views
from .views import review_comment_like as review_comment_like_views
from .views import post_like as post_like_views
from .views import post_comment_like as post_comment_like_views
from .views import review_nested_comment as review_nested_comment_views
from .views import post_nested_comment as post_nested_comment_views
from .views import review_nested_comment_like as review_nested_comment_like_views
from .views import post_nested_comment_like as post_nested_comment_like_views

urlpatterns = [
    path('review/create/', review_views.create_review, name='create-review'),
    path('review/update/<int:review_id>/', review_views.update_review, name='update-review'),
    path('review/delete/<int:review_id>/', review_views.delete_review, name='delete-review'),
    path('review/<int:review_id>/', review_views.get_review_by_id, name='get-review-by-id'),
    path('review/', review_views.get_reviews_by_company, name='get-reviews-by-company'),

    path('review-comment/create/', comment_views.create_comment, name='create-comment'),
    path('review-comment/update/<int:comment_id>/', comment_views.update_comment, name='update-comment'),
    path('review-comment/delete/<int:comment_id>/', comment_views.delete_comment, name='delete-comment'),
    path('review-comment/', comment_views.get_comments_by_review, name='get-comments-by-review'),
    
    path('post/create/', post_views.create_post, name='create-post'),
    path('post/update/<int:post_id>/', post_views.update_post, name='update-post'),
    path('post/', post_views.get_posts, name='get-posts'),
    path('post/<int:post_id>/', post_views.get_post_by_id, name='get-post-by-id'),
    path('post/delete/<int:post_id>/', post_views.delete_post, name='delete-post'),
    path('post/user/<int:user_id>/', post_views.get_posts_by_user, name='get-posts-by-user'),
    path('post/trending/', post_views.get_trending_topics, name='get-trending-topics'),
    
    path('post-comment/create/', post_comment_views.create_comment, name='create-post-comment'),
    path('post-comment/update/<int:comment_id>/', post_comment_views.update_comment, name='update-post-comment'),
    path('post-comment/delete/<int:comment_id>/', post_comment_views.delete_comment, name='delete-post-comment'),
    path('post-comment/', post_comment_views.get_comments_by_post, name='get-comments-by-post'),

    # Like Endpoints
    path('review-like/create/', review_like_views.create_like, name='create-review-like'),
    path('review-like/delete/<int:review_id>/', review_like_views.delete_like, name='delete-review-like'),

    path('review-comment-like/create/', review_comment_like_views.create_like, name='create-review-comment-like'),
    path('review-comment-like/delete/<int:review_comment_id>/', review_comment_like_views.delete_like, name='delete-review-comment-like'),

    path('post-like/create/', post_like_views.create_like, name='create-post-like'),
    path('post-like/delete/<int:post_id>/', post_like_views.delete_like, name='delete-post-like'),

    path('post-comment-like/create/', post_comment_like_views.create_like, name='create-post-comment-like'),
    path('post-comment-like/delete/<int:post_comment_id>/', post_comment_like_views.delete_like, name='delete-post-comment-like'),

    # Review Nested Comment Endpoints
    path('review-nested-comment/create/', review_nested_comment_views.create_comment, name='create-review-nested-comment'),
    path('review-nested-comment/update/<int:comment_id>/', review_nested_comment_views.update_comment, name='update-review-nested-comment'),
    path('review-nested-comment/delete/<int:comment_id>/', review_nested_comment_views.delete_comment, name='delete-review-nested-comment'),
    path('review-nested-comment/', review_nested_comment_views.get_comments_by_parent, name='get-review-nested-comments-by-parent'),
    path('review-nested-comment-like/create/', review_nested_comment_like_views.create_like, name='create-review-nested-comment-like'),
    path('review-nested-comment-like/delete/<int:review_nested_comment_id>/', review_nested_comment_like_views.delete_like, name='delete-review-nested-comment-like'),

    # Post Nested Comment Endpoints
    path('post-nested-comment/create/', post_nested_comment_views.create_comment, name='create-post-nested-comment'),
    path('post-nested-comment/update/<int:comment_id>/', post_nested_comment_views.update_comment, name='update-post-nested-comment'),
    path('post-nested-comment/delete/<int:comment_id>/', post_nested_comment_views.delete_comment, name='delete-post-nested-comment'),
    path('post-nested-comment/', post_nested_comment_views.get_comments_by_parent, name='get-post-nested-comments-by-parent'),
    path('post-nested-comment-like/create/', post_nested_comment_like_views.create_like, name='create-post-nested-comment-like'),
    path('post-nested-comment-like/delete/<int:post_nested_comment_id>/', post_nested_comment_like_views.delete_like, name='delete-post-nested-comment-like'),

]