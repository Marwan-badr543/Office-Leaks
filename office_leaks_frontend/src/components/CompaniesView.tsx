import React, { useState, useEffect, useMemo, useRef } from "react";
import { 
  Building2, 
  MapPin, 
  Calendar, 
  Star, 
  Search, 
  ChevronLeft, 
  CheckCircle,
  MessageSquare,
  ThumbsUp,
  X,
  Lock,
  User as UserIcon,
  ShieldCheck,
  PenTool,
  Share
} from "lucide-react";
import type { Company, Review, User, Comment, NestedComment } from "../types";
import { companiesApi } from "../api/companiesApi";
import { postsApi } from "../api/postsApi";
import { RepostModal } from "./RepostModal";
import { useDebounce } from "../hooks/useDebounce";
import { useScrollMemory } from "../hooks/useScrollMemory";

interface CompaniesViewProps {
  currentUser?: User | null;
  onOpenAuthModal?: () => void;
  selectedCompanyIdExternal?: string | null;
  onClearExternalCompany?: () => void;
  onNavigateToUser?: (userId: string) => void;
}

interface ReviewCardProps {
  rev: Review;
  currentUser?: User | null;
  onOpenAuthModal?: () => void;
  onNavigateToUser?: (userId: string) => void;
}

interface NestedCommentRowProps {
  nested: NestedComment;
  currentUser: User | null | undefined;
  onOpenAuthModal?: () => void;
  onNavigateToUser?: (userId: string) => void;
}

export const NestedCommentRow: React.FC<NestedCommentRowProps> = ({
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
        await companiesApi.likeNestedComment(nested.id, userId);
      } else {
        await companiesApi.unlikeNestedComment(nested.id, userId);
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
            className="w-5 h-5 rounded-full overflow-hidden flex-shrink-0 cursor-pointer"
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
          className={`flex items-center gap-1 hover:text-slate-700 cursor-pointer transition-colors ${
            hasLiked ? "text-[#0EA5E9]" : ""
          }`}
        >
          <ThumbsUp className={`w-2.5 h-2.5 ${animatingLike ? "animate-scale-pulse" : ""} ${hasLiked ? "fill-[#0EA5E9]" : ""}`} />
          <span>{likesCount}</span>
        </button>
      </div>
    </div>
  );
};

interface ReviewCommentRowProps {
  comm: Comment;
  currentUser: User | null | undefined;
  onOpenAuthModal?: () => void;
  onNavigateToUser?: (userId: string) => void;
  onReplyAdded?: () => void;
}

