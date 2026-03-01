import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Phone, Lock, LogIn } from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8443/api/v1';

interface PortalMetadata {
  slug: string;
  display_name: string;
  firm_name: string | null;
  logo_path: string | null;
  portal_url: string;
}

export const CAClientLogin: React.FC = () => {
  const { caSlug: rawSlug } = useParams<{ caSlug: string }>();
  const caSlug = rawSlug?.startsWith('ca-') ? rawSlug.substring(3) : rawSlug;
  const navigate = useNavigate();
  const [portalData, setPortalData] = useState<PortalMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchPortalMetadata = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/public/ca-slug/${caSlug}/portal`);
        setPortalData(response.data);
      } catch (err: any) {
        toast.error('CA portal not found');
        navigate('/');
      } finally {
        setLoading(false);
      }
    };

    if (caSlug) {
      fetchPortalMetadata();
    }
  }, [caSlug, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/auth/login`,
        new URLSearchParams({
          username: formData.username,
          password: formData.password,
          grant_type: 'password',
        }),
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      const { access_token } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('userType', 'client');

      toast.success('Login successful!');
      navigate(`/ca-${caSlug}/home`);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading portal...</p>
        </div>
      </div>
    );
  }

  const firmName = portalData?.firm_name || portalData?.display_name || 'CA Portal';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50 px-4">
      <div className="w-full max-w-md">
        {/* Logo/Header */}
        <div className="text-center mb-8">
          {portalData?.logo_path ? (
            <img
              src={portalData.logo_path}
              alt={firmName}
              className="w-24 h-24 mx-auto rounded-full object-cover border-4 border-white shadow-lg mb-4"
            />
          ) : (
            <div className="w-24 h-24 mx-auto rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white text-4xl font-bold shadow-lg mb-4">
              {firmName.charAt(0).toUpperCase()}
            </div>
          )}
          <h1 className="text-3xl font-bold text-gray-900">{firmName}</h1>
          <p className="text-gray-600 mt-2">Client Portal Login</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Phone Number
              </label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="tel"
                  required
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="9876543210"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="password"
                  required
                  className="w-full pl-11 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Logging in...
                </>
              ) : (
                <>
                  <LogIn size={20} />
                  Login
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center space-y-3">
            <button
              onClick={() => navigate(`/ca-${caSlug}/reset-password`)}
              className="text-sm text-indigo-600 hover:underline block w-full"
            >
              Forgot Password?
            </button>
            <button
              onClick={() => navigate(`/ca-${caSlug}`)}
              className="text-sm text-gray-600 hover:underline"
            >
              ← Back to CA Profile
            </button>
          </div>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-600 mt-8">
          Secure client portal powered by DocManager
        </p>
      </div>
    </div>
  );
};
