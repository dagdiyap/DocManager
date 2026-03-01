import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// CA Management
export const getCAs = () => apiClient.get('/ca/list')
export const registerCA = (data: any) => apiClient.post('/ca/register', data)
export const updateCA = (caId: string, data: any) => apiClient.patch(`/ca/${caId}`, data)

// Licensing
export const issueLicense = (data: any) => apiClient.post('/license/issue', data)
export const revokeLicense = (licenseId: number, reason: string) =>
    apiClient.post(`/license/revoke/${licenseId}`, { reason })

// Support
export const getSupportSessions = () => apiClient.get('/support/sessions')
export const sendRemoteCommand = (caId: string, action: string, payload?: any) =>
    apiClient.post('/support/execute_command', { ca_id: caId, action, payload })

export default apiClient
