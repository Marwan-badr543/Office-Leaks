import type { User, Company, Post, Notification } from "../types";

// Pure system configuration - all datasets are loaded dynamically via backend REST API
export const mockCurrentUser: User = {
  id: "1",
  name: "Corporate Member",
  username: "user_1",
  avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=1",
  title: "Verified Employee",
  location: "Riyadh, KSA",
};

export const mockCompanies: Company[] = [];
export const mockPosts: Post[] = [];
export const mockUsers: User[] = [];
export const mockNotifications: Notification[] = [];
