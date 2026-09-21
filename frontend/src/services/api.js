/**
 * services/api.js — Axios instance pre-configured with base URL,
 * auth header injection, and automatic token refresh on 401.
 */
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
})

// ─── Request interceptor — attach access token ────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// ─── Response interceptor — handle 401 by refreshing token ───────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post('/api/auth/refresh', {
            refresh_token: refreshToken,
          })
          localStorage.setItem('access_token',  data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch {
          // Refresh failed — clear tokens and let UI handle redirect
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
        }
      }
    }
    return Promise.reject(error)
  }
)

export default api

// ─── Auth API helpers ─────────────────────────────────────────────────────────
export const authApi = {
  register:       (data) => api.post('/auth/register', data),
  login:          (data) => api.post('/auth/login', data),
  verifyEmail:    (token) => api.get(`/auth/verify?token=${token}`),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword:  (data) => api.post('/auth/reset-password', data),
  refresh:        (refresh_token) => api.post('/auth/refresh', { refresh_token }),
  me:             () => api.get('/auth/me'),
}

// ─── Management API helpers ───────────────────────────────────────────────────
export const managementApi = {
  // Faculty
  getFaculty:       () => api.get('/faculty/'),
  createFaculty:    (data) => api.post('/faculty/', data),
  updateFaculty:    (id, data) => api.put(`/faculty/${id}`, data),
  deleteFaculty:    (id) => api.delete(`/faculty/${id}`),

  // Departments & Courses
  getDepartments:   () => api.get('/departments/'),
  createDepartment: (data) => api.post('/departments/', data),
  updateDepartment: (id, data) => api.put(`/departments/${id}`, data),
  deleteDepartment: (id) => api.delete(`/departments/${id}`),
  createCourse:     (deptId, data) => api.post(`/departments/${deptId}/courses`, data),
  updateCourse:     (id, data) => api.put(`/departments/courses/${id}`, data),
  getCourseSubjects: (courseId) => api.get(`/departments/courses/${courseId}/subjects`),
  addCourseSubject:  (courseId, data) => api.post(`/departments/courses/${courseId}/subjects`, data),
  deleteCourseSubject: (courseId, subjectId) => api.delete(`/departments/courses/${courseId}/subjects/${subjectId}`),
  deleteCourse:     (id) => api.delete(`/departments/courses/${id}`),

  // Fees
  getFees:          () => api.get('/fees/'),
  createFee:        (data) => api.post('/fees/', data),
  updateFee:        (id, data) => api.put(`/fees/${id}`, data),
  deleteFee:        (id) => api.delete(`/fees/${id}`),
  
  // Students (Admissions)
  updateStudent:    (id, data) => api.put(`/admission/${id}`, data),
  deleteStudent:    (id) => api.delete(`/admission/${id}`),

  // Dashboard Stats
  getDashboardStats: () => api.get('/dashboard/stats'),

  // Bot Logs
  getBotLogs:       (params) => api.get('/logs/', { params }),

  // Advanced Allocation Engine
  getStagingRecords: () => api.get('/allocation/staging'),
  clearStaging:      () => api.delete('/allocation/staging'),
  uploadStaging:    (data) => api.post('/allocation/upload-staging', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  runAllocation:    () => api.post('/allocation/run'),
  confirmAllocation: (id) => api.post(`/allocation/${id}/confirm`),
  cancelAllocation: (id) => api.post(`/allocation/${id}/cancel`),
  commitAllocations: () => api.post('/allocation/commit'),
}

// ─── Student Portal API helpers ───────────────────────────────────────────────
export const studentApi = {
  getProfile: () => api.get('/admission/me'),
  getAttendanceSummary: (studentId) => api.get(`/attendance/student/${studentId}/summary`),
  getDailyAttendance: (studentId) => api.get(`/attendance/student/${studentId}`),
  getResults: (studentId, semester) => api.get(`/results/student/${studentId}${semester ? `?semester=${semester}` : ''}`),
  getFees: () => api.get('/fees/my'),
  downloadAdmissionLetterUrl: (studentId) => `/api/admission/${studentId}/letter`,
  downloadMarksheetUrl: (studentId, semester) => `/api/results/${studentId}/semester/${semester}/marksheet`,
}

// ─── Notification API helpers ─────────────────────────────────────────────────
export const notificationApi = {
  getMyNotifications: (unreadOnly = false) => api.get(`/notifications/my${unreadOnly ? '?unread_only=true' : ''}`),
  markAsRead: (id) => api.patch(`/notifications/${id}/read`),
  getAllNotifications: (params) => api.get('/notifications/all', { params }),
}

// ─── Faculty Portal API helpers ───────────────────────────────────────────────
export const facultyApi = {
  getProfile: () => api.get('/faculty/me'),
  getCourseSubjects: (courseId) => api.get(`/departments/courses/${courseId}/subjects`),
  uploadAttendance: (data) => api.post('/attendance/bulk/upload', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  uploadResults: (data) => api.post('/results/bulk', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getStudents: () => api.get('/admission/'),
}
