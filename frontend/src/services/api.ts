import axios from 'axios';
import type { User, Trip, TripRequest, Notification, PaginatedResponse, SearchParams } from '../types';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

// Auth
export const authApi = {
  register: (data: { email: string; password: string; name: string; phone: string }) =>
    api.post<User>('/auth/register', data),
  
  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string; user: User }>('/auth/login', data),
  
  logout: () => api.post('/auth/logout'),
  
  me: () => api.get<User>('/auth/me'),
};

// Trips
export const tripsApi = {
  search: (params: SearchParams) =>
    api.get<PaginatedResponse<Trip>>('/trips', { params }),
  
  getById: (id: string) => api.get<Trip>(`/trips/${id}`),
  
  create: (data: {
    from_city: string;
    to_city: string;
    departure_date: string;
    departure_time: string;
    available_seats: number;
    price_per_seat: number;
    description?: string;
  }) => api.post<Trip>('/trips', data),
  
  update: (id: string, data: Partial<Trip>) => api.put<Trip>(`/trips/${id}`, data),
  
  delete: (id: string) => api.delete(`/trips/${id}`),
  
  getMyTrips: () => api.get<PaginatedResponse<Trip>>('/trips/my/driver'),
  
  createRequest: (tripId: string, data: { seats_requested: number; message?: string }) =>
    api.post<TripRequest>(`/trips/${tripId}/requests`, null, { params: data }),
  
  getTripRequests: (tripId: string) =>
    api.get<PaginatedResponse<TripRequest>>(`/trips/${tripId}/requests`),
};

// Requests
export const requestsApi = {
  getMy: (status?: string) =>
    api.get<PaginatedResponse<TripRequest>>('/requests/my', { params: { status } }),
  
  updateStatus: (requestId: string, status: 'confirmed' | 'rejected') =>
    api.put<TripRequest>(`/requests/${requestId}`, { status }),
};

// Users
export const usersApi = {
  getById: (id: string) => api.get(`/users/${id}`),
  
  update: (id: string, data: { name?: string; phone?: string }) =>
    api.put(`/users/${id}`, data),
  
  getTrips: (id: string, role?: string) =>
    api.get<PaginatedResponse<Trip>>(`/users/${id}/trips`, { params: { role } }),
};

// Notifications
export const notificationsApi = {
  getAll: (isRead?: boolean) =>
    api.get<PaginatedResponse<Notification>>('/notifications', { params: { is_read: isRead } }),
  
  markAsRead: (id: string) => api.put(`/notifications/${id}/read`),
  
  markAllAsRead: () => api.put('/notifications/read-all'),
};

export default api;
