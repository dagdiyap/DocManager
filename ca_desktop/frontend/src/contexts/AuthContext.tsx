import React, { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

interface AuthContextType {
    user: any | null
    userType: 'ca' | 'client' | null
    isLoading: boolean
    login: (token: string, type: 'ca' | 'client', userData: any) => void
    logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<any | null>(null)
    const [userType, setUserType] = useState<'ca' | 'client' | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const navigate = useNavigate()

    useEffect(() => {
        // Check for existing session
        const token = localStorage.getItem('token')
        const type = localStorage.getItem('userType') as 'ca' | 'client'
        const storedUser = localStorage.getItem('user')

        if (token && type && storedUser) {
            setUser(JSON.parse(storedUser))
            setUserType(type)
        }
        setIsLoading(false)
    }, [])

    const login = (token: string, type: 'ca' | 'client', userData: any) => {
        localStorage.setItem('token', token)
        localStorage.setItem('userType', type)
        localStorage.setItem('user', JSON.stringify(userData))
        setUser(userData)
        setUserType(type)
        if (type === 'ca') {
            navigate('/ca')
        } else {
            navigate('/portal')
        }
    }

    const logout = () => {
        localStorage.clear()
        setUser(null)
        setUserType(null)
        navigate('/')
    }

    return (
        <AuthContext.Provider value={{ user, userType, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider')
    }
    return context
}