export const ReviewCommentRow: React.FC<ReviewCommentRowProps> = ({
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

  useEffect(() => {
    if (!showReplies || fetchedNestedRef.current) return;
    let isSubscribed = true;
    companiesApi
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
        await companiesApi.likeReviewComment(comm.id, userId);
      } else {
        await companiesApi.unlikeReviewComment(comm.id, userId);
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
      const newNested = await companiesApi.createNestedComment(comm.id, replyText.trim(), userId);
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
    <div className="bg-slate-50 rounded-xl p-3 text-xs border border-slate-100 space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              if (comm.userId && onNavigateToUser) {
                onNavigateToUser(comm.userId);
              }
            }}
            className="w-6 h-6 rounded-full overflow-hidden flex-shrink-0 cursor-pointer"
          >
            <img
              src={comm.authorAvatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${comm.userId}`}
              alt={comm.authorName}
              className="w-full h-full object-cover"
            />
          </button>
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
          className={`flex items-center gap-1 hover:text-slate-700 cursor-pointer transition-colors ${
            hasLiked ? "text-[#0EA5E9]" : ""
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
        <div className="pl-8 mt-2 border-l border-slate-200 space-y-2">
          {nestedComments.map((nested) => (
            <NestedCommentRow
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
            className={`px-3 py-1 rounded-xl text-[10px] font-bold font-heading transition-colors ${
              submittingReply || !replyText.trim()
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

export const ReviewCard: React.FC<ReviewCardProps> = ({
  rev,
  currentUser,
  onOpenAuthModal,
  onNavigateToUser,
}) => {
  const [hasLiked, setHasLiked] = useState(rev.hasLiked || false);
  const [likesCount, setLikesCount] = useState(rev.likesCount || 0);
  const [showComments, setShowComments] = useState(false);
  const [commentList, setCommentList] = useState<Comment[]>([]);
  const [newCommentText, setNewCommentText] = useState("");
  const [submittingComment, setSubmittingComment] = useState(false);
  const [animatingLike, setAnimatingLike] = useState(false);
  const [commentsCount, setCommentsCount] = useState(rev.commentsCount || 0);
  const [showRepostModal, setShowRepostModal] = useState(false);

  const formatNumber = (num: number) => {
    return num >= 1000 ? `${(num / 1000).toFixed(1)}k` : num;
  };

  // Fetch comments when comments section is opened
  useEffect(() => {
    if (!showComments) return;
    let isSubscribed = true;

    companiesApi
      .getReviewComments(rev.id)
      .then((comments) => {
        if (isSubscribed) {
          setCommentList(comments);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch review comments:", err);
      });

    return () => {
      isSubscribed = false;
    };
  }, [showComments, rev.id]);

  const handleLikeClick = async () => {
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }

    setAnimatingLike(true);
    setTimeout(() => setAnimatingLike(false), 300);

    const targetLikedState = !hasLiked;
    const userId = Number(currentUser.id) || 1;

    // Optimistic Update
    setHasLiked(targetLikedState);
    setLikesCount((prev) => (targetLikedState ? prev + 1 : Math.max(0, prev - 1)));

    try {
      if (targetLikedState) {
        await companiesApi.likeReview(rev.id, userId);
      } else {
        await companiesApi.unlikeReview(rev.id, userId);
      }
    } catch (err: any) {
      const isDuplicate = err.response?.data?.error?.type === "DuplicateResourceError" ||
                          err.response?.data?.error?.message?.includes("already liked");

      if (targetLikedState && isDuplicate) {
        // Self-healing: they already liked it previously, so the initial backend count already included their like.
        // We set hasLiked to true, but reset the count to rev.likesCount (since their like was already counted in it).
        setHasLiked(true);
        setLikesCount(rev.likesCount);
      } else {
        console.error("Failed to toggle review like:", err);
        // Rollback
        setHasLiked(!targetLikedState);
        setLikesCount((prev) => (targetLikedState ? Math.max(0, prev - 1) : prev + 1));
      }
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
      const newComment = await companiesApi.createReviewComment(rev.id, newCommentText.trim(), userId);
      setCommentList((prev) => [...prev, newComment]);
      setCommentsCount((prev) => prev + 1);
      rev.commentsCount += 1;
      setNewCommentText("");
    } catch (err) {
      console.error("Failed to post comment to backend:", err);
    } finally {
      setSubmittingComment(false);
    }
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
        reviewId: Number(rev.id),
        companyId: Number(rev.companyId),
        category: rev.category,
        isAnonymous,
      });
      window.location.reload();
    } catch (err: any) {
      console.error("Failed to repost review:", err);
      let errMsg = "Failed to share review. Please try again.";
      if (err.data) {
        if (typeof err.data === "string") {
          errMsg = err.data;
        } else if (typeof err.data === "object") {
          errMsg = err.data.detail || err.data.error || Object.values(err.data).flat().join(" ") || errMsg;
        }
      }
      alert(errMsg);
      throw err;
    }
  };

  const isHigh = rev.rating ? rev.rating >= 3.0 : false;
  const initials = rev.isAnonymous 
    ? "AE" 
    : rev.authorName.split(" ").map((w) => w[0]).join("").slice(0, 2).toUpperCase();

  return (
    <div id={`review-${rev.id}`} className="bg-white border border-slate-100 rounded-2xl p-5 shadow-sm space-y-4 hover:shadow-md transition-shadow duration-200">
      {/* Facebook-like Header */}
      <div className="flex items-center justify-between gap-3 border-b border-slate-50 pb-3">
        <div className="flex items-center gap-3">
          {/* Avatar */}
          {rev.isAnonymous ? (
            <div className="w-10 h-10 rounded-xl bg-[#0F172A] text-white flex items-center justify-center font-extrabold text-xs font-heading shadow-sm flex-shrink-0">
              <span>AE</span>
            </div>
          ) : (
            <button
              onClick={() => {
                if (rev.user?.id && onNavigateToUser) {
                  onNavigateToUser(rev.user.id);
                }
              }}
              className="w-10 h-10 rounded-xl bg-[#0F172A] text-white flex items-center justify-center font-extrabold text-xs font-heading shadow-sm flex-shrink-0 cursor-pointer overflow-hidden"
            >
              {rev.user?.avatar ? (
                <img
                  src={rev.user.avatar}
                  alt={rev.authorName}
                  className="w-full h-full object-cover"
                />
              ) : (
                <span>{initials}</span>
              )}
            </button>
          )}

          <div>
            {rev.isAnonymous ? (
              <h3 className="font-bold text-slate-800 text-sm font-heading">
                Anonymous Member
              </h3>
            ) : (
              <button
                onClick={() => {
                  if (rev.user?.id && onNavigateToUser) {
                    onNavigateToUser(rev.user.id);
                  }
                }}
                className="font-bold text-slate-800 text-sm font-heading hover:text-[#0EA5E9] transition-colors cursor-pointer text-left"
              >
                {rev.authorName}
              </button>
            )}
            <div className="text-[10px] text-slate-400 mt-0.5 font-medium">
              <span>{rev.createdAt}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Category & Rating Badges (Before Content) */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] font-extrabold px-2.5 py-1 rounded-lg bg-[#0EA5E9]/10 text-[#0EA5E9] uppercase tracking-wider font-heading">
          {rev.category}
        </span>
        {rev.rating !== undefined && rev.rating !== null && (
          <span className={`text-[10px] font-extrabold px-2.5 py-1 rounded-lg uppercase tracking-wider font-heading ${
            isHigh 
              ? "bg-[#22C55E]/10 text-[#22C55E]" 
              : "bg-[#EF4444]/10 text-[#EF4444]"
          }`}>
            {rev.rating.toFixed(1)} Rating
          </span>
        )}
      </div>

      {/* Content */}
      <div>
        <p className="text-xs text-slate-600 leading-relaxed font-body">
          {rev.content}
        </p>
      </div>

      {/* Action Footer Buttons */}
      <div className="flex items-center gap-2 pt-2 border-t border-slate-50">
        <button 
          onClick={handleLikeClick}
          className={`flex items-center gap-1.5 font-bold transition-all px-2.5 py-1.5 rounded-lg cursor-pointer text-xs ${
            hasLiked 
              ? "text-[#0EA5E9] bg-[#0EA5E9]/10" 
              : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
          }`}
        >
          <ThumbsUp className={`w-4 h-4 transition-transform ${animatingLike ? "animate-scale-pulse" : ""} ${hasLiked ? "fill-[#0EA5E9]" : ""}`} />
          <span>{formatNumber(likesCount)}</span>
        </button>
        <button 
          onClick={() => setShowComments(!showComments)}
          className={`flex items-center gap-1.5 font-bold transition-all px-2.5 py-1.5 rounded-lg cursor-pointer text-xs ${
            showComments 
              ? "text-[#0F172A] bg-slate-100" 
              : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          <span>{formatNumber(commentsCount)}</span>
        </button>
        <button 
          onClick={handleRepostClick}
          className="flex items-center gap-1.5 font-bold transition-all px-2.5 py-1.5 rounded-lg cursor-pointer text-xs text-slate-500 hover:bg-slate-50 hover:text-slate-800"
        >
          <Share className="w-4 h-4" />
          <span>Share</span>
        </button>
      </div>

      {showRepostModal && currentUser && (
        <RepostModal
          isOpen={showRepostModal}
          onClose={() => setShowRepostModal(false)}
          currentUser={currentUser}
          review={rev}
          onSubmit={handleRepostSubmit}
        />
      )}

      {/* Expanded Discussion Comments Panel */}
      {showComments && (
        <div className="mt-4 pt-4 border-t border-slate-100 space-y-4 transition-all duration-200">
          <h5 className="text-[10px] uppercase tracking-wider font-bold text-slate-400 font-heading">
            Discussion thread ({commentsCount})
          </h5>

          {/* Comment list */}
          <div className="space-y-3 pr-1">
            {commentList.map((comm) => (
              <ReviewCommentRow
                key={comm.id}
                comm={comm}
                currentUser={currentUser}
                onOpenAuthModal={onOpenAuthModal}
                onNavigateToUser={onNavigateToUser}
                onReplyAdded={() => {
                  setCommentsCount((prev) => prev + 1);
                  rev.commentsCount += 1;
                }}
              />
            ))}

            {commentList.length === 0 && (
              <p className="text-xs text-slate-400 italic text-center py-4 font-body">
                No comments yet. Be the first to join the conversation.
              </p>
            )}
          </div>

          {/* New Comment Input */}
          <form onSubmit={handleAddComment} className="flex gap-2">
            <input
              type="text"
              placeholder={currentUser ? "Post a comment..." : "Sign in to post a comment..."}
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
              className={`px-4 py-2 rounded-xl text-xs font-bold font-heading transition-colors ${
                submittingComment || !newCommentText.trim()
                  ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                  : "bg-[#0F172A] text-white hover:bg-slate-800 cursor-pointer"
              }`}
            >
              {submittingComment ? "Replying..." : "Reply"}
            </button>
          </form>
        </div>
      )}
    </div>
  );
};

export const CompaniesView: React.FC<CompaniesViewProps> = ({
  currentUser,
  onOpenAuthModal,
  selectedCompanyIdExternal,
  onClearExternalCompany,
  onNavigateToUser,
}) => {
  const [companyList, setCompanyList] = useState<Company[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const debouncedSearchTerm = useDebounce(searchTerm, 250);
  const [industryFilter, setIndustryFilter] = useState("All");
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");
  const [liveReviews, setLiveReviews] = useState<Review[]>([]);
  const [loadingCompanies, setLoadingCompanies] = useState(true);
  const [isMobileDetailView, setIsMobileDetailView] = useState(false);

  useScrollMemory("companies");

  // Separate Modal States: Rating Modal vs Review Modal
  const [showRateModal, setShowRateModal] = useState(false);
  const [rateScore, setRateScore] = useState<number>(3.5);
  const [submittingRate, setSubmittingRate] = useState(false);
  const [rateSuccessMsg, setRateSuccessMsg] = useState("");

  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewContent, setReviewContent] = useState("");
  const [reviewCategory, setReviewCategory] = useState<Review["category"]>("Workplace Culture");
  const [reviewIsAnonymous, setReviewIsAnonymous] = useState(true);
  const [submittingReview, setSubmittingReview] = useState(false);

  const [aiCreateName, setAiCreateName] = useState("");
  const [isCreatingWithAi, setIsCreatingWithAi] = useState(false);
  const [aiCreateError, setAiCreateError] = useState("");

  // Sync aiCreateName with debouncedSearchTerm initially
  useEffect(() => {
    if (debouncedSearchTerm) {
      setAiCreateName(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);

  // Body scroll lock & ESC key listener for modal popups
  useEffect(() => {
    const isModalOpen = showRateModal || showReviewModal;
    if (isModalOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setShowRateModal(false);
        setShowReviewModal(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [showRateModal, showReviewModal]);

  // Shallow URL syncing for selected company
  useEffect(() => {
    if (selectedCompanyId) {
      const url = new URL(window.location.href);
      url.searchParams.set("company", selectedCompanyId);
      window.history.replaceState({}, "", url.toString());
    }
  }, [selectedCompanyId]);

  const fetchedCompaniesRef = useRef(false);
  const lastLoadedCompanyIdRef = useRef<string | null>(null);

  // Load companies from API on mount
  useEffect(() => {
    if (fetchedCompaniesRef.current) return;
    fetchedCompaniesRef.current = true;
    let isSubscribed = true;
    const controller = new AbortController();
    setLoadingCompanies(true);

    companiesApi
      .getCompanies({ page: 1, pageSize: 50 })
      .then((res) => {
        if (!isSubscribed) return;
        const comps = res.companies || [];
        setCompanyList(comps);
        
        // Check URL search parameter for company selection
        const urlParams = new URLSearchParams(window.location.search);
        const urlCompanyId = urlParams.get("company");

        if (urlCompanyId && comps.some((c) => c.id === urlCompanyId)) {
          setSelectedCompanyId(urlCompanyId);
          setIsMobileDetailView(true);
        } else if (comps.length > 0) {
          setSelectedCompanyId((prev) => prev || comps[0].id);
        }
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error("Failed to fetch companies from API:", err);
      })
      .finally(() => {
        if (isSubscribed) setLoadingCompanies(false);
      });

    return () => {
      isSubscribed = false;
      controller.abort();
      fetchedCompaniesRef.current = false;
    };
  }, []);

  // Sync external selected company
  useEffect(() => {
    if (selectedCompanyIdExternal) {
      if (selectedCompanyIdExternal !== "view-all") {
        setSelectedCompanyId(selectedCompanyIdExternal);
        setIsMobileDetailView(true);
      }
      if (onClearExternalCompany) onClearExternalCompany();
    }
  }, [selectedCompanyIdExternal, onClearExternalCompany]);

  // Load company specific reviews from API
  useEffect(() => {
    if (!selectedCompanyId) {
      setLiveReviews([]);
      return;
    }

    if (lastLoadedCompanyIdRef.current === selectedCompanyId) {
      return;
    }
    lastLoadedCompanyIdRef.current = selectedCompanyId;

    let isSubscribed = true;
    const controller = new AbortController();

    companiesApi
      .getCompanyReviews(selectedCompanyId)
      .then((revs) => {
        if (isSubscribed) {
          setLiveReviews(revs || []);
        }
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        console.error("Failed to fetch company reviews:", err);
        if (isSubscribed) setLiveReviews([]);
        lastLoadedCompanyIdRef.current = null;
      })
      .finally(() => {
        // Nothing here
      });

    return () => {
      isSubscribed = false;
      controller.abort();
      lastLoadedCompanyIdRef.current = null;
    };
  }, [selectedCompanyId]);

  useEffect(() => {
    if (liveReviews.length > 0) {
      const urlParams = new URLSearchParams(window.location.search);
      const highlightReviewId = urlParams.get("highlightReview");
      if (highlightReviewId) {
        setTimeout(() => {
          const element = document.getElementById(`review-${highlightReviewId}`);
          if (element) {
            element.scrollIntoView({ behavior: "smooth", block: "center" });
            element.classList.add("ring-2", "ring-[#0EA5E9]", "ring-offset-2");
            setTimeout(() => {
              element.classList.remove("ring-2", "ring-[#0EA5E9]", "ring-offset-2");
            }, 2000);
            
            const url = new URL(window.location.href);
            url.searchParams.delete("highlightReview");
            window.history.replaceState({}, "", url.toString());
          }
        }, 300);
      }
    }
  }, [liveReviews]);

  // Unique industries
  const industries = useMemo(() => {
    const set = new Set(companyList.map((c) => c.industry));
    return ["All", ...Array.from(set)];
  }, [companyList]);

  // Filtered companies list with debounced search term
  const filteredCompanies = useMemo(() => {
    return companyList.filter((c) => {
      const matchesSearch = c.name.toLowerCase().includes(debouncedSearchTerm.toLowerCase()) ||
                            c.location.toLowerCase().includes(debouncedSearchTerm.toLowerCase());
      const matchesIndustry = industryFilter === "All" || c.industry === industryFilter;
      return matchesSearch && matchesIndustry;
    });
  }, [companyList, debouncedSearchTerm, industryFilter]);


  const selectedCompany = companyList.find((c) => c.id === selectedCompanyId);

  const ratingIsHigh = (rating: number) => rating >= 3.0;

  const handleSelectCompany = (id: string) => {
    setSelectedCompanyId(id);
    setIsMobileDetailView(true);
  };

  // Open Rate Company Modal (Requires Authentication)
  const handleOpenRateModal = () => {
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    setShowRateModal(true);
    setRateScore(3.5);
    setRateSuccessMsg("");
  };

  // Submit Rate Only
  const handleSubmitRate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    if (!selectedCompany) return;

    setSubmittingRate(true);
    const userId = Number(currentUser.id) || 1;
    try {
      const currentRate = await companiesApi.rateCompany({
        userId,
        companyId: selectedCompany.id,
        rate: rateScore,
      });

      // Update local company average rating
      setCompanyList((prev) =>
        prev.map((c) =>
          c.id === selectedCompany.id ? { ...c, rating: currentRate } : c
        )
      );

      setRateSuccessMsg("Rating submitted successfully!");
      setTimeout(() => {
        setShowRateModal(false);
      }, 1000);
    } catch (err) {
      console.error("Failed to submit company rating:", err);
    } finally {
      setSubmittingRate(false);
    }
  };

  // Open Written Review Modal (Requires Authentication)
  const handleOpenReviewModal = () => {
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    setShowReviewModal(true);
    setReviewContent("");
    setReviewCategory("Workplace Culture");
    setReviewIsAnonymous(true);
  };

  // Submit Written Review Only
  const handleSubmitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    if (!reviewContent.trim() || !selectedCompany) return;

    setSubmittingReview(true);
    const userId = Number(currentUser.id) || 1;
    try {
      const newRev = await companiesApi.createReview({
        userId,
        companyId: selectedCompany.id,
        review: reviewContent,
        isAnonymous: reviewIsAnonymous,
      });

      newRev.category = reviewCategory;

      setLiveReviews((prev) => [newRev, ...prev]);
      setShowReviewModal(false);
    } catch (err) {
      console.error("Failed to submit review:", err);
    } finally {
      setSubmittingReview(false);
    }
  };

  const handleCreateWithAi = async () => {
    if (!currentUser) {
      if (onOpenAuthModal) onOpenAuthModal();
      return;
    }
    if (!aiCreateName.trim()) return;

    setIsCreatingWithAi(true);
    setAiCreateError("");
    try {
      const res = await companiesApi.createCompanyWithAi(aiCreateName.trim());
      if (res.company) {
        setCompanyList((prev) => {
          if (prev.some((c) => c.id === res.company!.id)) {
            return prev;
          }
          return [res.company!, ...prev];
        });
        setSelectedCompanyId(res.company.id);
        setIsMobileDetailView(true);
        setSearchTerm("");
        setAiCreateName("");
      } else {
        setAiCreateError("AI could not find or create this company.");
      }
    } catch (err: any) {
      console.error("AI creation failed:", err);
      let errMsg = "Failed to create company with AI.";
      if (err.data && err.data.detail) {
        errMsg = err.data.detail;
      }
      setAiCreateError(errMsg);
    } finally {
      setIsCreatingWithAi(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-5 h-[calc(100vh-140px)] md:h-[calc(100vh-100px)] overflow-hidden relative">
      {/* LEFT COLUMN: Directory List */}
      <div 
        className={`w-full md:w-5/12 lg:w-4/12 flex flex-col bg-white border border-slate-100 rounded-2xl overflow-hidden shadow-sm ${
          isMobileDetailView ? "hidden md:flex" : "flex"
        }`}
      >
        {/* Search and Filters */}
        <div className="p-4 border-b border-slate-100 space-y-3">
          <h2 className="text-sm font-bold text-slate-800 font-heading">
            Company Directory
          </h2>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search companies..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9]"
            />
          </div>
          <div className="flex items-center justify-between text-xs gap-2">
            <span className="text-slate-400 font-medium">Industry:</span>
            <select
              value={industryFilter}
              onChange={(e) => setIndustryFilter(e.target.value)}
              className="bg-slate-50 border border-slate-200 rounded-xl px-2 py-1 text-slate-750 focus:outline-none text-[11px]"
            >
              {industries.map((ind) => (
                <option key={ind} value={ind}>
                  {ind}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Directory List Container */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          {loadingCompanies ? (
            <p className="text-xs text-slate-400 italic text-center py-8">
              Loading companies from database...
            </p>
          ) : (
            filteredCompanies.map((comp) => {
              const isSelected = comp.id === selectedCompanyId;
              const isHigh = ratingIsHigh(comp.rating);
              return (
                <div
                  key={comp.id}
                  onClick={() => handleSelectCompany(comp.id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all duration-200 flex items-center justify-between ${
                    isSelected
                      ? "bg-[#0EA5E9]/5 border-[#0EA5E9] shadow-sm"
                      : "bg-white border-slate-100 hover:border-slate-200"
                  }`}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-10 h-10 rounded-lg bg-slate-900 flex items-center justify-center text-white font-extrabold text-xs flex-shrink-0">
                      {comp.logo.startsWith("http") ? (
                        <img src={comp.logo} alt={comp.name} className="w-full h-full rounded-lg object-cover" />
                      ) : (
                        comp.logo
                      )}
                    </div>
                    <div className="min-w-0">
                      <h3 className="font-bold text-slate-800 text-xs font-heading truncate flex items-center gap-1">
                        {comp.name}
                        {comp.verified && (
                          <CheckCircle className="w-3 h-3 fill-[#0EA5E9] stroke-white" />
                        )}
                      </h3>
                      <p className="text-[10px] text-slate-400 mt-0.5 truncate font-medium">
                        {comp.industry} • Founded {comp.foundedYear}
                      </p>
                    </div>
                  </div>

                  <span className={`text-xs font-bold px-2 py-1 rounded-lg flex items-center gap-0.5 ${
                    isHigh 
                      ? "bg-[#22C55E]/10 text-[#22C55E]" 
                      : "bg-[#EF4444]/10 text-[#EF4444]"
                  }`}>
                    <Star className="w-3 h-3 fill-current stroke-none" />
                    {comp.rating.toFixed(1)}
                  </span>
                </div>
              );
            })
          )}

          {!loadingCompanies && filteredCompanies.length === 0 && (
            <div className="p-5 rounded-2xl border border-dashed border-slate-250 bg-slate-50/70 backdrop-blur-xs flex flex-col items-center text-center space-y-4 font-body shadow-xs transition-all duration-300">
              <div className="w-10 h-10 rounded-xl bg-[#0EA5E9]/10 text-[#0EA5E9] flex items-center justify-center animate-pulse">
                <Building2 className="w-5 h-5" />
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-slate-800 font-heading">
                  Didn't find your company?
                </h4>
                <p className="text-[10px] text-slate-500 leading-normal max-w-[220px] mx-auto">
                  Create it instantly with AI! Gemini will research the website, location, logo, and social links.
                </p>
              </div>
              <div className="w-full space-y-2">
                <input
                  type="text"
                  placeholder="Enter company name..."
                  value={aiCreateName}
                  onChange={(e) => setAiCreateName(e.target.value)}
                  className="w-full px-3 py-2 bg-white border border-slate-200 rounded-xl text-xs placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9] shadow-xs"
                />
                <button
                  type="button"
                  onClick={handleCreateWithAi}
                  disabled={isCreatingWithAi || !aiCreateName.trim()}
                  className={`w-full py-2.5 rounded-xl text-[10px] font-bold font-heading uppercase tracking-wider transition-all flex items-center justify-center gap-1.5 shadow-sm ${
                    isCreatingWithAi || !aiCreateName.trim()
                      ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                      : "bg-[#0F172A] text-white hover:bg-slate-800 cursor-pointer shadow-slate-900/10"
                  }`}
                >
                  {isCreatingWithAi ? (
                    <>
                      <span className="w-3.5 h-3.5 border-2 border-slate-400 border-t-slate-800 rounded-full animate-spin"></span>
                      AI Researching...
                    </>
                  ) : (
                    "Create Company with AI ✨"
                  )}
                </button>
              </div>
              {aiCreateError && (
                <p className="text-[10px] text-red-500 font-bold bg-red-50/50 border border-red-100 rounded-lg px-2.5 py-1">{aiCreateError}</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* RIGHT COLUMN: Detail View */}
      <div 
        className={`flex-1 flex flex-col bg-white border border-slate-100 rounded-2xl overflow-y-auto shadow-sm ${
          !isMobileDetailView ? "hidden md:flex" : "flex"
        }`}
      >
        {selectedCompany ? (
          <>
            {/* Header / Banner */}
            <div className="relative h-28 lg:h-36 bg-slate-900 flex-shrink-0">
              <img
                src={selectedCompany.banner || "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&h=300&q=80"}
                alt={selectedCompany.name}
                className="w-full h-full object-cover opacity-80"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent" />
              
              <button
                onClick={() => setIsMobileDetailView(false)}
                className="md:hidden absolute top-4 left-4 bg-white/90 text-slate-800 p-2 rounded-xl backdrop-blur-sm shadow-md"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <div className="absolute bottom-4 left-5 right-5 flex justify-between items-end text-white">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white text-slate-800 font-extrabold text-sm flex items-center justify-center rounded-xl shadow-md border-2 border-white overflow-hidden">
                    {selectedCompany.logo.startsWith("http") ? (
                      <img src={selectedCompany.logo} alt={selectedCompany.name} className="w-full h-full object-cover" />
                    ) : (
                      selectedCompany.logo
                    )}
                  </div>
                  <div>
                    <h1 className="text-base lg:text-lg font-extrabold font-heading text-white flex items-center gap-1 leading-none">
                      {selectedCompany.name}
                      {selectedCompany.verified && (
                        <CheckCircle className="w-4 h-4 fill-[#0EA5E9] stroke-white" />
                      )}
                    </h1>
                    <p className="text-[10px] lg:text-xs text-slate-200 mt-1 leading-none font-medium">
                      {selectedCompany.industry} • Founded {selectedCompany.foundedYear}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="flex items-center gap-1 bg-white/20 px-2.5 py-1 rounded-lg backdrop-blur-sm">
                    <Star className="w-3.5 h-3.5 fill-amber-400 stroke-amber-400" />
                    <span className="text-xs font-bold text-white">
                      {selectedCompany.rating.toFixed(1)} / 4.0
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="px-5 py-4 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4 flex-shrink-0 bg-slate-50/20">
              <div className="text-xs text-slate-500 max-w-xl space-y-3">
                <p className="font-body italic leading-relaxed text-slate-600">
                  "{selectedCompany.description}"
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-2 text-slate-500 font-medium font-body">
                  <div className="flex items-center gap-2 bg-white/60 border border-slate-100/50 rounded-xl px-3 py-1.5 shadow-xs">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    <span><strong>Address:</strong> {selectedCompany.address || selectedCompany.location}</span>
                  </div>
                  <div className="flex items-center gap-2 bg-white/60 border border-slate-100/50 rounded-xl px-3 py-1.5 shadow-xs">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    <span><strong>Founded:</strong> {selectedCompany.foundedYear}</span>
                  </div>
                  <div className="flex items-center gap-2 bg-white/60 border border-slate-100/50 rounded-xl px-3 py-1.5 shadow-xs">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    <span><strong>Industry:</strong> {selectedCompany.industry}</span>
                  </div>
                  <div className="flex items-center gap-2 bg-white/60 border border-slate-100/50 rounded-xl px-3 py-1.5 shadow-xs">
                    <Star className="w-3.5 h-3.5 text-amber-500 fill-amber-500" />
                    <span><strong>Rating:</strong> {selectedCompany.rating.toFixed(1)} / 4.0</span>
                  </div>
                </div>

                {/* Social & Web Links */}
                <div className="flex items-center gap-2 pt-1 flex-wrap">
                  {selectedCompany.website && (
                    <a
                      href={selectedCompany.website.startsWith("http") ? selectedCompany.website : `https://${selectedCompany.website}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-[#0EA5E9] hover:underline font-bold text-[10px] flex items-center gap-1 cursor-pointer bg-white border border-slate-200/60 rounded-lg px-2.5 py-1.5 shadow-xs transition-colors hover:bg-slate-50"
                    >
                      Website 🌐
                    </a>
                  )}
                  {selectedCompany.linkedin && (
                    <a
                      href={selectedCompany.linkedin.startsWith("http") ? selectedCompany.linkedin : `https://${selectedCompany.linkedin}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-slate-700 hover:text-blue-700 font-bold text-[10px] flex items-center gap-1 cursor-pointer bg-white border border-slate-200/60 rounded-lg px-2.5 py-1.5 shadow-xs transition-colors hover:bg-slate-50"
                    >
                      LinkedIn 💼
                    </a>
                  )}
                  {selectedCompany.instagram && (
                    <a
                      href={selectedCompany.instagram.startsWith("http") ? selectedCompany.instagram : `https://${selectedCompany.instagram}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-pink-650 hover:text-pink-700 font-bold text-[10px] flex items-center gap-1 cursor-pointer bg-white border border-slate-200/60 rounded-lg px-2.5 py-1.5 shadow-xs transition-colors hover:bg-slate-50"
                    >
                      Instagram 📸
                    </a>
                  )}
                  {selectedCompany.facebook && (
                    <a
                      href={selectedCompany.facebook.startsWith("http") ? selectedCompany.facebook : `https://${selectedCompany.facebook}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-800 hover:text-blue-900 font-bold text-[10px] flex items-center gap-1 cursor-pointer bg-white border border-slate-200/60 rounded-lg px-2.5 py-1.5 shadow-xs transition-colors hover:bg-slate-50"
                    >
                      Facebook 👥
                    </a>
                  )}
                </div>
              </div>

              {/* Separated Rate vs Review Buttons */}
              <div className="flex items-center gap-2 self-start md:self-center">
                <button
                  onClick={handleOpenRateModal}
                  className="bg-amber-500 hover:bg-amber-600 text-white px-3.5 py-2.5 rounded-xl text-xs font-bold font-heading flex items-center justify-center gap-1.5 shadow-sm transition-all cursor-pointer"
                >
                  <Star className="w-3.5 h-3.5 fill-current stroke-none" />
                  Rate Company
                </button>

                <button
                  onClick={handleOpenReviewModal}
                  className="bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 text-white px-3.5 py-2.5 rounded-xl text-xs font-bold font-heading flex items-center justify-center gap-1.5 shadow-sm shadow-[#0EA5E9]/20 transition-all cursor-pointer"
                >
                  <PenTool className="w-3.5 h-3.5" />
                  Write Review
                </button>
              </div>
            </div>

            {/* Employee Reviews Thread */}
            <div className="p-5 space-y-4 bg-slate-50/50">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold text-slate-700 text-xs tracking-wider uppercase font-heading">
                  Decrypted Reviews ({liveReviews.length})
                </h3>
              </div>

              {liveReviews.map((rev) => (
                <ReviewCard
                  key={rev.id}
                  rev={rev}
                  currentUser={currentUser}
                  onOpenAuthModal={onOpenAuthModal}
                  onNavigateToUser={onNavigateToUser}
                />
              ))}

              {liveReviews.length === 0 && (
                <div className="text-center py-10 bg-white border border-slate-100 rounded-2xl">
                  <Building2 className="w-8 h-8 text-slate-300 mx-auto mb-2" />
                  <p className="text-xs text-slate-400 italic">
                    No written reviews for this company yet. Be the first to share your experience.
                  </p>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 bg-slate-50/50">
            <Building2 className="w-12 h-12 text-slate-300 mb-3 animate-pulse" />
            <h2 className="text-sm font-bold text-slate-700 font-heading">
              Select a Company
            </h2>
            <p className="text-xs text-slate-400 mt-1 max-w-xs leading-normal">
              Select any company from the left directory list to view ratings and employee reviews.
            </p>
          </div>
        )}
      </div>

      {/* 1. SEPARATE RATE COMPANY ONLY MODAL */}
      {showRateModal && selectedCompany && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-100 rounded-2xl shadow-xl max-w-md w-full p-6 space-y-4 font-body animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-extrabold text-slate-800 text-base font-heading">
                  Rate {selectedCompany.name}
                </h3>
                <p className="text-xs text-slate-400 font-medium">
                  Submit a score rating (1.0 to 4.0 scale)
                </p>
              </div>
              <button
                onClick={() => setShowRateModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {rateSuccessMsg ? (
              <div className="py-6 text-center text-xs font-bold text-green-600 bg-green-50 rounded-xl border border-green-200">
                {rateSuccessMsg}
              </div>
            ) : (
              <form onSubmit={handleSubmitRate} className="space-y-5 text-xs">
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-slate-700 flex items-center gap-1">
                      Rating Score
                    </span>
                    <span className={`font-extrabold text-sm px-2.5 py-1 rounded-lg ${
                      rateScore >= 3.0 ? "bg-[#22C55E]/10 text-[#22C55E]" : "bg-[#EF4444]/10 text-[#EF4444]"
                    }`}>
                      {rateScore.toFixed(1)} / 4.0
                    </span>
                  </div>
                  <div className="flex items-center gap-4">
                    <input
                      type="range"
                      min="1.0"
                      max="4.0"
                      step="0.1"
                      value={rateScore}
                      onChange={(e) => setRateScore(parseFloat(e.target.value))}
                      className="flex-1 accent-amber-500 cursor-pointer"
                    />
                    <div className="flex gap-1">
                      {[1, 2, 3, 4].map((star) => (
                        <Star
                          key={star}
                          className={`w-4 h-4 cursor-pointer ${
                            rateScore >= star
                              ? "fill-amber-400 stroke-amber-400"
                              : "text-slate-300"
                          }`}
                          onClick={() => setRateScore(star)}
                        />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setShowRateModal(false)}
                    className="px-4 py-2 font-bold text-slate-500 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer font-heading"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submittingRate}
                    className="px-5 py-2 font-bold text-white bg-amber-500 hover:bg-amber-600 rounded-xl shadow-sm transition-all font-heading cursor-pointer"
                  >
                    {submittingRate ? "Submitting..." : "Submit Rating"}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* 2. SEPARATE WRITE REVIEW ONLY MODAL */}
      {showReviewModal && selectedCompany && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-100 rounded-2xl shadow-xl max-w-lg w-full p-6 space-y-4 font-body animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <h3 className="font-extrabold text-slate-800 text-base font-heading">
                  Write Review for {selectedCompany.name}
                </h3>
                <p className="text-xs text-slate-400 font-medium">
                  Share your written workplace experience
                </p>
              </div>
              <button
                onClick={() => setShowReviewModal(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg transition-colors cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmitReview} className="space-y-4 text-xs">
              {/* Category selector */}
              <div className="flex flex-col gap-1">
                <label className="font-bold text-slate-600">Category</label>
                <select
                  value={reviewCategory}
                  onChange={(e) => setReviewCategory(e.target.value as Review["category"])}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9]"
                >
                  <option value="Workplace Culture">Workplace Culture</option>
                  <option value="Salary Data">Salary Data</option>
                  <option value="Misconduct">Misconduct</option>
                  <option value="Internal Policy">Internal Policy</option>
                  <option value="Management">Management</option>
                  <option value="Growth">Growth</option>
                  <option value="Interviews">Interviews</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              {/* Review text content */}
              <div className="flex flex-col gap-1">
                <label className="font-bold text-slate-600">Review Details</label>
                <textarea
                  required
                  rows={4}
                  placeholder={`Write your honest review of ${selectedCompany.name}...`}
                  value={reviewContent}
                  onChange={(e) => setReviewContent(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-slate-700 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] resize-none"
                />
              </div>

              {/* Anonymous vs Public Selector */}
              <div className="flex items-center justify-between bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                <span className="font-bold text-slate-600 flex items-center gap-1.5">
                  <ShieldCheck className="w-4 h-4 text-[#0EA5E9]" />
                  Posting Mode:
                </span>
                <div className="flex bg-white p-1 rounded-lg border border-slate-200">
                  <button
                    type="button"
                    onClick={() => setReviewIsAnonymous(true)}
                    className={`px-3 py-1 rounded-md font-bold transition-all cursor-pointer ${
                      reviewIsAnonymous
                        ? "bg-[#0F172A] text-white"
                        : "text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    <Lock className="w-3 h-3 inline mr-1 text-[#0EA5E9]" />
                    Anonymous 🔒
                  </button>
                  <button
                    type="button"
                    onClick={() => setReviewIsAnonymous(false)}
                    className={`px-3 py-1 rounded-md font-bold transition-all cursor-pointer ${
                      !reviewIsAnonymous
                        ? "bg-[#0F172A] text-white"
                        : "text-slate-500 hover:text-slate-800"
                    }`}
                  >
                    <UserIcon className="w-3 h-3 inline mr-1 text-slate-300" />
                    Public 👤
                  </button>
                </div>
              </div>

              {/* Actions */}
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowReviewModal(false)}
                  className="px-4 py-2 font-bold text-slate-500 hover:bg-slate-100 rounded-xl transition-colors cursor-pointer font-heading"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submittingReview || !reviewContent.trim()}
                  className={`px-5 py-2 font-bold text-white rounded-xl shadow-sm transition-all font-heading ${
                    submittingReview || !reviewContent.trim()
                      ? "bg-slate-200 text-slate-400 cursor-not-allowed"
                      : "bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 cursor-pointer shadow-[#0EA5E9]/20"
                  }`}
                >
                  {submittingReview ? "Submitting..." : "Submit Review"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
