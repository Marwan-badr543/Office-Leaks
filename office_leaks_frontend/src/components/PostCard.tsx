import React, { useState, useMemo, useEffect, useRef, useCallback } from "react";
import {
  ThumbsUp,
  MessageSquare,
  Share,
  Bookmark,
  CheckCircle,
  Lock,
  ChevronDown,
  ChevronUp,
  Heart,
  Building2
} from "lucide-react";
import type { Post, Comment, User, NestedComment } from "../types";
import { postsApi } from "../api/postsApi";
import { useToast } from "../hooks/useToast";
import { RepostModal } from "./RepostModal";

interface PostNestedCommentRowProps {
  nested: NestedComment;
  currentUser: User | null | undefined;
  onOpenAuthModal?: () => void;
  onNavigateToUser?: (userId: string) => void;
}

export const PostNestedCommentRow: React.FC<PostNestedCommentRowProps> = ({
  nested,
  currentUser,
  onOpenAuthModal,
  onNavigateToUser,
}) => {
  const [hasLiked, setHasLiked] = useState(nested.hasLiked || false);
  const [likesCount, setLikesCount] = useState(nested.likesCount || 0);
  const [animatingLike, setAnimatingLike] = useState(false);

  const handleLikeClick = async () => {
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }

    setAnimatingLike(true);
    setTimeout(() => setAnimatingLike(false), 300);

    const targetLikedState = !hasLiked;
    const userId = Number(currentUser.id) || 1;

    setHasLiked(targetLikedState);
    setLikesCount((prev) => (targetLikedState ? prev + 1 : Math.max(0, prev - 1)));

    try {
      if (targetLikedState) {
        await postsApi.likeNestedComment(nested.id, userId);
      } else {
        await postsApi.unlikeNestedComment(nested.id, userId);
      }
    } catch (err) {
      console.error("Failed to toggle nested comment like:", err);
      setHasLiked(!targetLikedState);
      setLikesCount((prev) => (targetLikedState ? Math.max(0, prev - 1) : prev + 1));
    }
  };

  return (
    <div className="bg-white rounded-lg p-2.5 text-[11px] border border-slate-100/50 space-y-1">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (nested.userId && onNavigateToUser) {
                onNavigateToUser(nested.userId);
              }
            }}
            className="w-5 h-5 rounded-full overflow-hidden flex-shrink-0 cursor-pointer animate-in fade-in"
          >
            <img
              src={nested.authorAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${nested.userId}`}
              alt={nested.authorName}
              className="w-full h-full object-cover"
            />
          </button>
          <button
            onClick={() => {
              if (nested.userId && onNavigateToUser) {
                onNavigateToUser(nested.userId);
              }
            }}
            className="font-bold text-slate-800 font-heading hover:text-[#0EA5E9] transition-colors cursor-pointer text-left"
          >
            {nested.authorName}
          </button>
        </div>
        <span className="text-[9px] text-slate-400">
          {nested.createdAt}
        </span>
      </div>

      <p className="text-slate-650 leading-normal font-body">
        {nested.parentCommentAuthorName && (
          <span className="text-[#0EA5E9] font-bold mr-1">
            @{nested.parentCommentAuthorName}
          </span>
        )}
        {nested.content}
      </p>

      <div className="flex items-center gap-2 pt-0.5 text-[9px] text-slate-400 font-bold">
        <button
          onClick={handleLikeClick}
          className={`flex items-center gap-1 hover:text-slate-700 cursor-pointer transition-colors ${hasLiked ? "text-[#0EA5E9]" : ""
            }`}
        >
          <ThumbsUp className={`w-2.5 h-2.5 ${animatingLike ? "animate-scale-pulse" : ""} ${hasLiked ? "fill-[#0EA5E9]" : ""}`} />
          <span>{likesCount}</span>
        </button>
      </div>
    </div>
  );
};

interface PostCommentRowProps {
  comm: Comment;
  currentUser: User | null | undefined;
  onOpenAuthModal?: () => void;
  onNavigateToUser?: (userId: string) => void;
  onReplyAdded?: () => void;
}

export const PostCommentRow: React.FC<PostCommentRowProps> = ({
  comm,
  currentUser,
  onOpenAuthModal,
  onNavigateToUser,
  onReplyAdded,
}) => {
  const [hasLiked, setHasLiked] = useState(comm.hasLiked || false);
  const [likesCount, setLikesCount] = useState(comm.likesCount || 0);
  const [nestedComments, setNestedComments] = useState<NestedComment[]>([]);
  const [repliesCount, setRepliesCount] = useState(comm.repliesCount || 0);
  const [showReplyForm, setShowReplyForm] = useState(false);
  const [showReplies, setShowReplies] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [submittingReply, setSubmittingReply] = useState(false);
  const [animatingLike, setAnimatingLike] = useState(false);
  const fetchedNestedRef = useRef(false);

  // Lazy-load nested comments ONLY when they are expanded (prevents massive duplicated network overhead)
  useEffect(() => {
    if (!showReplies || fetchedNestedRef.current) return;
    let isSubscribed = true;

    postsApi
      .getNestedComments(comm.id)
      .then((res) => {
        if (isSubscribed) {
          setNestedComments(res);
          fetchedNestedRef.current = true;
        }
      })
      .catch((err) => {
        console.error(`Failed to fetch nested comments for ${comm.id}:`, err);
      });
    return () => {
      isSubscribed = false;
    };
  }, [comm.id, showReplies]);

  const handleLikeClick = async () => {
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }

    setAnimatingLike(true);
    setTimeout(() => setAnimatingLike(false), 300);

    const targetLikedState = !hasLiked;
    const userId = Number(currentUser.id) || 1;

    setHasLiked(targetLikedState);
    setLikesCount((prev) => (targetLikedState ? prev + 1 : Math.max(0, prev - 1)));

    try {
      if (targetLikedState) {
        await postsApi.likePostComment(comm.id, userId);
      } else {
        await postsApi.unlikePostComment(comm.id, userId);
      }
    } catch (err) {
      console.error("Failed to toggle comment like:", err);
      setHasLiked(!targetLikedState);
      setLikesCount((prev) => (targetLikedState ? Math.max(0, prev - 1) : prev + 1));
    }
  };

  const handleAddReply = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    if (!replyText.trim()) return;

    setSubmittingReply(true);
    const userId = Number(currentUser.id) || 1;
    try {
      const newNested = await postsApi.createNestedComment(comm.id, replyText.trim(), userId);
      setNestedComments((prev) => [...prev, newNested]);
      setRepliesCount((prev) => prev + 1);
      if (onReplyAdded) onReplyAdded();
      setReplyText("");
      setShowReplyForm(false);
      setShowReplies(true);
    } catch (err) {
      console.error("Failed to post nested reply:", err);
    } finally {
      setSubmittingReply(false);
    }
  };

  return (
    <div className="bg-slate-50 rounded-xl p-3 text-xs border border-slate-100 space-y-2 animate-in fade-in duration-200">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (comm.userId && onNavigateToUser) {
                onNavigateToUser(comm.userId);
              }
            }}
            className="w-6 h-6 rounded-full overflow-hidden flex-shrink-0 cursor-pointer bg-slate-150"
          >
            <img
              src={comm.authorAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${comm.userId}`}
              alt={comm.authorName}
              className="w-full h-full object-cover"
            />
          </button>
          <div>
            <button
              onClick={() => {
                if (comm.userId && onNavigateToUser) {
                  onNavigateToUser(comm.userId);
                }
              }}
              className="font-bold text-slate-800 font-heading hover:text-[#0EA5E9] transition-colors cursor-pointer text-left"
            >
              {comm.authorName}
            </button>
            {comm.authorTitle && (
              <span className="text-[9px] text-[#0EA5E9] font-semibold block leading-none">
                {comm.authorTitle}
              </span>
            )}
          </div>
        </div>
        <span className="text-[10px] text-slate-400">
          {comm.createdAt}
        </span>
      </div>

      <p className="text-slate-650 leading-normal font-body pl-8">
        {comm.content}
      </p>

      <div className="flex items-center gap-3 pt-1 text-[10px] text-slate-400 font-bold pl-8">
        <button
          onClick={handleLikeClick}
          className={`flex items-center gap-1 hover:text-slate-700 cursor-pointer transition-colors ${hasLiked ? "text-[#0EA5E9]" : ""
            }`}
        >
          <ThumbsUp className={`w-3 h-3 ${animatingLike ? "animate-scale-pulse" : ""} ${hasLiked ? "fill-[#0EA5E9]" : ""}`} />
          <span>{likesCount}</span>
        </button>
        <button
          onClick={() => {
            if (!currentUser && onOpenAuthModal) {
              onOpenAuthModal();
              return;
            }
            setShowReplyForm(!showReplyForm);
          }}
          className="hover:text-slate-700 cursor-pointer flex items-center gap-0.5"
        >
          <MessageSquare className="w-3 h-3" />
          <span>Reply ({repliesCount})</span>
        </button>
      </div>

      {(repliesCount > 0 || nestedComments.length > 0) && (
        <div className="pl-8 mt-1.5 flex items-center gap-2">
          <button
            onClick={() => setShowReplies(!showReplies)}
            className="text-[10px] font-bold text-slate-500 hover:text-slate-700 cursor-pointer flex items-center gap-1"
          >
            <span className="w-4 border-t border-slate-350 mr-1 inline-block" />
            {showReplies ? "Hide replies" : `View ${repliesCount} ${repliesCount === 1 ? 'reply' : 'replies'}`}
          </button>
        </div>
      )}

      {(repliesCount > 0 || nestedComments.length > 0) && showReplies && (
        <div className="pl-8 mt-2 border-l border-slate-200 space-y-2 animate-in fade-in duration-200">
          {nestedComments.map((nested) => (
            <PostNestedCommentRow
              key={nested.id}
              nested={nested}
              currentUser={currentUser}
              onOpenAuthModal={onOpenAuthModal}
              onNavigateToUser={onNavigateToUser}
            />
          ))}
        </div>
      )}

      {showReplyForm && (
        <form onSubmit={handleAddReply} className="flex gap-2 pl-8 mt-2">
          <input
            autoFocus
            type="text"
            placeholder={`Reply to ${comm.authorName}...`}
            value={replyText}
            onChange={(e) => setReplyText(e.target.value)}
            className="flex-grow bg-white border border-slate-200 rounded-xl px-2 py-1 text-[11px] focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9] font-body"
          />
          <button
            type="submit"
            disabled={submittingReply || !replyText.trim()}
            className={`px-3 py-1 rounded-xl text-[10px] font-bold font-heading transition-colors ${submittingReply || !replyText.trim()
                ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                : "bg-[#0F172A] text-white hover:bg-slate-800 cursor-pointer"
              }`}
          >
            {submittingReply ? "Posting..." : "Reply"}
          </button>
        </form>
      )}
    </div>
  );
};

