export interface User {
  id: string;
  name: string;
  username: string;
  avatar: string;
  title: string;
  companyName?: string;
  location: string;
  timezone?: string;
  bio?: string;
  isCurrentUser?: boolean;
  age?: number;
  gender?: 'MALE' | 'FEMALE';
  country?: string;
  firstName?: string;
  lastName?: string;
  defaultAvatarUrl?: string;
}

export interface Company {
  id: string;
  name: string;
  logo: string;
  industry: string;
  foundedYear: number;
  location: string;
  rating: number; // 1.0 - 5.0 (or 1.0 - 4.0 as per design rules)
  verified: boolean;
  banner?: string;
  description?: string;
  address?: string;
  website?: string;
  linkedin?: string;
  instagram?: string;
  facebook?: string;
}

export interface Review {
  id: string;
  companyId: string;
  companyName: string;
  rating?: number | null; // 1.0 - 4.0 scale as per design rules
  category: "Workplace Culture" | "Salary Data" | "Misconduct" | "Internal Policy" | "Management" | "Growth" | "Interviews" | "Other";
  tag?: string; // e.g. "Strategy Practice", "Upstream Engineering"
  salaryInfo?: string; // e.g. "SAR 28K–78K / month"
  title: string;
  content: string;
  authorName: string; // "Anonymous" or custom
  createdAt: string;
  likesCount: number;
  commentsCount: number;
  hasLiked?: boolean;
  user?: User | null;
  isAnonymous: boolean;
}

export interface Post {
  id: string;
  type: "text" | "review";
  author: User;
  createdAt: string;
  content: string;
  likesCount: number;
  commentsCount: number;
  hasLiked?: boolean;
  hasSaved?: boolean;
  category?: string;
  review?: Review; // Mutually exclusive with plain text if type is review
  companyTag?: {
    id: string;
    name: string;
  };
  comments?: Comment[];
  parentPost?: Post; // For reposts — the original post being quoted
}

export interface Comment {
  id: string;
  postId: string;
  authorName: string;
  authorTitle?: string;
  authorAvatar?: string;
  content: string;
  createdAt: string;
  likesCount?: number;
  hasLiked?: boolean;
  userId?: string;
  repliesCount?: number;
}

export interface NestedComment {
  id: string;
  parentCommentId: string;
  userId: string;
  authorName: string;
  authorAvatar?: string;
  parentCommentAuthorName?: string;
  content: string;
  createdAt: string;
  likesCount: number;
  hasLiked: boolean;
}

export interface Notification {
  id: string;
  type: "like" | "comment" | "mention" | "system";
  senderName: string;
  content: string;
  createdAt: string;
  isRead: boolean;
}
