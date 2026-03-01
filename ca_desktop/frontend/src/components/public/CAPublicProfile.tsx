import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Building2, Mail, Phone, Globe, MapPin } from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8443/api/v1';

interface CAProfile {
  slug: string;
  display_name: string;
  username: string;
  profile: {
    firm_name: string | null;
    logo_path: string | null;
    professional_bio: string | null;
    address: string | null;
    phone_number: string | null;
    email: string | null;
    website_url: string | null;
  } | null;
}

export const CAPublicProfile: React.FC = () => {
  const { caSlug } = useParams<{ caSlug: string }>();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<CAProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/public/ca-slug/${caSlug}`);
        setProfile(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'CA not found');
      } finally {
        setLoading(false);
      }
    };

    if (caSlug) {
      fetchProfile();
    }
  }, [caSlug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading profile...</p>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-purple-50">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">CA Not Found</h1>
          <p className="text-gray-600 mb-8">{error || 'The CA profile you are looking for does not exist.'}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  const firmName = profile.profile?.firm_name || profile.display_name || profile.username;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              {profile.profile?.logo_path ? (
                <img
                  src={profile.profile.logo_path}
                  alt={firmName}
                  className="w-16 h-16 rounded-full object-cover border-2 border-indigo-200"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                  {firmName.charAt(0).toUpperCase()}
                </div>
              )}
              <div>
                <h1 className="text-2xl font-bold text-gray-900">{firmName}</h1>
                <p className="text-sm text-gray-600">Chartered Accountant</p>
              </div>
            </div>
            <button
              onClick={() => navigate(`/ca-${caSlug}/login`)}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition font-semibold"
            >
              Client Portal Login
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Professional Bio */}
        {profile.profile?.professional_bio && (
          <section className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">About</h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">
              {profile.profile.professional_bio}
            </p>
          </section>
        )}

        {/* Contact Information */}
        <section className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Contact Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {profile.profile?.address && (
              <div className="flex items-start gap-3">
                <MapPin className="text-indigo-600 mt-1" size={20} />
                <div>
                  <p className="font-semibold text-gray-900">Address</p>
                  <p className="text-gray-600">{profile.profile.address}</p>
                </div>
              </div>
            )}
            {profile.profile?.phone_number && (
              <div className="flex items-start gap-3">
                <Phone className="text-indigo-600 mt-1" size={20} />
                <div>
                  <p className="font-semibold text-gray-900">Phone</p>
                  <a
                    href={`tel:${profile.profile.phone_number}`}
                    className="text-indigo-600 hover:underline"
                  >
                    {profile.profile.phone_number}
                  </a>
                </div>
              </div>
            )}
            {profile.profile?.email && (
              <div className="flex items-start gap-3">
                <Mail className="text-indigo-600 mt-1" size={20} />
                <div>
                  <p className="font-semibold text-gray-900">Email</p>
                  <a
                    href={`mailto:${profile.profile.email}`}
                    className="text-indigo-600 hover:underline"
                  >
                    {profile.profile.email}
                  </a>
                </div>
              </div>
            )}
            {profile.profile?.website_url && (
              <div className="flex items-start gap-3">
                <Globe className="text-indigo-600 mt-1" size={20} />
                <div>
                  <p className="font-semibold text-gray-900">Website</p>
                  <a
                    href={profile.profile.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-indigo-600 hover:underline"
                  >
                    {profile.profile.website_url}
                  </a>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Client Portal CTA */}
        <section className="mt-8 bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl shadow-lg p-8 text-white text-center">
          <Building2 size={48} className="mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">Access Your Client Portal</h2>
          <p className="text-indigo-100 mb-6 max-w-2xl mx-auto">
            View your documents, messages, and compliance status through our secure client portal.
          </p>
          <button
            onClick={() => navigate(`/ca-${caSlug}/login`)}
            className="px-8 py-4 bg-white text-indigo-600 rounded-lg hover:bg-indigo-50 transition font-bold text-lg"
          >
            Login to Portal
          </button>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 text-center text-gray-600 text-sm">
          <p>© {new Date().getFullYear()} {firmName}. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};
