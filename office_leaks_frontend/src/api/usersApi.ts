import { apiClient } from './apiClient';
import { adaptUser, adaptPost, type BackendUser, type BackendPost } from './adapters';
import type { User, Post } from '../types';

export interface FetchUsersParams {
  page?: number;
  pageSize?: number;
  fullName?: string;
}

export interface CreateUserPayload {
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  age?: number;
  country?: string;
  gender: 'MALE' | 'FEMALE';
  about?: string;
  current_company?: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface UpdateUserPayload {
  first_name?: string;
  last_name?: string;
  age?: number;
  gender?: 'MALE' | 'FEMALE';
  about?: string;
  current_company?: string;
  country?: string;
  user_timezone?: string;
}

export interface ChangePasswordPayload {
  old_password: string;
  new_password: string;
}

export const usersApi = {
  async getUsers(params: FetchUsersParams = {}): Promise<{
    users: User[];
    total: number;
    hasMore: boolean;
  }> {
    const query = new URLSearchParams();
    query.set('page', String(params.page || 1));
    query.set('page_size', String(params.pageSize || 10));
    if (params.fullName) query.set('full_name', params.fullName);

    const data = await apiClient.get<{
      users: BackendUser[];
      total_count?: number;
      total_pages?: number;
      current_page?: number;
    }>(`/user/?${query.toString()}`);

    const rawUsers = data.users || [];
    const users = rawUsers.map(adaptUser);
    const currentPage = data.current_page || params.page || 1;
    const totalPages = data.total_pages || 1;

    return {
      users,
      total: data.total_count || users.length,
      hasMore: currentPage < totalPages,
    };
  },

  async getUserById(userId: string): Promise<User> {
    const raw = await apiClient.get<BackendUser>(`/user/${userId}/`);
    return adaptUser(raw);
  },

  async getUserPosts(userId: string, page = 1): Promise<Post[]> {
    const data = await apiClient.get<{ posts: BackendPost[] }>(
      `/review/post/user/${userId}/?page=${page}&page_size=10`
    );
    return (data.posts || []).map((p) => adaptPost(p));
  },

  async createUser(payload: CreateUserPayload): Promise<{ id: number; username: string }> {
    return await apiClient.post<{ id: number; username: string }>('/user/create/', payload);
  },

  async login(payload: LoginPayload): Promise<LoginResponse> {
    return await apiClient.post<LoginResponse>('/user/login/', payload);
  },

  async updateUser(payload: UpdateUserPayload): Promise<User> {
    const raw = await apiClient.patch<BackendUser>('/user/update/', payload);
    return adaptUser(raw);
  },

  async changePassword(payload: ChangePasswordPayload): Promise<{ detail: string }> {
    return await apiClient.post<{ detail: string }>('/user/change-password/', payload);
  },

  async deleteAccount(): Promise<void> {
    await apiClient.delete('/user/delete/');
  },

  async uploadProfileImage(file: File): Promise<{ image_url: string }> {
    const formData = new FormData();
    formData.append('image', file);

    const token = localStorage.getItem('office_leaks_token');
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch('/api/user/upload-profile-image/', {
      method: 'POST',
      body: formData,
      headers,
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status}`);
    }

    return response.json();
  },
};
