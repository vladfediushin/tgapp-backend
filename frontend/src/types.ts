// === Telegram SDK Types ===

export interface TelegramUser {
    id: number
    is_bot: boolean
    first_name: string
    last_name?: string
    username?: string
    language_code?: string
  }
  
  export interface TelegramWebApp {
    initData: string
    initDataUnsafe: {
      user?: TelegramUser
      auth_date?: number
      hash?: string
    }
    ready(): void
    expand(): void
  }
  
  declare global {
    interface Window {
      Telegram?: {
        WebApp: TelegramWebApp
      }
    }
  }
  
  // === Other ===

  import { AxiosResponse } from 'axios'

  export interface UserOut {
  id: string
  telegram_id: number
  username?: string
  first_name?: string
  last_name?: string
  created_at: string
  exam_country: string
  exam_language: string
  ui_language: string
  exam_date?: string     // ISO date string
  daily_goal?: number
}

export type ApiResponse<T> = AxiosResponse<T>