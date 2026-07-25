import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { X, Repeat2, Lock, CheckCircle, ShieldCheck, User as UserIcon } from "lucide-react";
import type { Post, Review, User } from "../types";

interface RepostModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentUser: User;
  /** The original post being reposted (for feed leaks) */
  parentPost?: Post;
  /** The review being reposted (for company page reviews) */
  review?: Review;
  onSubmit: (content: string, isAnonymous: boolean) => Promise<void>;
}

export const RepostModal: React.FC<RepostModalProps> = ({
  isOpen,
  onClose,
  currentUser,
  parentPost,
  review,
  onSubmit,
}) => {
  const [content, setContent] = useState("");
  const [isAnonymousShare, setIsAnonymousShare] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!isOpen) return;
    document.body.style.overflow = "hidden";
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(content.trim(), isAnonymousShare);
      setContent("");
      onClose();
    } catch (err) {
      console.error("Failed to repost:", err);
    } finally {
      setSubmitting(false);
    }
  };

  // Determine what content to show in the embedded preview
  const parentContent = parentPost
    ? parentPost.review
      ? parentPost.review.content
      : parentPost.content
    : review
      ? review.content
      : "";

  const parentAuthor = parentPost
    ? parentPost.author.name
    : review
      ? review.authorName
      : "Unknown";

  const parentCategory = parentPost
    ? parentPost.category
    : review
      ? review.category
      : undefined;

  const isAnonymous = parentPost
    ? parentPost.author.id === "anon"
    : review
      ? review.isAnonymous
      : false;

  const parentCreatedAt = parentPost
    ? parentPost.createdAt
    : review
      ? review.createdAt
      : "";

  return createPortal(
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-slate-100 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden font-body animate-in fade-in zoom-in-95 duration-150 relative">
        {/* Header */}
        <div className="bg-[#0F172A] p-5 text-white flex items-center justify-between border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-[#0EA5E9] text-[#0F172A] rounded-xl flex items-center justify-center shadow-md shadow-[#0EA5E9]/20">
              <Repeat2 className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <h2 className="text-sm font-extrabold font-heading">Repost Leak</h2>
              <p className="text-[10px] text-slate-300 mt-0.5">Share with your own commentary</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-xl transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* User input area */}
          <div className="flex gap-3">
            <img
              src={currentUser.avatar}
              alt={currentUser.name}
              className="w-10 h-10 rounded-xl object-cover flex-shrink-0 border border-slate-100"
            />
            <div className="flex-1">
              <p className="text-xs font-bold text-slate-800 font-heading">{currentUser.name}</p>
              <textarea
                autoFocus
                placeholder="Add your thoughts about this leak..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={3}
                className="w-full mt-2 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-[#0EA5E9] focus:border-[#0EA5E9] resize-none font-body"
              />
            </div>
          </div>

          {/* Identity Mode Selector (Anonymous vs Public Profile) */}
          <div className="flex items-center justify-between bg-slate-50 p-2 rounded-xl border border-slate-100">
            <span className="text-xs font-bold text-slate-700 font-heading flex items-center gap-1.5">
              <ShieldCheck className="w-4 h-4 text-[#0EA5E9]" />
              Repost As:
            </span>
            <div className="flex bg-white p-1 rounded-lg border border-slate-200/80 shadow-xs">
              <button
                type="button"
                onClick={() => setIsAnonymousShare(true)}
                className={`px-3 py-1 rounded-md text-xs font-bold font-heading flex items-center gap-1.5 transition-all cursor-pointer ${
                  isAnonymousShare
                    ? "bg-[#0F172A] text-white shadow-sm"
                    : "text-slate-500 hover:text-slate-800"
                }`}
              >
                <Lock className="w-3 h-3 text-[#0EA5E9]" />
                Anonymous 🔒
              </button>
              <button
                type="button"
                onClick={() => setIsAnonymousShare(false)}
                className={`px-3 py-1 rounded-md text-xs font-bold font-heading flex items-center gap-1.5 transition-all cursor-pointer ${
                  !isAnonymousShare
                    ? "bg-[#0F172A] text-white shadow-sm"
                    : "text-slate-500 hover:text-slate-800"
                }`}
              >
                <UserIcon className="w-3 h-3 text-slate-400" />
                Public Profile 👤
              </button>
            </div>
          </div>

          {/* Embedded parent post/review preview */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-4 space-y-2.5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {isAnonymous ? (
                  <div className="w-8 h-8 rounded-lg bg-[#0F172A] text-white flex items-center justify-center text-[10px] font-extrabold font-heading">
                    <Lock className="w-3.5 h-3.5 text-[#0EA5E9]" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-lg bg-slate-200 flex items-center justify-center text-[10px] font-extrabold text-slate-600 overflow-hidden">
                    {parentPost?.author.avatar ? (
                      <img src={parentPost.author.avatar} alt={parentAuthor} className="w-full h-full object-cover" />
                    ) : (
                      parentAuthor.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase()
                    )}
                  </div>
                )}
                <div>
                  <span className="text-[11px] font-bold text-slate-700 font-heading">{parentAuthor}</span>
                  {parentPost?.companyTag && (
                    <span className="ml-1.5 text-[9px] text-[#0EA5E9] font-bold bg-[#0EA5E9]/10 px-1.5 py-0.5 rounded-full inline-flex items-center gap-0.5">
                      <CheckCircle className="w-2 h-2 fill-[#0EA5E9] stroke-white" />
                      {parentPost.companyTag.name}
                    </span>
                  )}
                </div>
              </div>
              <span className="text-[9px] text-slate-400 font-medium">{parentCreatedAt}</span>
            </div>

            {/* Category tag */}
            {parentCategory && (
              <span className="inline-block text-[10px] font-semibold px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded-md border border-indigo-100/50">
                {parentCategory}
              </span>
            )}

            {/* Review title if applicable */}
            {(parentPost?.review || review) && (
              <h4 className="font-bold text-slate-800 text-xs font-heading leading-snug">
                {parentPost?.review?.title || review?.title}
              </h4>
            )}

            {/* Content */}
            <p className="text-[11px] text-slate-600 leading-relaxed font-body line-clamp-4">
              {parentContent}
            </p>
          </div>

          {/* Submit */}
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className={`w-full py-3 rounded-xl font-extrabold text-white text-xs font-heading shadow-md transition-all ${
              submitting
                ? "bg-slate-300 text-slate-500 cursor-not-allowed"
                : "bg-[#0EA5E9] hover:bg-[#0EA5E9]/90 active:scale-[0.98] cursor-pointer shadow-[#0EA5E9]/20"
            }`}
          >
            {submitting ? "Reposting..." : "Repost to Feed"}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};
