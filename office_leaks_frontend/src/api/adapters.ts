import type { Post, User, Company, Review, Comment, NestedComment } from '../types';
import maleAvatar from '../assets/male_avatar.svg';
import femaleAvatar from '../assets/female_avatar.svg';

export interface BackendUser {
  id: number;
  username: string;
  first_name?: string;
  last_name?: string;
  full_name?: string;
  email?: string;
  role?: string;
  country?: string;
  about?: string;
  age?: number;
  gender?: 'MALE' | 'FEMALE';
  current_company?: string;
  is_active?: boolean;
  profile_image?: string | null;
  profile_image_url?: string | null;
  default_avatar_url?: string | null;
  user_timezone?: string;
}

export interface BackendCompany {
  id: number;
  name: string;
  industry?: string;
  description?: string;
  logo_filename?: string | null;
  logo_url?: string | null;
  average_rate?: number;
  current_rate?: number;
  founded_year?: number;
  founded_at?: string;
  location?: string;
  address?: string;
  website?: string;
  linkedin?: string;
  instagram?: string;
  facebook?: string;
}

export interface BackendReview {
  id: number;
  company_id: number;
  company_name?: string;
  review: string;
  is_anonymous: boolean;
  likes_number: number;
  comments_number: number;
  user_id: number;
  creation?: string;
  rate?: number | null;
  category?: string;
  user?: BackendUser | null;
  company?: BackendCompany | null;
  has_liked?: boolean;
}

export interface BackendPost {
  id: number;
  creation: string;
  content: string;
  is_anonymous: boolean;
  likes_number: number;
  comments_number: number;
  user_id: number;
  review?: BackendReview | null;
  company_id?: number | null;
  company_name?: string | null;
  company?: { id: number; name: string } | null;
  category?: string | null;
  user?: BackendUser | null;
  has_liked?: boolean;
  parent_post?: BackendPost | null;
}

export interface BackendComment {
  id: number;
  post_id?: number;
  review_id?: number;
  comment: string;
  user_id: number;
  creation?: string;
  user_name?: string;
  likes_number?: number;
  has_liked?: boolean;
  user_avatar?: string;
  replies_count?: number;
}

/**
 * Returns the correct default avatar based on gender.
 * Male avatar is the fallback when gender is unknown.
 */
export function getDefaultAvatar(gender?: string | null): string {
  if (gender === 'FEMALE') return femaleAvatar;
  return maleAvatar;
}

export function adaptUser(raw: BackendUser): User {
  const fullName = raw.full_name || (raw.first_name && raw.last_name ? `${raw.first_name} ${raw.last_name}` : undefined) || raw.username || `User #${raw.id}`;
  const avatarUrl = raw.profile_image_url || raw.profile_image || getDefaultAvatar(raw.gender);
  return {
    id: String(raw.id),
    name: fullName,
    username: raw.username || `user_${raw.id}`,
    avatar: avatarUrl,
    title: raw.role ? `${raw.role} Specialist` : 'Corporate Professional',
    companyName: raw.current_company || undefined,
    location: raw.country || 'Riyadh, KSA',
    bio: raw.about || 'Corporate insider & advocate for workplace transparency.',
    timezone: raw.user_timezone || 'GMT+3',
    age: raw.age,
    gender: raw.gender,
    country: raw.country,
    firstName: raw.first_name,
    lastName: raw.last_name,
    defaultAvatarUrl: raw.default_avatar_url || undefined,
  };
}

export const BACKEND_TO_DISPLAY_CAT: Record<string, Review['category']> = {
  "CULTURE": "Workplace Culture",
  "SALARIES": "Salary Data",
  "ISSUES": "Misconduct",
  "POLICIES": "Internal Policy",
  "MANAGEMENT": "Management",
  "GROWTH": "Growth",
  "INTERVIEWS": "Interviews",
  "OTHER": "Other",
  // Fallbacks for frontend self-consistency
  "Workplace Culture": "Workplace Culture",
  "Salary Data": "Salary Data",
  "Misconduct": "Misconduct",
  "Internal Policy": "Internal Policy",
  "Management": "Management",
  "Growth": "Growth",
  "Interviews": "Interviews",
  "Other": "Other"
};

export const DISPLAY_TO_BACKEND_CAT: Record<string, string> = {
  "Workplace Culture": "CULTURE",
  "Salary Data": "SALARIES",
  "Misconduct": "ISSUES",
  "Internal Policy": "POLICIES",
  "Management": "MANAGEMENT",
  "Growth": "GROWTH",
  "Interviews": "INTERVIEWS",
  "Other": "OTHER",
  "General Discussion": "OTHER"
};

