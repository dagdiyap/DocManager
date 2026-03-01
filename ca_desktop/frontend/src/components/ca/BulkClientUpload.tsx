import React, { useState } from 'react';
import { Upload, X, FileSpreadsheet, FileText, CheckCircle, AlertCircle, Users } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import api from '../../api';

interface BulkUploadProps {
  isOpen: boolean;
  onClose: () => void;
}

interface UploadResult {
  success: boolean;
  summary: {
    total_in_file: number;
    file_duplicates: number;
    unique_clients: number;
    created: number;
    skipped_existing: number;
    errors: number;
  };
  created_clients: Array<{
    phone_number: string;
    name: string;
    password: string;
  }>;
  skipped_phones: string[];
  errors: string[];
}

export const BulkClientUpload: React.FC<BulkUploadProps> = ({ isOpen, onClose }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [showResults, setShowResults] = useState(false);
  const queryClient = useQueryClient();

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await api.post('/clients/bulk-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
    onSuccess: (data: UploadResult) => {
      setUploadResult(data);
      setShowResults(true);
      queryClient.invalidateQueries({ queryKey: ['admin-clients'] });
      
      if (data.summary.created > 0) {
        toast.success(`Successfully created ${data.summary.created} clients!`);
      }
      if (data.summary.errors > 0) {
        toast.error(`${data.summary.errors} errors occurred`);
      }
    },
    onError: (err: any) => {
      toast.error(err.response?.data?.detail || 'Upload failed');
    },
  });

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const ext = file.name.toLowerCase();
      if (ext.endsWith('.xlsx') || ext.endsWith('.txt')) {
        setSelectedFile(file);
        setUploadResult(null);
        setShowResults(false);
      } else {
        toast.error('Please select .xlsx or .txt file');
      }
    }
  };

  const handleUpload = () => {
    if (selectedFile) {
      uploadMutation.mutate(selectedFile);
    }
  };

  const handleClose = () => {
    setSelectedFile(null);
    setUploadResult(null);
    setShowResults(false);
    onClose();
  };

  const downloadCredentials = () => {
    if (!uploadResult) return;

    const csvContent = [
      'Phone Number,Name,Password',
      ...uploadResult.created_clients.map(
        (c) => `${c.phone_number},${c.name},${c.password}`
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `client_credentials_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-3xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-4 rounded-t-2xl flex justify-between items-center">
          <div className="flex items-center gap-3">
            <Users size={28} />
            <div>
              <h2 className="text-2xl font-bold">Bulk Client Upload</h2>
              <p className="text-indigo-100 text-sm">Upload Excel or Text file</p>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition"
          >
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {!showResults ? (
            <>
              {/* Instructions */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-2">📋 File Format Instructions</h3>
                <div className="text-sm text-blue-800 space-y-2">
                  <p><strong>Excel (.xlsx):</strong></p>
                  <ul className="list-disc list-inside ml-4">
                    <li>Automatically detects phone, name, and email columns</li>
                    <li>Phone numbers: 10 digits (with or without +91 prefix)</li>
                    <li>Example: 9876543210 or +919876543210</li>
                  </ul>
                  <p className="mt-2"><strong>Text (.txt):</strong></p>
                  <ul className="list-disc list-inside ml-4">
                    <li>Format: phone,name,email (one per line)</li>
                    <li>Or just phone numbers (one per line)</li>
                    <li>Example: 9876543210,John Doe,john@example.com</li>
                  </ul>
                </div>
              </div>

              {/* File Upload Area */}
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:border-indigo-500 transition">
                <input
                  type="file"
                  id="file-upload"
                  accept=".xlsx,.txt"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                <label htmlFor="file-upload" className="cursor-pointer">
                  {selectedFile ? (
                    <div className="flex items-center justify-center gap-3 text-indigo-600">
                      {selectedFile.name.endsWith('.xlsx') ? (
                        <FileSpreadsheet size={48} />
                      ) : (
                        <FileText size={48} />
                      )}
                      <div className="text-left">
                        <p className="font-semibold text-lg">{selectedFile.name}</p>
                        <p className="text-sm text-gray-600">
                          {(selectedFile.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <Upload size={48} className="mx-auto text-gray-400 mb-3" />
                      <p className="text-lg font-semibold text-gray-700 mb-1">
                        Click to upload file
                      </p>
                      <p className="text-sm text-gray-500">
                        Supports .xlsx and .txt files
                      </p>
                    </div>
                  )}
                </label>
              </div>

              {/* Upload Button */}
              {selectedFile && (
                <div className="mt-6 flex gap-3">
                  <button
                    onClick={handleUpload}
                    disabled={uploadMutation.isPending}
                    className="flex-1 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-xl font-bold hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {uploadMutation.isPending ? 'Uploading...' : 'Upload & Create Clients'}
                  </button>
                  <button
                    onClick={() => setSelectedFile(null)}
                    className="px-6 py-3 bg-gray-200 text-gray-800 rounded-xl font-semibold hover:bg-gray-300 transition"
                  >
                    Clear
                  </button>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Results Summary */}
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-blue-600">
                      {uploadResult?.summary.total_in_file}
                    </p>
                    <p className="text-sm text-gray-600">Total in File</p>
                  </div>
                  <div className="bg-green-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-green-600">
                      {uploadResult?.summary.created}
                    </p>
                    <p className="text-sm text-gray-600">Created</p>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-yellow-600">
                      {uploadResult?.summary.skipped_existing}
                    </p>
                    <p className="text-sm text-gray-600">Already Exist</p>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-orange-600">
                      {uploadResult?.summary.file_duplicates}
                    </p>
                    <p className="text-sm text-gray-600">Duplicates in File</p>
                  </div>
                  <div className="bg-red-50 rounded-lg p-4 text-center">
                    <p className="text-2xl font-bold text-red-600">
                      {uploadResult?.summary.errors}
                    </p>
                    <p className="text-sm text-gray-600">Errors</p>
                  </div>
                </div>

                {/* Created Clients */}
                {uploadResult && uploadResult.created_clients.length > 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <CheckCircle className="text-green-600" size={20} />
                        <h3 className="font-semibold text-green-900">
                          Successfully Created ({uploadResult.created_clients.length})
                        </h3>
                      </div>
                      <button
                        onClick={downloadCredentials}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-semibold"
                      >
                        Download Credentials
                      </button>
                    </div>
                    <div className="max-h-48 overflow-y-auto space-y-2">
                      {uploadResult.created_clients.map((client, idx) => (
                        <div key={idx} className="bg-white rounded p-3 text-sm">
                          <p className="font-semibold">{client.name}</p>
                          <p className="text-gray-600">
                            {client.phone_number} • Password: {client.password}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Errors */}
                {uploadResult && uploadResult.errors.length > 0 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <AlertCircle className="text-red-600" size={20} />
                      <h3 className="font-semibold text-red-900">
                        Errors ({uploadResult.errors.length})
                      </h3>
                    </div>
                    <div className="max-h-48 overflow-y-auto space-y-1">
                      {uploadResult.errors.slice(0, 10).map((error, idx) => (
                        <p key={idx} className="text-sm text-red-700">
                          • {error}
                        </p>
                      ))}
                      {uploadResult.errors.length > 10 && (
                        <p className="text-sm text-red-600 font-semibold">
                          ... and {uploadResult.errors.length - 10} more errors
                        </p>
                      )}
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={() => {
                      setShowResults(false);
                      setSelectedFile(null);
                      setUploadResult(null);
                    }}
                    className="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 transition"
                  >
                    Upload Another File
                  </button>
                  <button
                    onClick={handleClose}
                    className="px-6 py-3 bg-gray-200 text-gray-800 rounded-xl font-semibold hover:bg-gray-300 transition"
                  >
                    Close
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
