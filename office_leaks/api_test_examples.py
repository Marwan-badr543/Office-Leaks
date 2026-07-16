"""
=============================================================================
  API Testing Examples - Review App
  Base URL: http://localhost:8000/review/
=============================================================================

  This file contains example request dicts and paths
  for testing all CRUD endpoints across:
    1. Review
    2. Review Comment
    3. Post (content post & review post)
    4. Post Comment

  Use these with httpie, curl, Postman, or DRF's browsable API.
=============================================================================
"""


# =============================================================================
#  1. REVIEW
# =============================================================================

# --- Create Review ---
# POST /review/review/create/
create_review = {
    "user_id": 1,
    "company_id": 1,
    "review": "Great workplace culture with amazing benefits!",
    "is_anonymous": False
}

# --- Update Review ---
# PATCH /review/review/update/1/
# (user can only update the review text, and only their own review)
update_review = {
    "review": "Updated review - still a great company but management could improve.",
    "user_id": 1
}

# --- Get Reviews by Company ---
# GET /review/review/?company_id=1&page=1&page_size=10
get_reviews_by_company_params = {
    "company_id": 1,
    "page": 1,
    "page_size": 10
}

# --- Delete Review ---
# DELETE /review/review/delete/1/
delete_review = {
    "user_id": 1
}


# =============================================================================
#  2. REVIEW COMMENT
# =============================================================================

# --- Create Review Comment ---
# POST /review/review-comment/create/
create_review_comment = {
    "user_id": 1,
    "review_id": 1,
    "comment": "I totally agree with this review!"
}

# --- Update Review Comment ---
# PATCH /review/review-comment/update/1/
# (user can only update the comment text, and only their own comment)
update_review_comment = {
    "comment": "Updated - I mostly agree but have some reservations.",
    "user_id": 1
}

# --- Get Comments by Review ---
# GET /review/review-comment/?review_id=1&page=1&page_size=10
get_review_comments_params = {
    "review_id": 1,
    "page": 1,
    "page_size": 10
}

# --- Delete Review Comment ---
# DELETE /review/review-comment/delete/1/
delete_review_comment = {
    "user_id": 1
}


# =============================================================================
#  3. POST (two types: content post & review post)
# =============================================================================

# --- Create Content Post (user writes their own content) ---
# POST /review/post/create/
create_content_post = {
    "user_id": 1,
    "content": "Just finished my first week at the new job!"
}

# --- Create Review Post (user shares/reposts a review) ---
# POST /review/post/create/
# (can NOT send both content and review_id)
create_review_post = {
    "user_id": 1,
    "review_id": 1
}

# --- Update Post (only content posts can be updated) ---
# PATCH /review/post/update/1/
# (review posts will be rejected with "Review posts cannot be updated.")
update_post = {
    "content": "Updated - second week now and still loving it!",
    "user_id": 1
}

# --- Get Posts (Feed) ---
# GET /review/post/?page=1&page_size=10
# For review posts, the response nests the full review object.
# For content posts, review will be null.
get_posts_params = {
    "page": 1,
    "page_size": 10
}

# --- Delete Post ---
# DELETE /review/post/delete/1/
# (user can only delete their own post, works for both types)
delete_post = {
    "user_id": 1
}


# =============================================================================
#  4. POST COMMENT
# =============================================================================

# --- Create Post Comment ---
# POST /review/post-comment/create/
create_post_comment = {
    "user_id": 1,
    "post_id": 1,
    "comment": "Nice post, congrats on the new job!"
}

# --- Update Post Comment ---
# PATCH /review/post-comment/update/1/
# (user can only update the comment text, and only their own comment)
update_post_comment = {
    "comment": "Updated - hope you're still enjoying it!",
    "user_id": 1
}

# --- Get Comments by Post ---
# GET /review/post-comment/?post_id=1&page=1&page_size=10
get_post_comments_params = {
    "post_id": 1,
    "page": 1,
    "page_size": 10
}

# --- Delete Post Comment ---
# DELETE /review/post-comment/delete/1/
delete_post_comment = {
    "user_id": 1
}


# =============================================================================
#  CURL EXAMPLES
# =============================================================================
"""
# ---- REVIEW ----
curl -X POST http://localhost:8000/review/review/create/ -H "Content-Type: application/json" -d '{"user_id": 1, "company_id": 1, "review": "Great workplace!", "is_anonymous": false}'
curl -X PATCH http://localhost:8000/review/review/update/1/ -H "Content-Type: application/json" -d '{"review": "Updated review text", "user_id": 1}'
curl -X GET "http://localhost:8000/review/review/?company_id=1&page=1&page_size=10"
curl -X DELETE http://localhost:8000/review/review/delete/1/ -H "Content-Type: application/json" -d '{"user_id": 1}'

# ---- REVIEW COMMENT ----
curl -X POST http://localhost:8000/review/review-comment/create/ -H "Content-Type: application/json" -d '{"user_id": 1, "review_id": 2, "comment": "I agree!"}'
curl -X PATCH http://localhost:8000/review/review-comment/update/1/ -H "Content-Type: application/json" -d '{"comment": "Updated comment", "user_id": 1}'
curl -X GET "http://localhost:8000/review/review-comment/?review_id=2&page=1&page_size=10"
curl -X DELETE http://localhost:8000/review/review-comment/delete/1/ -H "Content-Type: application/json" -d '{"user_id": 1}'

# ---- POST (content post) ----
curl -X POST http://localhost:8000/review/post/create/ -H "Content-Type: application/json" -d '{"user_id": 1, "content": "My first post!"}'

# ---- POST (review post) ----
curl -X POST http://localhost:8000/review/post/create/ -H "Content-Type: application/json" -d '{"user_id": 1, "review_id": 2}'

# ---- POST update & feed & delete ----
curl -X PATCH http://localhost:8000/review/post/update/1/ -H "Content-Type: application/json" -d '{"content": "Updated post", "user_id": 1}'
curl -X GET "http://localhost:8000/review/post/?page=1&page_size=10"
curl -X DELETE http://localhost:8000/review/post/delete/1/ -H "Content-Type: application/json" -d '{"user_id": 1}'

# ---- POST COMMENT ----
curl -X POST http://localhost:8000/review/post-comment/create/ -H "Content-Type: application/json" -d '{"user_id": 1, "post_id": 1, "comment": "Nice post!"}'
curl -X PATCH http://localhost:8000/review/post-comment/update/1/ -H "Content-Type: application/json" -d '{"comment": "Updated comment", "user_id": 1}'
curl -X GET "http://localhost:8000/review/post-comment/?post_id=1&page=1&page_size=10"
curl -X DELETE http://localhost:8000/review/post-comment/delete/1/ -H "Content-Type: application/json" -d '{"user_id": 1}'
"""
