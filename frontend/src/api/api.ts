import axios, { AxiosResponse } from 'axios'

// создаём экземпляр axios с базовым URL из .env
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 8000, // 8 секунд таймаут - должно быть достаточно
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor для обработки ошибок и retry
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Retry для network errors или 5xx ошибок
    if (
      (error.code === 'ECONNABORTED' || 
       error.code === 'NETWORK_ERROR' || 
       (error.response && error.response.status >= 500)) &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      console.log('Retrying failed request...', error.config.url);
      
      // Убираем задержку для более быстрого retry
      return api(originalRequest);
    }

    console.error('API Error:', error.config?.url, error.message);
    return Promise.reject(error);
  }
)

// -------------------------
// Типы для работы с пользователем
// -------------------------

/** Входная схема для создания/обновления пользователя */
export interface UserCreate {
  telegram_id: number
  username?: string
  first_name?: string
  last_name?: string
  exam_country: string
  exam_language: string
  ui_language: string  // FIXED: removed typo from ui_langugage
  exam_date?: string    // OPTIONAL: ISO date string
  daily_goal?: number   // OPTIONAL: daily goal
}

export interface UserSettingsUpdate {
  exam_country?: string   // Made optional
  exam_language?: string  // Made optional
  ui_language?: string    // Made optional
  exam_date?: string      // ISO-строка, optional
  daily_goal?: number     // optional
}

export const createUser = (payload: UserCreate) => {
  return api.post<UserOut>('/users/', payload)
}

export const updateUser = (userId: string, payload: UserSettingsUpdate) => {
  return api.patch<UserOut>(`/users/${userId}`, payload)
}

/** Ответ от сервера при создании/получении пользователя */
export interface UserOut {
  id: string
  created_at: string
  username?: string
  first_name?: string
  last_name?: string
  exam_country?: string
  exam_language?: string
  ui_language?: string
  exam_date?: string     // ISO date string
  daily_goal?: number
}

// -------------------------
// NEW: Exam Settings Types
// -------------------------

export interface ExamSettingsUpdate {
  exam_date?: string  // ISO date string (YYYY-MM-DD)
  daily_goal?: number // 1-100
}

export interface ExamSettingsResponse {
  exam_date?: string
  daily_goal?: number
  days_until_exam?: number
  recommended_daily_goal?: number
}

export const setExamSettings = (userId: string, settings: ExamSettingsUpdate) => {
  return api.post<ExamSettingsResponse>(`/users/${userId}/exam-settings`, settings)
}

export const getExamSettings = (userId: string) => {
  return api.get<ExamSettingsResponse>(`/users/${userId}/exam-settings`)
}

// Получить количество нерешенных вопросов для пользователя
export const getRemainingQuestionsCount = (userId: string, country: string, language: string) => {
  return api.get<{ remaining_count: number }>(`/questions/remaining-count`, {
    params: {
      user_id: userId,
      country,
      language
    }
  })
}

// -------------------------
// Типы и функции для работы с вопросами
// -------------------------

/** Структура одного вопроса из ответа сервера */
export interface QuestionOut {
  id: string
  data: {
    question: string
    question_image: string | null
    options: string[]
    correct_index: number
  }
  country: string
  language: string
  topic: string
}

/** Параметры фильтра для запроса вопросов */
export interface GetQuestionsParams {
  user_id: string
  country?: string
  language?: string
  mode?: string
  batch_size?: number
  topic?: string | string[]
}

/**
 * Получить вопросы с сервера
 */
export const getQuestions = (params: GetQuestionsParams) => {
  return api.get<QuestionOut[]>('/questions/', { params })
}

// -------------------------
// Типы и функции для статистики и ответов
// -------------------------

/** Статистика пользователя */
export interface UserStats {
  answered: number
  correct: number
  total_questions: number
}

/** Получить статистику пользователя по его ID */
export const getUserStats = (userId: string) => {
  return api.get<UserStats>(`/users/${userId}/stats`)
}

/** Параметры для отправки одного ответа */
export interface AnswerSubmit {
  user_id: string
  question_id: number
  is_correct: boolean
}

/** Отправить ответ пользователя */
export const submitAnswer = (payload: AnswerSubmit) => {
  return api.post('/user_progress/submit_answer', payload)
}

/**Получить юзера по Telegram ID */
/**
 * Возвращает объект пользователя по его telegram_id
 */
export const getUserByTelegramId = async (
  telegramId: number
): Promise<AxiosResponse<UserOut>> => {
  return api.get<UserOut>(`/users/by-telegram-id/${telegramId}`)
}

/** Получить список тем для юзера */
export const getTopics = (country: string, language: string) =>
  api.get<{ topics: string[] }>(
    `/topics?country=${country}&language=${language}`,
  )

/**Дневной прогресс */
export interface DailyProgress {
  questions_mastered_today: number
  date: string
}

export const getDailyProgress = (userId: string, targetDate?: string) => {
  // Если targetDate не передан, используем сегодняшнюю дату в формате YYYY-MM-DD
  const dateToUse = targetDate || new Date().toISOString().split('T')[0]
  const params = `?target_date=${dateToUse}`
  return api.get<DailyProgress>(`/users/${userId}/daily-progress${params}`)
}

// -------------------------
// NEW: Answers by Day
// -------------------------

export interface AnswersByDay {
  date: string;
  total_answers: number;
  correct_answers: number;
  incorrect_answers: number;
}

export const getAnswersByDay = (userId: string, days: number = 7) => {
  return api.get<AnswersByDay[]>(`/users/${userId}/answers-by-day`, {
    params: { days }
  })
}


export default api