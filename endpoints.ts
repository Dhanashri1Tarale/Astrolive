import { api } from './client'
import type {
  User, Astrologer, Consultation, Goal, ImportantDate,
  Journey, ShareCard, Notification, Analytics, Insight,
} from './types'

export const AuthApi = {
  demo: () => api<{ token: string; user: User }>('/api/auth/demo', { method: 'POST' }),
  login: (email: string, password: string) =>
    api<{ token: string; user: User }>('/api/auth/login', { method: 'POST', body: { email, password } }),
  register: (email: string, name: string, password: string) =>
    api<{ token: string; user: User }>('/api/auth/register', { method: 'POST', body: { email, name, password } }),
  me: () => api<User>('/api/auth/me'),
}

export const AstrologerApi = {
  list: () => api<Astrologer[]>('/api/astrologers'),
  get: (id: string) => api<Astrologer>(`/api/astrologers/${id}`),
}

export const ConsultationApi = {
  list: () => api<Consultation[]>('/api/consultations'),
  get: (id: string) => api<Consultation>(`/api/consultations/${id}`),
  create: (astrologer_id: string, topic: string, user_message: string) =>
    api<Consultation>('/api/consultations', { method: 'POST', body: { astrologer_id, topic, user_message } }),
  saveToMemory: (id: string) => api<Insight>(`/api/consultations/${id}/save-to-memory`, { method: 'POST' }),
}

export const GoalApi = {
  list: () => api<Goal[]>('/api/goals'),
  create: (title: string, category: string, description: string, insight_id?: string, actions?: string[]) =>
    api<Goal>('/api/goals', { method: 'POST', body: { title, category, description, insight_id, actions: actions || [] } }),
  completeAction: (actionId: string) =>
    api(`/api/goals/actions/${actionId}/complete`, { method: 'POST' }),
}

export const JourneyApi = {
  get: () => api<Journey>('/api/journey'),
}

export const DatesApi = {
  list: () => api<ImportantDate[]>('/api/important-dates'),
  create: (title: string, date: string, description: string, reminder_enabled: boolean) =>
    api<ImportantDate>('/api/important-dates', { method: 'POST', body: { title, date, description, reminder_enabled } }),
  toggleReminder: (id: string) =>
    api<ImportantDate>(`/api/important-dates/${id}/toggle-reminder`, { method: 'POST' }),
}

export const ShareApi = {
  generate: () => api<ShareCard>('/api/share-card', { method: 'POST' }),
  latest: () => api<ShareCard>('/api/share-card/latest'),
}

export const NotificationApi = {
  list: () => api<Notification[]>('/api/notifications'),
  markRead: (id: string) => api<Notification>(`/api/notifications/${id}/read`, { method: 'POST' }),
}

export const AnalyticsApi = {
  get: () => api<Analytics>('/api/analytics'),
}
