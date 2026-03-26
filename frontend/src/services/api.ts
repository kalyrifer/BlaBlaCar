import axios from 'axios';
import type { User, Trip, TripRequest, Notification, PaginatedResponse, SearchParams } from '../types';

// Axios instance for making HTTP requests
const axiosInstance = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

// Token storage - use localStorage for persistence
const getToken = (): string | null => {
  return localStorage.getItem('access_token');
};

const setToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('access_token', token);
  } else {
    localStorage.removeItem('access_token');
  }
};

const clearToken = () => {
  localStorage.removeItem('access_token');
};

// Request interceptor to add auth token
axiosInstance.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle 401 errors
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      clearToken();
    }
    return Promise.reject(error);
  }
);

// Auth - use axiosInstance for requests
export const authApi = {
  register: (data: { email: string; password: string; name: string; phone: string }) =>
    axiosInstance.post<User>('/auth/register', data),
  
  login: async (data: { email: string; password: string }) => {
    const response = await axiosInstance.post<{ access_token: string; user: User }>('/auth/login', data);
    if (response.data.access_token) {
      setToken(response.data.access_token);
    }
    return response;
  },
  
  logout: async () => {
    try {
      await axiosInstance.post('/auth/logout');
    } finally {
      clearToken();
    }
  },
  
  me: () => axiosInstance.get<User>('/auth/me'),
};

// Helper to check if user is logged in
export const isLoggedIn = (): boolean => {
  return !!getToken();
};

// Helper to get token (for debugging)
export const getAccessToken = getToken;

// Helper to set token (exported for use in stores)
export const setAccessToken = setToken;

// Trips
export const tripsApi = {
  search: (params: SearchParams) =>
    axiosInstance.get<PaginatedResponse<Trip>>('/trips', { params }),
  
  getById: (id: string) => axiosInstance.get<Trip>(`/trips/${id}`),
  
  create: (data: {
    from_city: string;
    to_city: string;
    departure_date: string;
    departure_time: string;
    available_seats: number;
    price_per_seat: number;
    description?: string;
  }) => axiosInstance.post<Trip>('/trips', data),
  
  update: (id: string, data: Partial<Trip>) => axiosInstance.put<Trip>(`/trips/${id}`, data),
  
  delete: (id: string) => axiosInstance.delete(`/trips/${id}`),
  
  getMyTrips: () => axiosInstance.get<PaginatedResponse<Trip>>('/trips/my/driver'),
  
  createRequest: (tripId: string, data: { seats_requested: number; message?: string }) =>
    axiosInstance.post<TripRequest>(`/trips/${tripId}/requests`, null, { params: data }),
  
  getTripRequests: (tripId: string) =>
    axiosInstance.get<PaginatedResponse<TripRequest>>(`/trips/${tripId}/requests`),
};

// Requests
export const requestsApi = {
  getMy: (status?: string) =>
    axiosInstance.get<PaginatedResponse<TripRequest>>('/requests/my', { params: { status } }),
  
  updateStatus: (requestId: string, status: 'confirmed' | 'rejected') =>
    axiosInstance.put<TripRequest>(`/requests/${requestId}`, { status }),
};

// Users
export const usersApi = {
  getById: (id: string) => axiosInstance.get(`/users/${id}`),
  
  update: (id: string, data: { name?: string; phone?: string }) =>
    axiosInstance.put(`/users/${id}`, data),
  
  getTrips: (id: string, role?: string) =>
    axiosInstance.get<PaginatedResponse<Trip>>(`/users/${id}/trips`, { params: { role } }),
};

// Notifications
export const notificationsApi = {
  getAll: (isRead?: boolean) =>
    axiosInstance.get<PaginatedResponse<Notification>>('/notifications', { params: { is_read: isRead } }),
  
  markAsRead: (id: string) => axiosInstance.put(`/notifications/${id}/read`),
  
  markAllAsRead: () => axiosInstance.put('/notifications/read-all'),
};

// Convenience exports - re-export all APIs under one object
export const api = {
  // Auth
  register: authApi.register,
  login: authApi.login,
  logout: authApi.logout,
  me: authApi.me,
  
  // Trips
  search: tripsApi.search,
  getById: tripsApi.getById,
  createTrip: tripsApi.create,
  updateTrip: tripsApi.update,
  deleteTrip: tripsApi.delete,
  getMyTrips: tripsApi.getMyTrips,
  createRequest: tripsApi.createRequest,
  getTripRequests: tripsApi.getTripRequests,
  
  // Requests
  getMyRequests: requestsApi.getMy,
  updateRequestStatus: requestsApi.updateStatus,
  
  // Users
  getUserById: usersApi.getById,
  updateUser: usersApi.update,
  getUserTrips: usersApi.getTrips,
  
  // Notifications
  getNotifications: notificationsApi.getAll,
  markNotificationRead: notificationsApi.markAsRead,
  markAllNotificationsRead: notificationsApi.markAllAsRead,
};

export default api;
