from django.contrib import admin
from .db.models import Review, ReviewComment, ReviewLike, ReviewCommentLike, Post, PostComment, PostLike, PostCommentLike


admin.site.register(Review)
admin.site.register(ReviewLike)
admin.site.register(ReviewComment)
admin.site.register(ReviewCommentLike)

admin.site.register(Post)
admin.site.register(PostLike)
admin.site.register(PostComment)
admin.site.register(PostCommentLike)