export function adaptCompany(raw: BackendCompany): Company {
  const rate = raw.current_rate !== undefined ? raw.current_rate : raw.average_rate;
  const ratingVal = (rate === undefined || rate === null || rate === 0) ? 3.0 : Number(rate.toFixed(1));
  return {
    id: String(raw.id),
    name: raw.name,
    logo: raw.logo_url || raw.logo_filename || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(raw.name)}`,
    industry: raw.industry || 'Technology & Enterprise',
    foundedYear: raw.founded_year || (raw.founded_at ? new Date(raw.founded_at).getFullYear() : 2018),
    location: raw.address || raw.location || 'Saudi Arabia',
    rating: ratingVal,
    verified: true,
    description: raw.description || `${raw.name} enterprise profile on Office Leaks.`,
    address: raw.address,
    website: raw.website,
    linkedin: raw.linkedin,
    instagram: raw.instagram,
    facebook: raw.facebook,
  };
}

export function formatCreationTime(creationStr: string): string {
  const created = new Date(creationStr);
  const now = new Date();

  const diffMs = Math.max(0, now.getTime() - created.getTime());

  // Less than 24 hours elapsed
  if (diffMs < 24 * 3600000) {
    if (diffMs < 60000) {
      return "just now";
    }
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 60) {
      return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`;
    }
    const diffHours = Math.floor(diffMs / 3600000);
    return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`;
  }

  // Between 24 hours and 48 hours elapsed
  if (diffMs < 48 * 3600000) {
    return "yesterday";
  }

  // Otherwise, show the date, not datetime
  return created.toLocaleDateString();
}

export function adaptReview(raw: BackendReview, companyNameFallback?: string): Review {
  const rawCat = raw.category || '';
  const cat = BACKEND_TO_DISPLAY_CAT[rawCat] || 'Workplace Culture';
  const formattedCreation = raw.creation ? formatCreationTime(raw.creation) : 'Recently';
  const isAnon = raw.is_anonymous || !raw.user_id;

  return {
    id: String(raw.id),
    companyId: String(raw.company_id),
    companyName: raw.company_name || companyNameFallback || `Company #${raw.company_id}`,
    rating: (raw.rate !== undefined && raw.rate !== null) ? Number(raw.rate.toFixed(1)) : null,
    category: cat,
    title: raw.review.length > 50 ? `${raw.review.slice(0, 50)}...` : raw.review,
    content: raw.review,
    authorName: isAnon ? 'Anonymous Member' : (raw.user?.full_name || raw.user?.username || `User #${raw.user_id}`),
    createdAt: formattedCreation,
    likesCount: raw.likes_number || 0,
    commentsCount: raw.comments_number || 0,
    hasLiked: raw.has_liked ?? false,
    user: isAnon ? null : (raw.user ? adaptUser(raw.user) : null),
    isAnonymous: isAnon,
  };
}

export function adaptPost(raw: BackendPost, companyLookup?: Record<string, string>): Post {
  const isReview = Boolean(raw.review);
  const isRepostedReview = isReview && (Boolean(raw.content) || (raw.user_id !== raw.review?.user_id));
  const companyName = raw.company?.name || raw.company_name || (raw.company_id ? companyLookup?.[String(raw.company_id)] : undefined);
  const companyId = raw.company?.id ? String(raw.company.id) : (raw.company_id ? String(raw.company_id) : undefined);
  const isAnon = raw.is_anonymous || !raw.user_id;

  const author: User = isAnon
    ? {
        id: 'anon',
        name: (isReview && !isRepostedReview) ? `${companyName || 'Corporate'} Member` : 'Anonymous Member',
        username: 'anonymous',
        avatar: '',
        title: (isReview && !isRepostedReview) ? 'Verified Member' : 'Anonymous Member',
        location: 'Encrypted',
      }
    : raw.user
      ? adaptUser(raw.user)
      : {
          id: String(raw.user_id),
          name: `User #${raw.user_id}`,
          username: `user_${raw.user_id}`,
          avatar: getDefaultAvatar(),
          title: 'Corporate Insider',
          location: 'Saudi Arabia',
        };

  const reviewAdapted = raw.review
    ? adaptReview(raw.review, companyName)
    : undefined;

  const rawCat = raw.category || '';
  const displayCat = BACKEND_TO_DISPLAY_CAT[rawCat] || (reviewAdapted ? reviewAdapted.category : 'Other');

  // Recursively adapt parent_post for reposts (one level deep)
  const parentPost = raw.parent_post ? adaptPost(raw.parent_post, companyLookup) : undefined;

  return {
    id: String(raw.id),
    type: (isReview && !isRepostedReview) ? 'review' : 'text',
    author,
    createdAt: raw.creation ? formatCreationTime(raw.creation) : 'Recently',
    content: (isReview && !isRepostedReview) 
      ? (raw.content || (reviewAdapted ? reviewAdapted.title : '')) 
      : (raw.content || ''),
    likesCount: raw.likes_number || 0,
    commentsCount: raw.comments_number || 0,
    hasLiked: raw.has_liked ?? false,
    hasSaved: false,
    category: displayCat,
    review: reviewAdapted,
    companyTag: companyId
      ? { id: companyId, name: companyName || `Company #${companyId}` }
      : undefined,
    parentPost,
  };
}

export function adaptComment(raw: BackendComment): Comment {
  return {
    id: String(raw.id),
    postId: String(raw.post_id || raw.review_id || 0),
    authorName: raw.user_name || `User #${raw.user_id}`,
    content: raw.comment,
    createdAt: raw.creation ? formatCreationTime(raw.creation) : 'Recently',
    likesCount: raw.likes_number || 0,
    hasLiked: raw.has_liked ?? false,
    userId: String(raw.user_id),
    authorAvatar: raw.user_avatar || getDefaultAvatar(),
    repliesCount: raw.replies_count || 0,
  };
}

export interface BackendNestedComment {
  id: number;
  parent_comment_id: number;
  comment_title: string;
  user_id: number;
  creation?: string;
  user_name?: string;
  likes_number?: number;
  has_liked?: boolean;
  parent_comment_author_name?: string;
  user_avatar?: string;
}

export function adaptNestedComment(raw: BackendNestedComment): NestedComment {
  return {
    id: String(raw.id),
    parentCommentId: String(raw.parent_comment_id),
    userId: String(raw.user_id),
    authorName: raw.user_name || `User #${raw.user_id}`,
    parentCommentAuthorName: raw.parent_comment_author_name,
    content: raw.comment_title,
    createdAt: raw.creation ? formatCreationTime(raw.creation) : 'Recently',
    likesCount: raw.likes_number || 0,
    hasLiked: raw.has_liked ?? false,
    authorAvatar: raw.user_avatar || getDefaultAvatar(),
  };
}
