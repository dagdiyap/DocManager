import React from 'react';
import {
  Building2, Mail, Phone, MapPin,
  CheckCircle, Users, TrendingUp, FileText,
  Factory, ShoppingBag, Home as HomeIcon, Briefcase, Star
} from 'lucide-react';

// All data hardcoded — no backend API dependency
const FIRM = {
  name: 'Dagdiya Associates',
  photo: 'https://www.spmlindia.com/resource/Image/Lokesh.jpg',
  address: 'Nanded, Maharashtra, India',
  phone: '+91 98901 54945',
  email: 'lokeshdagdiya@gmail.com',
  website: 'https://ca-lokesh-dagdiya.vercel.app',
};

const SERVICES = [
  {
    id: 1,
    title: 'GST Compliance & Advisory',
    description:
      'End-to-end GST services including registration, return filing, reconciliation, audit support, and advisory for complex GST matters across all business types.',
  },
  {
    id: 2,
    title: 'Income Tax Planning & Filing',
    description:
      'Strategic tax planning for individuals, HUFs, firms, and corporates. Advance tax computation, ITR filing, assessment support, and representation before tax authorities.',
  },
  {
    id: 3,
    title: 'Statutory & Internal Audits',
    description:
      'Comprehensive statutory audits, tax audits, internal audits, and special-purpose audits with detailed reporting and actionable recommendations for business improvement.',
  },
  {
    id: 4,
    title: 'Company Formation & Compliance',
    description:
      'Complete company incorporation, LLP formation, ROC filings, annual compliance, board resolutions, and secretarial services for seamless business operations.',
  },
  {
    id: 5,
    title: 'Accounting & Bookkeeping',
    description:
      'Professional bookkeeping, financial statement preparation, bank reconciliation, payroll processing, and MIS reporting tailored to your business needs.',
  },
  {
    id: 6,
    title: 'Business Advisory & Consulting',
    description:
      'Strategic business consulting including financial planning, project feasibility studies, loan syndication, business valuation, and succession planning.',
  },
];

const TESTIMONIALS = [
  {
    id: 1,
    client_name: 'Rajesh Patil, Manufacturing Unit Owner',
    text: 'We have been associated with Dagdiya Associates for over 15 years. Their expertise in GST compliance during the transition from VAT was invaluable. CA Lokesh personally ensured our manufacturing unit had zero compliance issues. Their proactive approach to tax planning has saved us lakhs every year.',
    rating: 5,
  },
  {
    id: 2,
    client_name: 'Priya Sharma, Real Estate Developer',
    text: 'As a real estate developer, tax complexities are enormous. Dagdiya Associates has been our trusted advisor for 8 years. Their deep knowledge of real estate taxation, RERA compliance, and GST on under-construction properties gives us complete peace of mind. Highly recommended for anyone in the construction industry.',
    rating: 5,
  },
  {
    id: 3,
    client_name: 'Amit Deshmukh, Retail Chain Owner',
    text: 'From a single retail store to a chain of 12 outlets, Dagdiya Associates has been with us every step of the way. Their accounting systems, inventory management advice, and multi-location GST compliance handling is top-notch. CA Lokesh treats our business like his own.',
    rating: 5,
  },
];

const INDUSTRIES = [
  { icon: Factory, name: 'Manufacturing', color: 'bg-blue-100 text-blue-600' },
  { icon: ShoppingBag, name: 'Retail & E-commerce', color: 'bg-purple-100 text-purple-600' },
  { icon: HomeIcon, name: 'Real Estate', color: 'bg-green-100 text-green-600' },
  { icon: Briefcase, name: 'Professional Services', color: 'bg-orange-100 text-orange-600' },
  { icon: TrendingUp, name: 'Startups & SMEs', color: 'bg-red-100 text-red-600' },
  { icon: Building2, name: 'Construction', color: 'bg-indigo-100 text-indigo-600' },
];

