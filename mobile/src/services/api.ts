<![CDATA[/**
 * API Service
 * 
 * Handles all communication with the ARIA backend.
 */

import axios, { AxiosInstance } from 'axios';
import * as SecureStore from 'expo-secure-store';

// Types
export interface Location {
  lat: number;
  lng: number;
  address?: string;
}

export interface ChatContext {
  location?: Location;
  timezone?: string;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  context?: ChatContext;
}

export interface ActionDetails {
  id: string;
  type: string;
  status: string;
  details: Record<string, any>;
}

export interface ChatResponse {
  response_id: string;
  conversation_id: string;
  message: string;
  actions: ActionDetails[];
  suggested_responses: string[];
  requires_confirmation: boolean;
}

export interface ActionConfirmRequest {
  confirmed: boolean;
  modifications?: Record<string, any>;
}

export interface ActionConfirmResponse {
  action_id: string;
  status: string;
  result?: Record<string, any>;
}

export interface Task {
  id: string;
  type: string;
  status: string;
  created_at: string;
  updated_at: string;
  summary: string;
  progress: {
    current_step: string;
    total_steps: number;
    percentage: number;
  };
  metadata: Record<string, any>;
}

// API Configuration
const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000/v1';

class APIService {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.client.interceptors.request.use(async (config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );

    // Load token on init
    this.loadToken();
  }

  private async loadToken() {
    try {
      this.token = await SecureStore.getItemAsync('auth_token');
    } catch (error) {
      console.log('No stored token');
    }
  }

  async setToken(token: string) {
    this.token = token;
    await SecureStore.setItemAsync('auth_token', token);
  }

  async clearToken() {
    this.token = null;
    await SecureStore.deleteItemAsync('auth_token');
  }

  // Chat endpoints
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/chat/message', request);
    return response.data;
  }

  async confirmAction(
    actionId: string,
    request: ActionConfirmRequest
  ): Promise<ActionConfirmResponse> {
    const response = await this.client.post<ActionConfirmResponse>(
      `/chat/action/${actionId}/confirm`,
      request
    );
    return response.data;
  }

  async getConversation(conversationId: string) {
    const response = await this.client.get(`/chat/conversation/${conversationId}`);
    return response.data;
  }

  // Tasks endpoints
  async getTasks(filters?: { status?: string; type?: string }): Promise<{ tasks: Task[] }> {
    const response = await this.client.get('/tasks', { params: filters });
    return response.data;
  }

  async getTask(taskId: string): Promise<Task> {
    const response = await this.client.get(`/tasks/${taskId}`);
    return response.data;
  }

  async cancelTask(taskId: string, reason?: string) {
    const response = await this.client.post(`/tasks/${taskId}/cancel`, { reason });
    return response.data;
  }

  // Calendar endpoints
  async getEvents(startDate: string, endDate: string) {
    const response = await this.client.get('/calendar/events', {
      params: { start_date: startDate, end_date: endDate },
    });
    return response.data;
  }

  async checkAvailability(date: string, durationMinutes: number = 60) {
    const response = await this.client.post('/calendar/availability', {
      date,
      duration_minutes: durationMinutes,
    });
    return response.data;
  }

  // Transport endpoints
  async getRideEstimate(pickup: Location, dropoff: Location) {
    const response = await this.client.post('/transport/estimate', {
      pickup,
      dropoff,
    });
    return response.data;
  }

  // Medical endpoints
  async searchDoctors(specialty: string, location: string) {
    const response = await this.client.post('/medical/search', {
      specialty,
      location,
    });
    return response.data;
  }

  // Reminders endpoints
  async getReminders() {
    const response = await this.client.get('/reminders');
    return response.data;
  }

  async createReminder(message: string, triggerTime: string) {
    const response = await this.client.post('/reminders', {
      message,
      trigger_time: triggerTime,
    });
    return response.data;
  }

  // Health check
  async healthCheck() {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const api = new APIService();
]]>
