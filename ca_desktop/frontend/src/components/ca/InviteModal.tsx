import React, { useState } from 'react';
import { X, Copy, Check, Share2, QrCode } from 'lucide-react';

interface InviteData {
  portal_url: string;
  username: string;
  password: string;
  qr_code_base64: string;
  whatsapp_share_url: string;
  client_directory?: string;
}

interface InviteModalProps {
  isOpen: boolean;
  onClose: () => void;
  inviteData: InviteData | null;
  clientName: string;
}

export const InviteModal: React.FC<InviteModalProps> = ({
  isOpen,
  onClose,
  inviteData,
  clientName,
}) => {
  const [copiedField, setCopiedField] = useState<string | null>(null);

  if (!isOpen || !inviteData) return null;

  const copyToClipboard = async (text: string, field: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedField(field);
      setTimeout(() => setCopiedField(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  const handleWhatsAppShare = () => {
    window.open(inviteData.whatsapp_share_url, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 rounded-t-lg flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold">Client Portal Invite</h2>
            <p className="text-indigo-100 text-sm mt-1">{clientName}</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <p className="text-gray-600 mb-6">
            Share these credentials with your client to give them access to their portal.
          </p>

          {/* Portal URL */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Portal URL
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inviteData.portal_url}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-800 font-mono text-sm"
              />
              <button
                onClick={() => copyToClipboard(inviteData.portal_url, 'url')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
              >
                {copiedField === 'url' ? (
                  <>
                    <Check size={16} />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={16} />
                    Copy
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Username */}
          <div className="mb-4">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Username (Phone Number)
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inviteData.username}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-800 font-mono text-sm"
              />
              <button
                onClick={() => copyToClipboard(inviteData.username, 'username')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
              >
                {copiedField === 'username' ? (
                  <>
                    <Check size={16} />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={16} />
                    Copy
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Password */}
          <div className="mb-6">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Password
            </label>
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={inviteData.password}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-800 font-mono text-sm"
              />
              <button
                onClick={() => copyToClipboard(inviteData.password, 'password')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition flex items-center gap-2"
              >
                {copiedField === 'password' ? (
                  <>
                    <Check size={16} />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy size={16} />
                    Copy
                  </>
                )}
              </button>
            </div>
            <p className="text-xs text-amber-600 mt-2 flex items-start gap-1">
              <span className="font-semibold">⚠️</span>
              <span>This password will only be shown once. Make sure to save it securely.</span>
            </p>
          </div>

          {/* QR Code */}
          <div className="mb-6 bg-gray-50 rounded-lg p-6 border border-gray-200">
            <div className="flex items-center gap-2 mb-4">
              <QrCode size={20} className="text-indigo-600" />
              <h3 className="font-semibold text-gray-800">QR Code</h3>
            </div>
            <div className="flex justify-center">
              <img
                src={inviteData.qr_code_base64}
                alt="Portal QR Code"
                className="w-64 h-64 border-4 border-white shadow-lg rounded-lg"
              />
            </div>
            <p className="text-sm text-gray-600 text-center mt-4">
              Client can scan this QR code to access the portal directly
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleWhatsAppShare}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center justify-center gap-2 font-semibold"
            >
              <Share2 size={20} />
              Share on WhatsApp
            </button>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition font-semibold"
            >
              Close
            </button>
          </div>

          {/* Client Directory */}
          {inviteData.client_directory && (
            <div className="mt-6 bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800 font-semibold mb-2">
                📁 Client Directory Created
              </p>
              <p className="text-xs text-green-700 font-mono bg-white px-3 py-2 rounded border border-green-200">
                {inviteData.client_directory}
              </p>
              <p className="text-xs text-green-600 mt-2">
                Upload documents to this directory for the client.
              </p>
            </div>
          )}

          {/* Info Box */}
          <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              <strong>💡 Tip:</strong> You can share the credentials via WhatsApp, email, or by showing the QR code to your client.
              The client should change their password after first login for security.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