export const CAWebsite: React.FC = () => {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold">
                D
              </div>
              <span className="text-xl font-bold text-gray-900">{FIRM.name}</span>
            </div>
            <div className="flex items-center gap-6">
              <a href="#services" className="hidden sm:inline text-gray-700 hover:text-blue-600 transition font-medium">
                Services
              </a>
              <a href="#about" className="hidden sm:inline text-gray-700 hover:text-blue-600 transition font-medium">
                About
              </a>
              <a href="#contact" className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-semibold text-sm">
                Contact Us
              </a>
            </div>
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
            <div className="mb-8">
              <h1 className="text-4xl sm:text-5xl md:text-7xl lg:text-8xl font-extrabold mb-3 md:mb-4 tracking-wide text-white drop-shadow-2xl leading-tight">
                DAGDIYA ASSOCIATES
              </h1>
              <p className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-semibold text-blue-50 tracking-wide drop-shadow-lg">
                Your Partner in Financial Excellence
              </p>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 justify-center">
              <a
                href="#contact"
                className="px-6 py-3 sm:px-8 sm:py-4 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition font-bold text-base sm:text-lg shadow-xl flex items-center justify-center gap-2"
              >
                Get in Touch
              </a>
              <a
                href="#services"
                className="px-6 py-3 sm:px-8 sm:py-4 bg-transparent border-2 border-white text-white rounded-lg hover:bg-white/10 transition font-bold text-base sm:text-lg flex items-center justify-center gap-2"
              >
                Our Services
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* About Section */}
      <section id="about" className="py-16 md:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="order-2 md:order-1">
              <div className="inline-block px-4 py-2 bg-blue-100 text-blue-600 rounded-full text-sm font-semibold mb-4">
                About Us
              </div>
              <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-8 leading-tight">
                Excellence Built on <span className="text-blue-600">47 Years of Trust</span>
              </h2>
              <div className="space-y-6 mb-8">
                <p className="text-lg text-gray-700 leading-relaxed">
                  Since 1979, we have been the cornerstone of financial excellence for businesses across Maharashtra. Our legacy spans nearly five decades of unwavering commitment to accuracy, compliance, and client success.
                </p>
                <p className="text-lg text-gray-700 leading-relaxed">
                  What started as a vision to provide ethical and professional accounting services has grown into a trusted partnership with hundreds of businesses. We don't just manage numbers—we build lasting relationships.
                </p>
                <p className="text-lg text-gray-700 leading-relaxed">
                  Our deep understanding of evolving tax regulations, combined with personalized attention to each client's unique needs, ensures your business stays compliant, competitive, and financially sound. From startups to established enterprises, we've been there through every milestone.
                </p>
              </div>
              {/* Mobile: Horizontal scroll carousel, Desktop: Grid */}
              <div className="overflow-x-auto pb-4 -mx-4 px-4 sm:overflow-visible sm:mx-0 sm:px-0">
                <div className="flex gap-4 sm:grid sm:grid-cols-3 min-w-max sm:min-w-0">
                  <div className="bg-white rounded-xl p-5 shadow-md hover:shadow-xl transition-all duration-300 border-t-4 border-green-500 w-72 sm:w-auto flex-shrink-0 sm:flex-shrink">
                    <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-3">
                      <CheckCircle className="text-green-600" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Expert Guidance</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      Professional advice backed by years of experience
                    </p>
                  </div>
                  <div className="bg-white rounded-xl p-5 shadow-md hover:shadow-xl transition-all duration-300 border-t-4 border-blue-500 w-72 sm:w-auto flex-shrink-0 sm:flex-shrink">
                    <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-3">
                      <Users className="text-blue-600" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Personalized Service</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      Tailored solutions for your business requirements
                    </p>
                  </div>
                  <div className="bg-white rounded-xl p-5 shadow-md hover:shadow-xl transition-all duration-300 border-t-4 border-indigo-500 w-72 sm:w-auto flex-shrink-0 sm:flex-shrink">
                    <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mb-3">
                      <TrendingUp className="text-indigo-600" size={24} />
                    </div>
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Timely Compliance</h3>
                    <p className="text-sm text-gray-600 leading-relaxed">
                      Never miss a deadline with our proactive approach
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div className="order-1 md:order-2 relative">
              <div className="relative rounded-2xl overflow-hidden shadow-2xl">
                <img
                  src={FIRM.photo}
                  alt="CA Lokesh Dagdiya"
                  className="w-full h-auto object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent"></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-16 md:py-24 bg-gradient-to-b from-white to-gray-50 relative overflow-hidden">
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
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-6">
            {SERVICES.map((service) => (
              <div
                key={service.id}
                className="bg-white border-2 border-gray-200 rounded-xl p-4 md:p-5 hover:border-blue-600 hover:shadow-xl transition-all duration-300 group cursor-pointer"
              >
                <div className="w-12 h-12 md:w-14 md:h-14 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-lg flex items-center justify-center mb-3 group-hover:from-blue-600 group-hover:to-indigo-600 transition-all duration-300">
                  <FileText className="text-blue-600 group-hover:text-white transition-colors duration-300" size={20} />
                </div>
                <h3 className="text-sm md:text-base font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors leading-tight">
                  {service.title}
                </h3>
                <p className="text-xs md:text-sm text-gray-600 leading-relaxed line-clamp-3">{service.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Industries We Serve */}
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
            {INDUSTRIES.map((industry, idx) => {
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
      <section className="py-16 md:py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Client Testimonials</h2>
            <p className="text-xl text-gray-600">What our clients say about us</p>
          </div>
          {/* Mobile: Horizontal scroll, Desktop: Grid */}
          <div className="overflow-x-auto pb-4 -mx-4 px-4 md:overflow-visible md:mx-0 md:px-0">
            <div className="flex gap-6 md:grid md:grid-cols-3 min-w-max md:min-w-0">
              {TESTIMONIALS.map((testimonial) => (
                <div
                  key={testimonial.id}
                  className="bg-white rounded-xl p-6 border-2 border-gray-200 hover:border-blue-600 hover:shadow-xl transition-all duration-300 w-80 md:w-auto flex-shrink-0 md:flex-shrink"
                >
                  <div className="flex gap-1 mb-3">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        size={18}
                        className={`${
                          i < testimonial.rating
                            ? 'text-yellow-400 fill-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-gray-700 italic mb-4 leading-relaxed text-sm">
                    &ldquo;{testimonial.text}&rdquo;
                  </p>
                  <div className="flex items-center gap-3 pt-3 border-t border-gray-200">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold text-sm">
                      {testimonial.client_name.charAt(0)}
                    </div>
                    <div>
                      <p className="font-bold text-gray-900 text-sm">{testimonial.client_name}</p>
                      <p className="text-xs text-gray-500">Valued Client</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

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
                <div className="flex items-start gap-4">
                  <MapPin className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                  <div>
                    <p className="font-semibold">Address</p>
                    <p className="text-gray-300">{FIRM.address}</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Phone className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                  <div>
                    <p className="font-semibold">Phone</p>
                    <a href={`tel:${FIRM.phone}`} className="text-gray-300 hover:text-blue-400 transition">
                      {FIRM.phone}
                    </a>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Mail className="text-blue-400 flex-shrink-0 mt-1" size={24} />
                  <div>
                    <p className="font-semibold">Email</p>
                    <a href={`mailto:${FIRM.email}`} className="text-gray-300 hover:text-blue-400 transition">
                      {FIRM.email}
                    </a>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-white text-gray-900 rounded-xl p-8">
              <h3 className="text-2xl font-bold mb-6">Quick Inquiry</h3>
              <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
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
          <p>&copy; {new Date().getFullYear()} {FIRM.name}. All rights reserved.</p>
          <p className="mt-2 text-sm">Powered by DocManager</p>
        </div>
      </footer>

      <style>{`
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
