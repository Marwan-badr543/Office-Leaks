import { apiClient } from './apiClient';
import { 
  adaptPost, 
  adaptComment, 
  adaptNestedComment,
  DISPLAY_TO_BACKEND_CAT, 
  type BackendPost, 
  type BackendComment,
  type BackendNestedComment 
} from './adapters';
import type { Post, Comment, NestedComment } from '../types';

export interface FetchPostsParams {
  page?: number;
  pageSize?: number;
  ordering?: 'recent' | 'popular';
  category?: string;
}

export interface FetchPostsResponse {
  posts: Post[];
  total: number;
  page: number;
  hasMore: boolean;
}

export const postsApi = {
  async getPosts(params: FetchPostsParams = {}): Promise<FetchPostsResponse> {
    const query = new URLSearchParams();
    query.set('page', String(params.page || 1));
    query.set('page_size', String(params.pageSize || 10));
    if (params.ordering) query.set('ordering', params.ordering);
    if (params.category && params.category !== 'All Leaks') {
      const backendCat = DISPLAY_TO_BACKEND_CAT[params.category] || params.category;
      query.set('category', backendCat);
    }

    const data = await apiClient.get<{
      posts: BackendPost[];
      total_count?: number;
      total_pages?: number;
      current_page?: number;
    }>(`/review/post/?${query.toString()}`);

    const rawPosts = data.posts || [];
    const posts = rawPosts.map((p) => adaptPost(p));
    const currentPage = data.current_page || params.page || 1;
    const totalPages = data.total_pages || 1;

    return {
      posts,
      total: data.total_count || posts.length,
      page: currentPage,
      hasMore: currentPage < totalPages,
    };
  },

  async createPost(payload: {
    userId?: number;
    content?: string;
    reviewId?: number;
    companyId?: number;
    category?: string;
    isAnonymous?: boolean;
    parentPostId?: number;
  }): Promise<Post> {
    const displayCategory = payload.category || 'Workplace Culture';
    const backendCategory = DISPLAY_TO_BACKEND_CAT[displayCategory] || 'OTHER';

    const requestBody = {
      user_id: payload.userId || 1,
      content: payload.content || '',
      review_id: payload.reviewId,
      company_id: payload.companyId,
      category: backendCategory,
      is_anonymous: payload.isAnonymous ?? true,
      parent_post_id: payload.parentPostId,
    };

    const rawPost = await apiClient.post<BackendPost>('/review/post/create/', requestBody);
    return adaptPost(rawPost);
  },

  async likePost(postId: string, userId = 1): Promise<void> {
    await apiClient.post('/review/post-like/create/', {
      user_id: userId,
      post_id: Number(postId),
    });
  },

  async unlikePost(postId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/post-like/delete/${postId}/`, {
      user_id: userId,
    });
  },

  async deletePost(postId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/post/delete/${postId}/`, {
      user_id: userId,
    });
  },

  async getComments(postId: string, page = 1): Promise<Comment[]> {
    const data = await apiClient.get<{ comments: BackendComment[] }>(
      `/review/post-comment/?post_id=${postId}&page=${page}&page_size=10`
    );
    return (data.comments || []).map(adaptComment);
  },

  async createComment(postId: string, commentText: string, userId = 1): Promise<Comment> {
    const raw = await apiClient.post<BackendComment>('/review/post-comment/create/', {
      user_id: userId,
      post_id: Number(postId),
      comment: commentText,
    });
    return adaptComment(raw);
  },

  async likePostComment(commentId: string, userId = 1): Promise<void> {
    await apiClient.post('/review/post-comment-like/create/', {
      user_id: userId,
      post_comment_id: Number(commentId),
    });
  },

  async unlikePostComment(commentId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/post-comment-like/delete/${commentId}/`, {
      user_id: userId,
    });
  },

  async getNestedComments(parentCommentId: string, page = 1): Promise<NestedComment[]> {
    const data = await apiClient.get<{ comments: BackendNestedComment[] }>(
      `/review/post-nested-comment/?parent_comment_id=${parentCommentId}&page=${page}&page_size=10`
    );
    return (data.comments || []).map(adaptNestedComment);
  },

  async createNestedComment(parentCommentId: string, commentText: string, userId = 1): Promise<NestedComment> {
    const raw = await apiClient.post<BackendNestedComment>('/review/post-nested-comment/create/', {
      user_id: userId,
      parent_comment_id: Number(parentCommentId),
      comment_title: commentText,
    });
    return adaptNestedComment(raw);
  },

  async likeNestedComment(nestedCommentId: string, userId = 1): Promise<void> {
    await apiClient.post('/review/post-nested-comment-like/create/', {
      user_id: userId,
      post_nested_comment_id: Number(nestedCommentId),
    });
  },

  async unlikeNestedComment(nestedCommentId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/post-nested-comment-like/delete/${nestedCommentId}/`, {
      user_id: userId,
    });
  },
};
