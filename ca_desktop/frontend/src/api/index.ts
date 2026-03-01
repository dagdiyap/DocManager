import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8443/api/v1'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Add a request interceptor to include the JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

// Add a response interceptor to handle token expiration
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.clear()
            window.location.href = '/portal/login'
        }
        return Promise.reject(error)
    }
)

export default api

// API Modules
export const authApi = {
    login: (credentials: any) => api.post('/auth/login', credentials, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
    register: (userData: any) => api.post('/auth/register', userData),
    logout: () => api.post('/auth/logout'),
    listClients: () => api.get('/clients/'),
    createClient: (clientData: any) => api.post('/clients/', clientData),
    updateClient: (phone: string, clientData: any) => api.patch(`/clients/${phone}`, clientData),
    deleteClient: (phone: string) => api.delete(`/clients/${phone}`),
}

export const documentApi = {
    list: () => api.get('/documents/'),
    upload: (formData: FormData) => api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    getDownloadToken: (docId: number) => api.get(`/documents/download-token/${docId}`),
    download: (token: string) => `${API_BASE_URL}/documents/download/${token}`,
}

export const messageApi = {
    list: () => api.get('/messaging/messages'),
    send: (msg: any) => api.post('/messaging/messages', msg),
    listSharedFiles: () => api.get('/messaging/shared-files'),
    getSharedFileDownloadToken: (fileId: number) => api.get(`/messaging/shared-files/download-token/${fileId}`),
    downloadSharedFile: (token: string) => `${API_BASE_URL}/messaging/shared-files/download/${token}`,
}

// Phase 2 APIs
export const complianceApi = {
    listRules: (clientType?: string) => api.get('/compliance/rules', { params: { client_type: clientType } }),
    getClientStatus: (phone: string) => api.get(`/clients/${phone}/compliance`),
}

export const reminderApi = {
    create: (data: any) => api.post('/reminders', null, { params: data }), // Note: backend uses query params for create
    list: (params: any) => api.get('/reminders', { params }),
    update: (id: number, data: any) => api.patch(`/reminders/${id}`, null, { params: data }),
    delete: (id: number) => api.delete(`/reminders/${id}`),
    sendGroup: (data: any) => api.post('/reminders/send-group', null, { params: data }),
}

export const caProfileApi = {
    get: () => api.get('/ca/profile'),
    update: (data: any) => api.patch('/ca/profile', data),
    uploadMedia: (formData: FormData) => api.post('/ca/media', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
    }),
    listMedia: (type?: string) => api.get('/ca/media', { params: { item_type: type } }),
    reorderMedia: (id: number, order: number) => api.put(`/ca/media/${id}/order`, null, { params: { order_index: order } }),
    listServices: () => api.get('/ca/services'),
    createService: (data: any) => api.post('/ca/services', null, { params: data }),
    updateService: (id: number, data: any) => api.patch(`/ca/services/${id}`, null, { params: data }),
    deleteService: (id: number) => api.delete(`/ca/services/${id}`),
    listTestimonials: () => api.get('/ca/testimonials'),
    createTestimonial: (data: any) => api.post('/ca/testimonials', null, { params: data }),
    updateTestimonial: (id: number, data: any) => api.patch(`/ca/testimonials/${id}`, null, { params: data }),
    deleteTestimonial: (id: number) => api.delete(`/ca/testimonials/${id}`), // Note: Added delete as missing in previous step
}

export const publicApi = {
    getProfile: (username: string) => api.get(`/public/ca/${username}/profile`),
    getMedia: (username: string) => api.get(`/public/ca/${username}/media`),
    getServices: (username: string) => api.get(`/public/ca/${username}/services`),
    getTestimonials: (username: string) => api.get(`/public/ca/${username}/testimonials`),
}
