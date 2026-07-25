import { apiClient } from './apiClient';
import { 
  adaptCompany, 
  adaptReview, 
  adaptComment, 
  adaptNestedComment,
  type BackendCompany, 
  type BackendReview, 
  type BackendComment,
  type BackendNestedComment 
} from './adapters';
import type { Company, Review, Comment, NestedComment } from '../types';

export interface FetchCompaniesParams {
  page?: number;
  pageSize?: number;
  nameSearch?: string;
  industry?: string;
  minRate?: number;
  maxRate?: number;
}

export const companiesApi = {
  async getCompanies(params: FetchCompaniesParams = {}): Promise<{
    companies: Company[];
    total: number;
    hasMore: boolean;
  }> {
    const query = new URLSearchParams();
    query.set('page', String(params.page || 1));
    query.set('page_size', String(params.pageSize || 10));
    if (params.nameSearch) query.set('name_search', params.nameSearch);
    if (params.industry && params.industry !== 'All Industries') query.set('industry', params.industry);
    if (params.minRate !== undefined) query.set('min_rate', String(params.minRate));
    if (params.maxRate !== undefined) query.set('max_rate', String(params.maxRate));

    const data = await apiClient.get<{
      companies: BackendCompany[];
      total_count?: number;
      total_pages?: number;
      current_page?: number;
    }>(`/company/?${query.toString()}`);

    const rawCompanies = data.companies || [];
    const companies = rawCompanies.map(adaptCompany);
    const currentPage = data.current_page || params.page || 1;
    const totalPages = data.total_pages || 1;

    return {
      companies,
      total: data.total_count || companies.length,
      hasMore: currentPage < totalPages,
    };
  },

  async getTopAndTrending(): Promise<{
    topRated: Company[];
    trending: { category: string; count: number }[];
  }> {
    const data = await apiClient.get<{
      top_rated: BackendCompany[];
      trending: { category: string; count: number }[];
    }>('/company/top-and-trending/');

    const topRatedRaw = data.top_rated || [];
    const trending = data.trending || [];

    return {
      topRated: topRatedRaw.map(adaptCompany),
      trending,
    };
  },

  async getCompanyReviews(companyId: string, page = 1): Promise<Review[]> {
    const data = await apiClient.get<{ reviews: BackendReview[] }>(
      `/review/review/?company_id=${companyId}&page=${page}&page_size=10`
    );
    return (data.reviews || []).map((r) => adaptReview(r));
  },

  async createReview(payload: {
    userId?: number;
    companyId: string;
    review: string;
    isAnonymous?: boolean;
  }): Promise<Review> {
    const raw = await apiClient.post<BackendReview>('/review/review/create/', {
      user_id: payload.userId || 1,
      company_id: Number(payload.companyId),
      review: payload.review,
      is_anonymous: payload.isAnonymous ?? true,
    });
    return adaptReview(raw);
  },

  async rateCompany(payload: {
    userId?: number;
    companyId: string;
    rate: number;
  }): Promise<number> {
    const res = await apiClient.post<{ current_rate: number }>('/company/rate/create/', {
      user_id: payload.userId || 1,
      company_id: Number(payload.companyId),
      rate: payload.rate,
    });
    return res.current_rate;
  },

  async searchCompanies(queryStr: string): Promise<Company[]> {
    if (!queryStr || !queryStr.trim()) return [];
    const data = await apiClient.get<{ companies: BackendCompany[] }>(
      `/company/search/?q=${encodeURIComponent(queryStr.trim())}`
    );
    return (data.companies || []).map(adaptCompany);
  },

  async likeReview(reviewId: string, userId = 1): Promise<void> {
    await apiClient.post('/review/review-like/create/', {
      user_id: userId,
      review_id: Number(reviewId),
    });
  },

  async unlikeReview(reviewId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/review-like/delete/${reviewId}/`, {
      user_id: userId,
    });
  },

  async getReviewComments(reviewId: string, page = 1): Promise<Comment[]> {
    const data = await apiClient.get<{ comments: BackendComment[] }>(
      `/review/review-comment/?review_id=${reviewId}&page=${page}&page_size=10`
    );
    return (data.comments || []).map(adaptComment);
  },

  async createReviewComment(reviewId: string, commentText: string, userId = 1): Promise<Comment> {
    const raw = await apiClient.post<BackendComment>('/review/review-comment/create/', {
      user_id: userId,
      review_id: Number(reviewId),
      comment: commentText,
    });
    return adaptComment(raw);
  },

  async likeReviewComment(commentId: string, userId = 1): Promise<void> {
    await apiClient.post('/review/review-comment-like/create/', {
      user_id: userId,
      review_comment_id: Number(commentId),
    });
  },

  async unlikeReviewComment(commentId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/review-comment-like/delete/${commentId}/`, {
      user_id: userId,
    });
  },

  async getNestedComments(parentCommentId: string, page = 1): Promise<NestedComment[]> {
    const data = await apiClient.get<{ comments: BackendNestedComment[] }>(
      `/review/review-nested-comment/?parent_comment_id=${parentCommentId}&page=${page}&page_size=10`
    );
    return (data.comments || []).map(adaptNestedComment);
  },

  async createNestedComment(parentCommentId: string, commentText: string, userId = 1): Promise<NestedComment> {
    const raw = await apiClient.post<BackendNestedComment>('/review/review-nested-comment/create/', {
      user_id: userId,
      parent_comment_id: Number(parentCommentId),
      comment_title: commentText,
    });
    return adaptNestedComment(raw);
  },

  async likeNestedComment(nestedCommentId: string, userId = 1): Promise<void> {
    await apiClient.post('/review/review-nested-comment-like/create/', {
      user_id: userId,
      review_nested_comment_id: Number(nestedCommentId),
    });
  },

  async unlikeNestedComment(nestedCommentId: string, userId = 1): Promise<void> {
    await apiClient.delete(`/review/review-nested-comment-like/delete/${nestedCommentId}/`, {
      user_id: userId,
    });
  },

  async createCompanyWithAi(companyName: string): Promise<{
    detail: string;
    exists?: boolean;
    company?: Company;
  }> {
    const res = await apiClient.post<{
      detail: string;
      exists?: boolean;
      company?: BackendCompany;
    }>('/company/create-ai/', { company_name: companyName });

    return {
      detail: res.detail,
      exists: res.exists,
      company: res.company ? adaptCompany(res.company) : undefined,
    };
  },
};

