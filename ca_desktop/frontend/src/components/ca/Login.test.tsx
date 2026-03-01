
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import CALogin from './Login'
import { AuthProvider } from '../../contexts/AuthContext'
import { MemoryRouter } from 'react-router-dom'
import { authApi } from '../../api'

// Mock API
vi.mock('../../api', () => ({
    authApi: {
        login: vi.fn(),
        register: vi.fn(),
    }
}))

// Mock Layout and other components if needed, but Login is standalone page
// We need to mock toast
vi.mock('react-hot-toast', () => ({
    default: {
        success: vi.fn(),
        error: vi.fn(),
    }
}))

describe('CALogin Component', () => {
    it('renders login form by default', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <CALogin />
                </AuthProvider>
            </MemoryRouter>
        )
        expect(screen.getByText('Welcome Back! 👋')).toBeInTheDocument()
        expect(screen.getByPlaceholderText('admin')).toBeInTheDocument()
        expect(screen.getByText('Sign In')).toBeInTheDocument()
    })

    it('toggles to registration form', () => {
        render(
            <MemoryRouter>
                <AuthProvider>
                    <CALogin />
                </AuthProvider>
            </MemoryRouter>
        )
        const toggleButton = screen.getByText(/Create Account/i)
        fireEvent.click(toggleButton)
        expect(screen.getByText('Setup Admin Account')).toBeInTheDocument()
        expect(screen.getByPlaceholderText('ca@firm.com')).toBeInTheDocument()
    })

    it('calls login api on submit', async () => {
        const mockLogin = vi.fn().mockResolvedValue({
            data: { access_token: 'fake-token', user_type: 'ca' }
        })
        vi.mocked(authApi.login).mockImplementation(mockLogin)

        render(
            <MemoryRouter>
                <AuthProvider>
                    <CALogin />
                </AuthProvider>
            </MemoryRouter>
        )

        fireEvent.change(screen.getByPlaceholderText('admin'), { target: { value: 'testuser' } })
        fireEvent.change(screen.getByPlaceholderText('••••••••'), { target: { value: 'password' } })

        const submitBtn = screen.getByText('Sign In')
        fireEvent.click(submitBtn)

        await waitFor(() => {
            expect(mockLogin).toHaveBeenCalled()
        })
    })
})
