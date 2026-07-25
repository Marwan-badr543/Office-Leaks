import React, { useMemo, useCallback } from "react";
import { Virtuoso } from "react-virtuoso";
import type { Post, User } from "../types";
import { PostCard } from "./PostCard";

interface PostListProps {
  posts: Post[];
  loading: boolean;
  hasMore: boolean;
  currentUser?: User | null;
  onOpenAuthModal?: () => void;
  loadMorePosts: () => void;
  onLike: (id: string) => void;
  onSave: (id: string) => void;
  selectedIndex?: number;
  onNavigateToUser?: (userId: string) => void;
  onCompanyClick?: (companyId: string) => void;
}

export const PostList: React.FC<PostListProps> = ({
  posts,
  loading,
  hasMore,
  currentUser,
  onOpenAuthModal,
  loadMorePosts,
  onLike,
  onSave,
  selectedIndex = -1,
  onNavigateToUser,
  onCompanyClick,
}) => {
  // Memoize Footer component to prevent Virtuoso from detecting a new component reference each render
  // Must be called before any early returns to satisfy React hooks rules
  const ListFooter = useCallback(() => {
    if (!loading && !hasMore) {
      return (
        <div className="py-8 text-center text-xs text-slate-400 font-medium font-body border-t border-slate-100/50 mt-4">
          All leaks decrypted. You're fully caught up.
        </div>
      );
    }
    if (loading) {
      return (
        <div className="py-6 flex flex-col items-center justify-center gap-2">
          <div className="w-6 h-6 border-2 border-[#0EA5E9] border-t-transparent rounded-full animate-spin" />
          <span className="text-[11px] font-bold text-[#0EA5E9] uppercase tracking-wider animate-pulse font-heading">
            Decrypting next batch...
          </span>
        </div>
      );
    }
    return <div className="h-8" />;
  }, [loading, hasMore]);

  // Memoize the components object so Virtuoso receives a referentially stable prop
  const virtuosoComponents = useMemo(() => ({
    Footer: ListFooter,
  }), [ListFooter]);

  // Cold load structural skeleton placeholders
  if (posts.length === 0 && loading) {
    return (
      <div className="space-y-4 w-full">
        {[1, 2, 3].map((key) => (
          <div
            key={key}
            className="post-wrapper-contain bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-4"
          >
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-xl skeleton-shimmer flex-shrink-0" />
              <div className="space-y-2 flex-1">
                <div className="h-4 w-36 rounded-md skeleton-shimmer" />
                <div className="h-3 w-48 rounded-md skeleton-shimmer" />
              </div>
            </div>
            <div className="space-y-2 pt-2">
              <div className="h-3.5 w-full rounded-md skeleton-shimmer" />
              <div className="h-3.5 w-5/6 rounded-md skeleton-shimmer" />
              <div className="h-3.5 w-3/4 rounded-md skeleton-shimmer" />
            </div>
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <div className="h-8 w-20 rounded-lg skeleton-shimmer" />
              <div className="h-8 w-20 rounded-lg skeleton-shimmer" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (posts.length === 0 && !loading) {
    return (
      <div className="bg-white border border-slate-100 rounded-2xl p-10 text-center shadow-sm">
        <p className="text-sm text-slate-500 font-medium font-body">
          No leaks found matching the current filters.
        </p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <Virtuoso
        useWindowScroll
        data={posts}
        endReached={loadMorePosts}
        increaseViewportBy={800}
        itemContent={(index, post) => (
          <PostCard
            key={post.id}
            post={post}
            currentUser={currentUser}
            onOpenAuthModal={onOpenAuthModal}
            onLike={onLike}
            onSave={onSave}
            isKeyboardFocused={selectedIndex === index}
            onNavigateToUser={onNavigateToUser}
            onCompanyClick={onCompanyClick}
          />
        )}
        components={virtuosoComponents}
      />
    </div>
  );
};