interface PostCardProps {
  post: Post;
  currentUser?: User | null;
  onOpenAuthModal?: () => void;
  onLike: (id: string) => void;
  onSave: (id: string) => void;
  isKeyboardFocused?: boolean;
  onNavigateToUser?: (userId: string) => void;
  onCompanyClick?: (companyId: string) => void;
}

export const PostCard: React.FC<PostCardProps> = React.memo(({
  post,
  currentUser,
  onOpenAuthModal,
  onLike,
  onSave,
  isKeyboardFocused = false,
  onNavigateToUser,
  onCompanyClick,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [commentList, setCommentList] = useState<Comment[]>(post.comments || []);
  const [newCommentText, setNewCommentText] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);

  // Animation pulse state & double-tap heart state
  const [animatingLike, setAnimatingLike] = useState(false);
  const [showDoubleTapHeart, setShowDoubleTapHeart] = useState(false);
  const [commentsCount, setCommentsCount] = useState(post.commentsCount || 0);
  const { addToast } = useToast();

  const commentInputRef = useRef<HTMLInputElement>(null);
  const cardRef = useRef<HTMLElement>(null);
  const lastTapRef = useRef<number>(0);

  // Repost modal state
  const [showRepostModal, setShowRepostModal] = useState(false);

  // Scroll into view when keyboard focused
  useEffect(() => {
    if (isKeyboardFocused && cardRef.current) {
      cardRef.current.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  }, [isKeyboardFocused]);

  // Fetch comments when comment thread is opened with AbortController
  useEffect(() => {
    if (!showComments) return;
    let isSubscribed = true;
    const controller = new AbortController();

    postsApi
      .getComments(post.id, 1)
      .then((comments) => {
        if (isSubscribed && comments.length > 0) {
          setCommentList(comments);
        }
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error(`Failed to fetch comments for post ${post.id}:`, err);
      });

    return () => {
      isSubscribed = false;
      controller.abort();
    };
  }, [showComments, post.id]);

  // Auto focus comment input when opening comments panel
  useEffect(() => {
    if (showComments && commentInputRef.current) {
      commentInputRef.current.focus();
    }
  }, [showComments]);

  // Instagram-style double tap gesture handler
  const handleDoubleTap = useCallback((_e: React.MouseEvent | React.TouchEvent) => {
    const now = Date.now();

    const DOUBLE_TAP_DELAY = 300; // ms
    if (now - lastTapRef.current < DOUBLE_TAP_DELAY) {
      // Trigger double tap heart animation overlay
      setShowDoubleTapHeart(true);
      setTimeout(() => setShowDoubleTapHeart(false), 750);

      // Trigger optimistic like if not already liked
      if (!currentUser && onOpenAuthModal) {
        onOpenAuthModal();
      } else if (!post.hasLiked) {
        onLike(post.id);
        setAnimatingLike(true);
        setTimeout(() => setAnimatingLike(false), 300);
      }
    }
    lastTapRef.current = now;
  }, [currentUser, onOpenAuthModal, post.hasLiked, post.id, onLike]);

  // Determine logo/avatar initial
  const avatarInitials = useMemo(() => {
    if (post.companyTag) {
      return post.companyTag.name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
    }
    return post.author.name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
  }, [post]);

  // Is this a review type?
  const isReview = post.type === "review" && post.review !== undefined;
  const review = post.review;

  // Formatting large numbers
  const formatNumber = (num: number) => {
    return num >= 1000 ? `${(num / 1000).toFixed(1)}k` : num;
  };

  const handleLikeClick = () => {
    if (!currentUser && onOpenAuthModal) {
      onOpenAuthModal();
      return;
    }
    setAnimatingLike(true);
    setTimeout(() => setAnimatingLike(false), 300);
    onLike(post.id);
  };

  const handleRepostClick = () => {
    if (!currentUser && onOpenAuthModal) {
      onOpenAuthModal();
      return;
    }
    setShowRepostModal(true);
  };

  const handleRepostSubmit = async (commentary: string, isAnonymous: boolean) => {
    const userId = Number(currentUser?.id) || 1;
    try {
      await postsApi.createPost({
        userId,
        content: commentary,
        parentPostId: Number(post.id),
        isAnonymous,
      });
      window.location.reload();
    } catch (err: any) {
      console.error("Failed to repost post:", err);
      let errMsg = "Failed to share. Please try again.";
      if (err.data) {
        if (typeof err.data === "string") {
          errMsg = err.data;
        } else if (typeof err.data === "object") {
          errMsg = err.data.detail || err.data.error || Object.values(err.data).flat().join(" ") || errMsg;
        }
      }
      addToast(errMsg, "error");
      throw err;
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    if (!newCommentText.trim()) return;

    setSubmittingComment(true);
    const userId = Number(currentUser.id) || 1;
    try {
      const newComment = await postsApi.createComment(post.id, newCommentText.trim(), userId);
      setCommentList(prev => [...prev, newComment]);
      setCommentsCount(prev => prev + 1);
      post.commentsCount += 1;
      setNewCommentText("");
    } catch (err) {
      console.error("Failed to post comment to backend API:", err);
    } finally {
      setSubmittingComment(false);
    }
  };

  return (
    <article
      id={`post-${post.id}`}
      ref={cardRef}
      onClick={handleDoubleTap}
      className={`post-wrapper-contain bg-white border rounded-2xl p-5 mb-5 shadow-sm hover:shadow-md transition-all duration-200 relative overflow-hidden select-none ${isKeyboardFocused
          ? "keyboard-focused-post border-[#0EA5E9]"
          : "border-slate-100"
        }`}
    >
      {/* Instagram-style double tap heart overlay animation */}
      {showDoubleTapHeart && (
        <div className="absolute inset-0 z-30 pointer-events-none flex items-center justify-center bg-black/5">
          <Heart className="w-24 h-24 text-[#0EA5E9] fill-[#0EA5E9] animate-double-tap-heart drop-shadow-lg" />
        </div>
      )}

      {/* Header Info */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          {/* Avatar / Company Initials Logo */}
          {post.author.id === 'anon' ? (
            <div className="w-12 h-12 rounded-xl bg-[#0F172A] text-white flex items-center justify-center font-extrabold text-sm font-heading shadow-sm flex-shrink-0 overflow-hidden">
              <span>{avatarInitials}</span>
            </div>
          ) : (
            <button
              onClick={() => {
                if (post.author.id && onNavigateToUser) {
                  onNavigateToUser(post.author.id);
                }
              }}
              className="w-12 h-12 rounded-xl bg-[#0F172A] text-white flex items-center justify-center font-extrabold text-sm font-heading shadow-sm flex-shrink-0 cursor-pointer overflow-hidden bg-slate-900"
            >
              {post.author.avatar ? (
                <img
                  src={post.author.avatar}
                  alt={post.author.name}
                  className="w-full h-full rounded-xl object-cover bg-white"
                />
              ) : (
                <span>{avatarInitials}</span>
              )}
            </button>
          )}

          <div>
            <div className="flex items-center gap-1.5 flex-wrap">
              {post.author.id === 'anon' ? (
                <span className="font-bold text-slate-800 text-sm font-heading">
                  {post.author.name}
                </span>
              ) : (
                <button
                  onClick={() => {
                    if (post.author.id && onNavigateToUser) {
                      onNavigateToUser(post.author.id);
                    }
                  }}
                  className="font-bold text-slate-800 text-sm font-heading hover:text-[#0EA5E9] transition-colors cursor-pointer text-left"
                >
                  {post.author.name}
                </button>
              )}
              {post.companyTag && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (onCompanyClick && post.companyTag) {
                      onCompanyClick(post.companyTag.id);
                    }
                  }}
                  className="flex items-center gap-1 text-xs text-[#0EA5E9] font-extrabold bg-[#0EA5E9]/10 px-2.5 py-0.5 rounded-xl hover:bg-[#0EA5E9]/20 transition-colors cursor-pointer"
                >
                  <Building2 className="w-3.5 h-3.5 text-[#0EA5E9]" />
                  {post.companyTag.name}
                </button>
              )}
            </div>

            {/* Meta details */}
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mt-0.5 font-medium flex-wrap">
              {isReview && review ? (
                <>
                  {review.rating !== undefined && review.rating !== null && (
                    <>
                      <span className="flex items-center gap-0.5 text-slate-700 font-bold">
                        {review.rating.toFixed(1)}
                        <span className="text-[10px] text-slate-450 font-normal">/4.0</span>
                      </span>
                      <span className="text-slate-300">•</span>
                    </>
                  )}
                  <span>{review.tag}</span>
                  <span className="text-slate-300">•</span>
                  <span>{post.author.location}</span>
                </>
              ) : (
                <>
                  <span>{post.author.title}</span>
                  <span className="text-slate-300">•</span>
                  <span>{post.author.location}</span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Timestamp & Anon Indicator */}
        <div className="text-right flex flex-col items-end gap-1.5">
          <span className="text-xs text-slate-400 font-medium">
            {post.createdAt}
          </span>
          {post.author.id === 'anon' && (
            <span className="flex items-center gap-1 text-[10px] text-slate-400 font-bold uppercase tracking-wider bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-lg">
              <Lock className="w-2.5 h-2.5 text-slate-400" />
              Anonymous
            </span>
          )}
        </div>
      </div>

      {/* Tags Row */}
      <div className="flex flex-wrap items-center gap-2 mt-4">
        {isReview && review && (
          <span className="text-xs font-semibold px-2.5 py-1 bg-amber-50 text-amber-700 rounded-lg border border-amber-100/50">
            {review.category}
          </span>
        )}
        {isReview && review && review.tag && (
          <span className="text-xs font-semibold px-2.5 py-1 bg-slate-50 text-slate-650 rounded-lg border border-slate-100">
            {review.tag}
          </span>
        )}
        {!isReview && post.category && (
          <span className="text-xs font-semibold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg border border-indigo-100/50">
            {post.category}
          </span>
        )}
      </div>

      {/* Review / Post Content */}
      <div className="mt-4">
        {isReview && review && (
          <>
            <h4 className="font-extrabold text-slate-800 text-base leading-snug font-heading mb-1.5">
              {review.title}
            </h4>
            <p className={`text-slate-600 text-sm leading-relaxed font-body ${!isExpanded ? "line-clamp-3" : ""}`}>
              {review.content}
            </p>
          </>
        )}
        {!isReview && post.content && (
          <p className={`text-slate-600 text-sm leading-relaxed font-body ${!isExpanded ? "line-clamp-3" : ""}`}>
            {post.content}
          </p>
        )}
        {((isReview && review) ? review.content.length > 180 : post.content.length > 180) && (
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-xs font-bold text-[#0EA5E9] hover:underline mt-2 flex items-center gap-0.5 cursor-pointer"
          >
            {isExpanded ? (
              <>Read Less <ChevronUp className="w-3.5 h-3.5" /></>
            ) : (
              <>Read full leak <ChevronDown className="w-3.5 h-3.5" /></>
            )}
          </button>
        )}

        {/* Facebook-style Quoted Parent Review Preview (For Reposted Reviews) */}
        {!isReview && post.review && (
          <div 
            onClick={(e) => {
              e.stopPropagation();
              if (onCompanyClick && post.companyTag) {
                const url = new URL(window.location.href);
                url.searchParams.set("tab", "companies");
                url.searchParams.set("company", post.companyTag.id);
                if (post.review) {
                  url.searchParams.set("highlightReview", post.review.id);
                }
                window.history.pushState({}, "", url.toString());
                onCompanyClick(post.companyTag.id);
              }
            }}
            className="mt-3 bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-2 text-left animate-in fade-in duration-200 cursor-pointer hover:border-[#0EA5E9] hover:bg-slate-100/50 transition-all"
          >
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-700 font-heading">
                  {post.review.authorName}
                </span>
                {post.companyTag && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onCompanyClick && post.companyTag) {
                        onCompanyClick(post.companyTag.id);
                      }
                    }}
                    className="text-[9px] text-[#0EA5E9] font-bold bg-[#0EA5E9]/10 px-1.5 py-0.5 rounded-full inline-flex items-center gap-0.5 hover:bg-[#0EA5E9]/20 transition-colors cursor-pointer"
                  >
                    <Building2 className="w-2.5 h-2.5 text-[#0EA5E9]" />
                    {post.companyTag.name}
                  </button>
                )}
              </div>
              <span>{post.review.createdAt}</span>
            </div>

            {post.review.category && (
              <span className="inline-block text-[9px] font-semibold px-2 py-0.5 bg-amber-50 text-amber-700 rounded-md border border-amber-100/50">
                {post.review.category}
              </span>
            )}

            {post.review.title && (
              <h5 className="font-bold text-slate-800 text-xs font-heading">
                {post.review.title}
              </h5>
            )}

            <p className="text-slate-650 text-xs leading-relaxed font-body line-clamp-3">
              {post.review.content}
            </p>
          </div>
        )}

        {/* Facebook-style Quoted Parent Post Preview */}
        {post.parentPost && (
          <div 
            onClick={(e) => {
              e.stopPropagation();
              if (post.parentPost) {
                const element = document.getElementById(`post-${post.parentPost.id}`);
                if (element) {
                  element.scrollIntoView({ behavior: "smooth", block: "center" });
                  element.classList.add("ring-2", "ring-[#0EA5E9]", "ring-offset-2");
                  setTimeout(() => {
                    element.classList.remove("ring-2", "ring-[#0EA5E9]", "ring-offset-2");
                  }, 2000);
                } else {
                  const url = new URL(window.location.href);
                  url.searchParams.set("tab", "feed");
                  url.searchParams.set("highlight", post.parentPost.id);
                  window.history.pushState({}, "", url.toString());
                  window.location.reload();
                }
              }
            }}
            className="mt-3 bg-slate-50 border border-slate-200/80 rounded-xl p-4 space-y-2 text-left animate-in fade-in duration-200 cursor-pointer hover:border-[#0EA5E9] hover:bg-slate-100/50 transition-all"
          >
            <div className="flex items-center justify-between text-[11px] text-slate-400">
              <div className="flex items-center gap-2">
                <span className="font-bold text-slate-700 font-heading">
                  {post.parentPost.author.name}
                </span>
                {post.parentPost.companyTag && (
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onCompanyClick && post.parentPost?.companyTag) {
                        onCompanyClick(post.parentPost.companyTag.id);
                      }
                    }}
                    className="text-[9px] text-[#0EA5E9] font-bold bg-[#0EA5E9]/10 px-1.5 py-0.5 rounded-full inline-flex items-center gap-0.5 hover:bg-[#0EA5E9]/20 transition-colors cursor-pointer"
                  >
                    <Building2 className="w-2 h-2 text-[#0EA5E9]" />
                    {post.parentPost.companyTag.name}
                  </button>
                )}
              </div>
              <span>{post.parentPost.createdAt}</span>
            </div>

            {post.parentPost.category && (
              <span className="inline-block text-[10px] font-semibold px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md border border-indigo-100/50">
                {post.parentPost.category}
              </span>
            )}

            {post.parentPost.review && (
              <h5 className="font-bold text-slate-800 text-xs font-heading">
                {post.parentPost.review.title}
              </h5>
            )}

            <p className="text-slate-655 text-xs leading-relaxed font-body line-clamp-3">
              {post.parentPost.review ? post.parentPost.review.content : post.parentPost.content}
            </p>
          </div>
        )}
      </div>

      {/* Engagement Stats & Divider */}
      <div className="flex items-center justify-between text-xs text-slate-400 mt-5 pt-3 border-t border-slate-100">
        <div className="flex items-center gap-4">
          <button
            onClick={handleLikeClick}
            className={`flex items-center gap-1.5 font-bold transition-all px-2.5 py-1.5 rounded-lg cursor-pointer ${post.hasLiked
                ? "text-[#0EA5E9] bg-[#0EA5E9]/10"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
              }`}
          >
            <ThumbsUp className={`w-4 h-4 transition-transform ${animatingLike ? "animate-scale-pulse" : ""} ${post.hasLiked ? "fill-[#0EA5E9]" : ""}`} />
            <span>{formatNumber(post.likesCount)}</span>
          </button>

          <button
            onClick={() => setShowComments(!showComments)}
            className={`flex items-center gap-1.5 font-bold transition-all px-2.5 py-1.5 rounded-lg cursor-pointer ${showComments
                ? "text-[#0F172A] bg-slate-100"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
              }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>{formatNumber(commentsCount)}</span>
          </button>

          {/* Repost button using modern curved arrow pointing right (Share) like Facebook */}
          {!(post.parentPost || post.review) && (
            <button
              onClick={handleRepostClick}
              className="flex items-center gap-1.5 font-bold transition-all px-2.5 py-1.5 rounded-lg cursor-pointer text-slate-500 hover:bg-slate-50 hover:text-slate-800"
            >
              <Share className="w-4 h-4" />
              <span>Share</span>
            </button>
          )}
        </div>
      </div>

      {/* Expanded Comments Panel */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-slate-100 space-y-4 transition-all duration-200">
          <h5 className="text-xs font-bold text-slate-855 font-heading">
            Discussion thread ({commentsCount})
          </h5>

          {/* Comment list */}
          <div className="space-y-3 pr-1">
            {commentList.map((comm) => (
              <PostCommentRow
                key={comm.id}
                comm={comm}
                currentUser={currentUser}
                onOpenAuthModal={onOpenAuthModal}
                onNavigateToUser={onNavigateToUser}
                onReplyAdded={() => {
                  setCommentsCount(prev => prev + 1);
                  post.commentsCount += 1;
                }}
              />
            ))}

            {commentList.length === 0 && (
              <p className="text-xs text-slate-400 italic text-center py-4 font-body">
                No comments yet. Be the first to join the conversation.
              </p>
            )}
          </div>

          {/* New Comment Input with Auto Focus */}
          <form onSubmit={handleAddComment} className="flex gap-2">
            <input
              ref={commentInputRef}
              type="text"
              placeholder={currentUser ? "Post an anonymous comment..." : "Sign in to post a comment..."}
              value={newCommentText}
              onChange={(e) => setNewCommentText(e.target.value)}
              onFocus={() => {
                if (!currentUser && onOpenAuthModal) onOpenAuthModal();
              }}
              className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9] font-body"
            />
            <button
              type="submit"
              disabled={submittingComment || !newCommentText.trim()}
              className={`px-4 py-2 rounded-xl text-xs font-bold font-heading transition-colors ${submittingComment || !newCommentText.trim()
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-[#0F172A] text-white hover:bg-slate-800 cursor-pointer"
                }`}
            >
              {submittingComment ? "Replying..." : "Reply"}
            </button>
          </form>
        </div>
      )}

      {/* Repost Commentary Modal */}
      {showRepostModal && currentUser && (
        <RepostModal
          isOpen={showRepostModal}
          onClose={() => setShowRepostModal(false)}
          currentUser={currentUser}
          parentPost={post}
          onSubmit={handleRepostSubmit}
        />
      )}
    </article>
  );
});
PostCard.displayName = "PostCard";
