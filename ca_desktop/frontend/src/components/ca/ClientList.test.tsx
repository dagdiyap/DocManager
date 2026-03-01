
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import ClientList from './ClientList'
import { AuthProvider } from '../../contexts/AuthContext'
import { MemoryRouter } from 'react-router-dom'
import { authApi } from '../../api'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

// Mock API
vi.mock('../../api', () => ({
    authApi: {
        listClients: vi.fn(),
        createClient: vi.fn(),
        deleteClient: vi.fn(),
    }
}))

vi.mock('react-hot-toast', () => ({
    default: {
        success: vi.fn(),
        error: vi.fn(),
    }
}))

const mockClients = [
    { id: 1, name: 'John Doe', phone_number: '9876543210', email: 'john@example.com', is_active: true },
    { id: 2, name: 'Jane Smith', phone_number: '1234567890', email: 'jane@example.com', is_active: true },
]

const createTestQueryClient = () => new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
        },
    },
})

describe('ClientList Component', () => {
    beforeEach(() => {
        vi.clearAllMocks()
        vi.mocked(authApi.listClients).mockResolvedValue({
            data: mockClients,
            status: 200,
            statusText: 'OK',
            headers: {},
            config: {} as any
        })
    })

    it('renders client list', async () => {
        render(
            <QueryClientProvider client={createTestQueryClient()}>
                <MemoryRouter>
                    <AuthProvider>
                        <ClientList />
                    </AuthProvider>
                </MemoryRouter>
            </QueryClientProvider>
        )

        expect(screen.getByText('Client Management')).toBeInTheDocument()

        await waitFor(() => {
            expect(screen.getByText('John Doe')).toBeInTheDocument()
            expect(screen.getByText('Jane Smith')).toBeInTheDocument()
        })
    })

    it('opens add client modal', async () => {
        render(
            <QueryClientProvider client={createTestQueryClient()}>
                <MemoryRouter>
                    <AuthProvider>
                        <ClientList />
                    </AuthProvider>
                </MemoryRouter>
            </QueryClientProvider>
        )

        const addBtn = screen.getByText('Add New Client')
        fireEvent.click(addBtn)

        expect(screen.getByText('Add New Client', { selector: 'h3' })).toBeInTheDocument()
        expect(screen.getByPlaceholderText('Amit Sharma')).toBeInTheDocument()
    })

    it('submits new client', async () => {
        vi.mocked(authApi.createClient).mockResolvedValue({
            data: { ...mockClients[0], id: 3, name: 'New User' },
            status: 200,
            statusText: 'OK',
            headers: {},
            config: {} as any
        })

        render(
            <QueryClientProvider client={createTestQueryClient()}>
                <MemoryRouter>
                    <AuthProvider>
                        <ClientList />
                    </AuthProvider>
                </MemoryRouter>
            </QueryClientProvider>
        )

        fireEvent.click(screen.getByText('Add New Client'))

        fireEvent.change(screen.getByPlaceholderText('Amit Sharma'), { target: { value: 'New User' } })
        fireEvent.change(screen.getByPlaceholderText('9876543210'), { target: { value: '5555555555' } })
        fireEvent.change(screen.getByPlaceholderText('client@example.com'), { target: { value: 'new@example.com' } })


        const submitBtn = screen.getByText('Create Client')
        fireEvent.click(submitBtn)

        await waitFor(() => {
            expect(authApi.createClient).toHaveBeenCalledWith(expect.objectContaining({
                name: 'New User',
                phone_number: '5555555555'
            }))
        })
    })
})
