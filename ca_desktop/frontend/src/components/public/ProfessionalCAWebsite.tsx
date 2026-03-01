import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Building2, Mail, Phone, MapPin, Globe, ChevronRight,
  CheckCircle, Users, TrendingUp, FileText, Calculator,
  Factory, ShoppingBag, Home as HomeIcon, Briefcase, Star
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8443/api/v1';

interface CAWebsiteData {
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
    media_items?: { file_path?: string; url?: string; title?: string }[];
  } | null;
  services: Array<{
    id: number;
    title: string;
    description: string;
  }>;
  testimonials: Array<{
    id: number;
    client_name: string;
    text: string;
    rating: number;
  }>;
}

export const ProfessionalCAWebsite: React.FC = () => {
  const { caSlug: rawSlug } = useParams<{ caSlug: string }>();
  const caSlug = rawSlug?.startsWith('ca-') ? rawSlug.substring(3) : rawSlug;
  const navigate = useNavigate();
  const [data, setData] = useState<CAWebsiteData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/public/ca-slug/${caSlug}`);
        setData(response.data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'CA not found');
      } finally {
        setLoading(false);
      }
    };

    if (caSlug) {
      fetchData();
    }
  }, [caSlug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="text-center max-w-md mx-4">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">CA Not Found</h1>
          <p className="text-gray-600 mb-8">{error || 'The CA profile you are looking for does not exist.'}</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  const firmName = data.profile?.firm_name || data.display_name || data.username;
  const caName = data.display_name || data.username;

  // Default services if none configured
  const services = data.services?.length > 0 ? data.services : [
    {
      id: 1,
      title: "Tax Planning & Compliance",
      description: "Expert guidance on income tax, GST, and regulatory compliance to optimize your tax liability."
    },
    {
      id: 2,
      title: "Audit & Assurance",
      description: "Comprehensive audit services ensuring accuracy, compliance, and financial transparency."
    },
    {
      id: 3,
      title: "Business Advisory",
      description: "Strategic financial advice to help your business grow and achieve its goals."
    },
    {
      id: 4,
      title: "Accounting Services",
      description: "Complete bookkeeping, financial reporting, and accounting solutions for your business."
    },
  ];

  // Default industries
  const industries = [
    { icon: Factory, name: "Manufacturing", color: "bg-blue-100 text-blue-600" },
    { icon: ShoppingBag, name: "Retail & E-commerce", color: "bg-purple-100 text-purple-600" },
    { icon: HomeIcon, name: "Real Estate", color: "bg-green-100 text-green-600" },
    { icon: Briefcase, name: "Professional Services", color: "bg-orange-100 text-orange-600" },
    { icon: TrendingUp, name: "Startups & SMEs", color: "bg-red-100 text-red-600" },
    { icon: Building2, name: "Construction", color: "bg-indigo-100 text-indigo-600" },
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              {data.profile?.logo_path ? (
                <img
                  src={data.profile.logo_path}
                  alt={firmName}
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold">
                  {firmName.charAt(0).toUpperCase()}
                </div>
              )}
              <span className="text-xl font-bold text-gray-900">{firmName}</span>
            </div>
            <button
              onClick={() => navigate(`/ca-${caSlug}/login`)}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold text-sm"
            >
              Client Login
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section with Moving Banner Images */}
      <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white py-24 overflow-hidden">
        {/* Animated Background Carousel */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-r from-blue-900/95 via-blue-800/90 to-indigo-900/95 z-10"></div>
          <div className="animate-slide-slow absolute inset-0 flex">
            <img
              src="https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=1920&h=1080&fit=crop&q=80"
              alt="Professional Accounting"
              className="w-full h-full object-cover flex-shrink-0"
            />
            <img
              src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&h=1080&fit=crop&q=80"
              alt="Financial Analysis"
              className="w-full h-full object-cover flex-shrink-0"
            />
            <img
              src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1920&h=1080&fit=crop&q=80"
              alt="Business Consulting"
              className="w-full h-full object-cover flex-shrink-0"
            />
          </div>
        </div>

        <div className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-4xl mx-auto">
            <div className="mb-6">
              <h1 className="text-6xl md:text-7xl font-bold mb-2 tracking-tight text-white drop-shadow-lg">
                DAGDIYA ASSOCIATES
              </h1>
              <p className="text-2xl md:text-3xl font-light text-blue-100 tracking-wide">
                Your Partner in Financial Excellence
              </p>
            </div>
            <p className="text-lg md:text-xl text-blue-50 mb-8 leading-relaxed max-w-3xl mx-auto">
              Serving businesses with integrity and expertise for over 47 years. Your trusted advisors for comprehensive financial solutions.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate(`/ca-${caSlug}/login`)}
                className="px-8 py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition font-bold text-lg shadow-xl flex items-center justify-center gap-2"
              >
                Access Client Portal
                <ChevronRight size={20} />
              </button>
              <a
                href="#contact"
                className="px-8 py-4 bg-transparent border-2 border-white text-white rounded-lg hover:bg-white hover:text-blue-600 transition font-bold text-lg"
              >
                Get in Touch
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
              <div className="inline-block px-4 py-2 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold mb-4">
                About Us
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight">
                Excellence Built on 47 Years of Trust
              </h2>
              <p className="text-lg text-gray-700 leading-relaxed mb-6">
                Since 1979, we have been the cornerstone of financial excellence for businesses across Maharashtra. Our legacy spans nearly five decades of unwavering commitment to accuracy, compliance, and client success. What started as a vision to provide ethical and professional accounting services has grown into a trusted partnership with hundreds of businesses.
              </p>
              <p className="text-lg text-gray-700 leading-relaxed mb-6">
                We don't just manage numbers—we build lasting relationships. Our deep understanding of evolving tax regulations, combined with personalized attention to each client's unique needs, ensures your business stays compliant, competitive, and financially sound. From startups to established enterprises, we've been there through every milestone.
              </p>
              <div className="space-y-4">
                <div className="flex items-start gap-3 group">
                  <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <CheckCircle className="text-green-600" size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Expert Guidance</h3>
                    <p className="text-gray-600">Professional advice backed by years of experience and certifications</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 group">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <Users className="text-blue-600" size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Personalized Service</h3>
                    <p className="text-gray-600">Tailored solutions for your specific business requirements</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 group">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                    <TrendingUp className="text-purple-600" size={20} />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">Timely Compliance</h3>
                    <p className="text-gray-600">Never miss a deadline with our proactive approach</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2 relative">
              {/* Use Lokesh's photo for lokesh-dagdiya, otherwise professional CA image */}
              {caSlug === 'lokesh-dagdiya' ? (
                <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                  <img
                    src="https://www.spmlindia.com/resource/Image/Lokesh.jpg"
                    alt="CA Lokesh Dagdiya"
                    className="w-full h-auto object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                </div>
              ) : data.profile?.logo_path ? (
                <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                  <img
                    src={data.profile.logo_path}
                    alt={firmName}
                    className="w-full h-auto object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
                </div>
              ) : (
                <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                  <img
                    src="https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=800&h=600&fit=crop&q=80"
                    alt="Professional Chartered Accountant"
                    className="w-full h-auto object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent"></div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Photo Gallery Section - if media items exist */}
      {data.profile?.media_items && data.profile.media_items.length > 0 && (
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <div className="inline-block px-4 py-2 bg-indigo-100 text-indigo-600 rounded-full text-sm font-semibold mb-4">
                Our Office
              </div>
              <h2 className="text-4xl font-bold text-gray-900 mb-4">Gallery</h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                A glimpse into our professional workspace
              </p>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {data.profile.media_items.slice(0, 10).map((item: any, idx: number) => (
                <div
                  key={idx}
                  className="group relative aspect-square rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2"
                >
                  <img
                    src={item.file_path || item.url}
                    alt={item.title || `Gallery ${idx + 1}`}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/0 to-black/0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    {item.title && (
                      <div className="absolute bottom-0 left-0 right-0 p-4">
                        <p className="text-white font-semibold">{item.title}</p>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Services Section with Background */}
      <section className="py-20 bg-gradient-to-b from-white to-gray-50 relative overflow-hidden">
        <div className="absolute inset-0 opacity-5">
          <img
            src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&h=1080&fit=crop&q=80"
            alt="Financial Background"
            className="w-full h-full object-cover"
          />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-2 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold mb-4">
              What We Do
            </div>
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Our Services</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Comprehensive financial solutions designed to meet all your business needs
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {services.map((service, idx) => (
              <div
                key={service.id || idx}
                className="bg-white border-2 border-gray-200 rounded-2xl p-6 hover:border-blue-600 hover:shadow-2xl transition-all duration-300 group transform hover:-translate-y-2 cursor-pointer"
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center mb-4 group-hover:from-blue-600 group-hover:to-indigo-600 transition-all duration-300 group-hover:scale-110">
                  <FileText className="text-blue-600 group-hover:text-white transition-colors duration-300" size={28} />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
                  {service.title}
                </h3>
                <p className="text-gray-600 leading-relaxed text-sm">{service.description}</p>
                <div className="mt-4 flex items-center text-blue-600 font-semibold text-sm opacity-0 group-hover:opacity-100 transition-opacity">
                  Learn More <ChevronRight size={16} className="ml-1" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Industries We Serve with Background Images */}
      <section className="py-20 bg-gray-900 relative overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1920&h=1080&fit=crop&q=80"
            alt="Business Background"
            className="w-full h-full object-cover opacity-30 blur-sm"
          />
        </div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Industries We Serve</h2>
            <p className="text-xl text-blue-100 max-w-2xl mx-auto">
              Specialized expertise across diverse sectors
            </p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
            {industries.map((industry, idx) => {
              const Icon = industry.icon;
              return (
                <div
                  key={idx}
                  className="bg-white/95 backdrop-blur-sm rounded-2xl p-6 text-center hover:shadow-2xl transition-all duration-300 border-2 border-white/20 hover:border-blue-400 group transform hover:-translate-y-2 cursor-pointer"
                  style={{ animationDelay: `${idx * 50}ms` }}
                >
                  <div className={`w-16 h-16 ${industry.color} rounded-full flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300`}>
                    <Icon size={32} className="group-hover:scale-110 transition-transform" />
                  </div>
                  <h3 className="font-semibold text-gray-900 text-sm group-hover:text-blue-600 transition-colors">
                    {industry.name}
                  </h3>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      {data.testimonials && data.testimonials.length > 0 && (
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">Client Testimonials</h2>
              <p className="text-xl text-gray-600">What our clients say about us</p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              {data.testimonials.slice(0, 3).map((testimonial, idx) => (
                <div
                  key={testimonial.id}
                  className="bg-white rounded-2xl p-8 border-2 border-gray-200 hover:border-blue-600 hover:shadow-2xl transition-all duration-300 group transform hover:-translate-y-2"
                  style={{ animationDelay: `${idx * 100}ms` }}
                >
                  <div className="flex gap-1 mb-4">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        size={20}
                        className={`transition-all duration-300 ${i < testimonial.rating
                          ? 'text-yellow-400 fill-yellow-400 group-hover:scale-110'
                          : 'text-gray-300'
                          }`}
                      />
                    ))}
                  </div>
                  <p className="text-gray-700 italic mb-6 leading-relaxed text-lg">
                    "{testimonial.text}"
                  </p>
                  <div className="flex items-center gap-3 pt-4 border-t border-gray-200">
                    <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold">
                      {testimonial.client_name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-bold text-gray-900">{testimonial.client_name}</p>
                      <p className="text-sm text-gray-500">Valued Client</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Contact Section */}
      <section id="contact" className="py-20 bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h2 className="text-4xl font-bold mb-6">Get in Touch</h2>
              <p className="text-gray-300 text-lg mb-8">
                Ready to take control of your finances? Contact us today for a consultation.
              </p>
              <div className="space-y-4">
                {data.profile?.address && (
                  <div className="flex items-start gap-4">
                    <MapPin className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                    <div>
                      <p className="font-semibold">Address</p>
                      <p className="text-gray-300">{data.profile.address}</p>
                    </div>
                  </div>
                )}
                {data.profile?.phone_number && (
                  <div className="flex items-start gap-4">
                    <Phone className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                    <div>
                      <p className="font-semibold">Phone</p>
                      <a href={`tel:${data.profile.phone_number}`} className="text-gray-300 hover:text-blue-400 transition">
                        {data.profile.phone_number}
                      </a>
                    </div>
                  </div>
                )}
                {data.profile?.email && (
                  <div className="flex items-start gap-4">
                    <Mail className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                    <div>
                      <p className="font-semibold">Email</p>
                      <a href={`mailto:${data.profile.email}`} className="text-gray-300 hover:text-blue-400 transition">
                        {data.profile.email}
                      </a>
                    </div>
                  </div>
                )}
                {data.profile?.website_url && (
                  <div className="flex items-start gap-4">
                    <Globe className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                    <div>
                      <p className="font-semibold">Website</p>
                      <a
                        href={data.profile.website_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-gray-300 hover:text-blue-400 transition"
                      >
                        {data.profile.website_url}
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="bg-white text-gray-900 rounded-xl p-8">
              <h3 className="text-2xl font-bold mb-6">Quick Inquiry</h3>
              <form className="space-y-4">
                <input
                  type="text"
                  placeholder="Your Name"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
                <input
                  type="email"
                  placeholder="Your Email"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
                <input
                  type="tel"
                  placeholder="Your Phone"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                />
                <textarea
                  placeholder="Your Message"
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600"
                ></textarea>
                <button
                  type="submit"
                  className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold"
                >
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-gray-400 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p>© {new Date().getFullYear()} {firmName}. All rights reserved.</p>
          <p className="mt-2 text-sm">Powered by DocManager</p>
        </div>
      </footer>

      <style>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        @keyframes slide-slow {
          0% { transform: translateX(0); }
          100% { transform: translateX(-66.666%); }
        }
        .animate-slide-slow {
          animation: slide-slow 20s linear infinite;
        }
        .animate-slide-slow:hover {
          animation-play-state: paused;
        }
      `}</style>
    </div>
  );
};
