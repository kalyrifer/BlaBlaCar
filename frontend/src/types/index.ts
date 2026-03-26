// Types for the application

export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  avatar_url?: string;
  rating?: number;
  created_at: string;
}

export interface Driver {
  id: string;
  name: string;
  avatar_url?: string;
  rating?: number;
  phone?: string;
}

export interface Trip {
  id: string;
  driver_id: string;
  driver: Driver;
  from_city: string;
  to_city: string;
  departure_date: string;
  departure_time: string;
  available_seats: number;
  price_per_seat: number;
  description?: string;
  status: 'active' | 'completed' | 'cancelled';
  created_at: string;
}

export interface TripRequest {
  id: string;
  trip_id: string;
  passenger_id: string;
  seats_requested: number;
  message?: string;
  status: 'pending' | 'confirmed' | 'rejected';
  created_at: string;
}

export interface Notification {
  id: string;
  type: 'request_received' | 'request_confirmed' | 'request_rejected' | 'trip_cancelled';
  title: string;
  message: string;
  is_read: boolean;
  related_trip_id?: string;
  related_request_id?: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface SearchParams {
  from_city: string;
  to_city: string;
  date?: string;
}

// ================== Chat Types ==================

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ConversationListItem {
  id: string;
  trip_id: string;
  other_user_id: string;
  other_user_name: string;
  trip_from_city: string;
  trip_to_city: string;
  last_message?: string;
  last_message_time?: string;
  unread_count: number;
}

export interface MessageListResponse {
  items: Message[];
  total: number;
}

export interface ConversationListResponse {
  items: ConversationListItem[];
  total: number;
}
