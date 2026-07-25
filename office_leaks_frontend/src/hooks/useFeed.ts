import { useState, useEffect, useCallback, useRef } from "react";
import type { Post, Review, User } from "../types";
import { postsApi } from "../api/postsApi";
import { companiesApi } from "../api/companiesApi";

interface UseFeedOptions {
  currentUser?: User | null;
  onOpenAuthModal?: () => void;
  onErrorToast?: (msg: string, actionText?: string, onAction?: () => void) => void;
  enabled?: boolean;
}

export const useFeed = (options: UseFeedOptions = {}) => {
  const { currentUser, onOpenAuthModal, onErrorToast, enabled = true } = options;
  const [posts, setPosts] = useState<Post[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);

  // Filters
  const [activeCategory, setActiveCategory] = useState<string>("All Leaks");
  const [feedType, setFeedType] = useState<"all" | "review" | "text">("all");
  const [sortBy, setSortBy] = useState<"recent" | "popular">("recent");

  // Zero-latency haptic feedback helper
  const triggerHaptic = useCallback(() => {
    try {
      if (typeof navigator !== "undefined" && navigator.vibrate) {
        navigator.vibrate(10);
      }
    } catch {}
  }, []);

  // Fetch initial posts from API (AllowAny public endpoint)
  useEffect(() => {
    if (!enabled) return;
    let isSubscribed = true;
    const controller = new AbortController();
    setLoading(true);
    setPage(1);

    postsApi
      .getPosts({
        page: 1,
        pageSize: 10,
        ordering: sortBy,
        category: activeCategory !== "All Leaks" ? activeCategory : undefined,
      })
      .then((res) => {
        if (!isSubscribed) return;
        let fetched = res.posts || [];
        if (feedType === "review") {
          fetched = fetched.filter((p) => p.type === "review");
        } else if (feedType === "text") {
          fetched = fetched.filter((p) => p.type === "text");
        }
        setPosts(fetched);
        setHasMore(res.hasMore);
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error("Failed to fetch posts from backend:", err);
        if (!isSubscribed) return;
        setPosts([]);
        setHasMore(false);
      })
      .finally(() => {
        if (isSubscribed) setLoading(false);
      });

    return () => {
      isSubscribed = false;
      controller.abort();
    };
  }, [activeCategory, feedType, sortBy, enabled]);

  // Load next page (AllowAny public endpoint)
  const loadMorePosts = useCallback(() => {
    if (loading || !hasMore) return;

    setLoading(true);
    const nextPage = page + 1;

    postsApi
      .getPosts({
        page: nextPage,
        pageSize: 10,
        ordering: sortBy,
        category: activeCategory !== "All Leaks" ? activeCategory : undefined,
      })
      .then((res) => {
        let fetched = res.posts || [];
        if (feedType === "review") {
          fetched = fetched.filter((p) => p.type === "review");
        } else if (feedType === "text") {
          fetched = fetched.filter((p) => p.type === "text");
        }
        setPosts((prev) => [...prev, ...fetched]);
        setPage(nextPage);
        setHasMore(res.hasMore);
      })
      .catch((err) => {
        console.error("Failed to load more posts:", err);
        setHasMore(false);
      })
      .finally(() => setLoading(false));
  }, [loading, hasMore, page, sortBy, activeCategory, feedType]);

  // Handle Like (Optimistic UI Update with Rollback & Toast)
  const handleLikePost = useCallback(
    (postId: string) => {
      if (!currentUser) {
        if (onOpenAuthModal) onOpenAuthModal();
        return;
      }

      triggerHaptic();
      let wasLikedPreviously = false;

      // Instant optimistic state flip (<16ms)
      setPosts((prev) =>
        prev.map((post) => {
          if (post.id === postId) {
            wasLikedPreviously = !!post.hasLiked;
            const isLiking = !post.hasLiked;
            return {
              ...post,
              hasLiked: isLiking,
              likesCount: Math.max(0, post.likesCount + (isLiking ? 1 : -1)),
            };
          }
          return post;
        })
      );

      const userId = Number(currentUser.id) || 1;
      const apiCall = wasLikedPreviously
        ? postsApi.unlikePost(postId, userId)
        : postsApi.likePost(postId, userId);

      apiCall.catch((err) => {
        console.error("Optimistic Like mutation failed, rolling back:", err);
        // Rollback state instantly
        setPosts((prev) =>
          prev.map((post) => {
            if (post.id === postId) {
              return {
                ...post,
                hasLiked: wasLikedPreviously,
                likesCount: Math.max(0, post.likesCount + (wasLikedPreviously ? 1 : -1)),
              };
            }
            return post;
          })
        );
        if (onErrorToast) {
          onErrorToast("Action failed. Tap to retry", "Retry", () => handleLikePost(postId));
        }
      });
    },
    [currentUser, onOpenAuthModal, triggerHaptic, onErrorToast]
  );

  // Handle Save (Optimistic UI Update with Rollback & Toast)
  const handleSavePost = useCallback(
    (postId: string) => {
      if (!currentUser) {
        if (onOpenAuthModal) onOpenAuthModal();
        return;
      }

      triggerHaptic();

      setPosts((prev) =>
        prev.map((post) => {
          if (post.id === postId) {
            return { ...post, hasSaved: !post.hasSaved };
          }
          return post;
        })
      );
    },
    [currentUser, onOpenAuthModal, triggerHaptic]
  );


  // Add post (Requires Authentication)
  const handleAddPost = useCallback(
    async (
      type: "text" | "review",
      content: string,
      companyId?: string,
      _rating?: number,
      category?: Review["category"],
      _tag?: string,
      isAnonymous: boolean = true
    ) => {
      if (!currentUser) {
        if (onOpenAuthModal) onOpenAuthModal();
        return;
      }

      const userId = Number(currentUser.id) || 1;
      try {
        if (type === "review" && companyId) {
          const createdReview = await companiesApi.createReview({
            userId,
            companyId,
            review: content,
            isAnonymous,
          });
          const createdPost = await postsApi.createPost({
            userId,
            reviewId: Number(createdReview.id),
            category: category || "Workplace Culture",
            isAnonymous,
          });
          setPosts((prev) => [createdPost, ...prev]);
        } else {
          const createdPost = await postsApi.createPost({
            userId,
            content,
            companyId: companyId ? Number(companyId) : undefined,
            category: category || "General Discussion",
            isAnonymous,
          });
          setPosts((prev) => [createdPost, ...prev]);
        }
      } catch (err) {
        console.error("Error creating post on backend API:", err);
        if (onErrorToast) {
          onErrorToast("Failed to publish leak. Please try again.");
        }
      }
    },
    [currentUser, onOpenAuthModal, onErrorToast]
  );


  return {
    posts,
    hasMore,
    loading,
    activeCategory,
    setActiveCategory,
    feedType,
    setFeedType,
    sortBy,
    setSortBy,
    loadMorePosts,
    handleLikePost,
    handleSavePost,
    handleAddPost,
  };
};
