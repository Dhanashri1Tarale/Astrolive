export interface User {
  id: string
  email: string
  name: string
  is_demo: boolean
  zodiac_sign?: string | null
}

export interface Astrologer {
  id: string
  name: string
  specialty: string
  bio: string
  experience_years: number
  rating: number
  reviews_count: number
  price_per_session: number
  avatar_emoji: string
  languages: string[]
}

export interface Insight {
  id: string
  summary: string
  key_points: string[]
  category: string
  saved_to_memory: boolean
}

export interface Consultation {
  id: string
  topic: string
  transcript: string
  status: string
  created_at: string
  astrologer: Astrologer
  insight?: Insight | null
}

export interface ActionItem {
  id: string
  title: string
  description: string
  is_completed: boolean
  order: number
}

export interface Goal {
  id: string
  title: string
  category: string
  description: string
  progress: number
  status: string
  actions: ActionItem[]
}

export interface ImportantDate {
  id: string
  title: string
  date: string
  description: string
  reminder_enabled: boolean
}

export interface JourneyEvent {
  id: string
  type: string
  title: string
  description: string
  created_at: string
}

export interface Milestone {
  key: string
  label: string
  done: boolean
}

export interface Journey {
  goal: Goal | null
  progress_percent: number
  milestones: Milestone[]
  today_insight: string
  today_action: ActionItem | null
  events: JourneyEvent[]
}

export interface ShareCard {
  id: string
  headline: string
  stats: {
    zodiac_sign: string
    goal_title: string
    progress_percent: number
    actions_completed: number
    actions_total: number
  }
  created_at: string
}

export interface Notification {
  id: string
  message: string
  type: string
  is_read: boolean
  created_at: string
}

export interface Analytics {
  total_consultations: number
  total_goals: number
  active_goals: number
  completed_actions: number
  total_actions: number
  current_streak_days: number
  journey_progress: number
  category_breakdown: Record<string, number>
}
