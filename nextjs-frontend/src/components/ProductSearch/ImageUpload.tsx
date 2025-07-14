'use client';

import { useState, useRef } from 'react';
import { Upload, Camera, X } from 'lucide-react';
import Image from 'next/image';

interface ImageUploadProps {
  onImageUpload: (file: File) => void;
}

export default function ImageUpload({ onImageUpload }: ImageUploadProps) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);

    const files = e.dataTransfer.files;
    if (files[0] && files[0].type.startsWith('image/')) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    setIsUploading(true);

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setSelectedImage(e.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Upload to backend
    try {
      await onImageUpload(file);
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const clearImage = () => {
    setSelectedImage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="h-full bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8 relative overflow-hidden">
      {/* Decorative background */}
      {/* <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-100/20 to-blue-100/20 rounded-full blur-3xl"></div> */}

      <div className="mb-2 flex items-center gap-3 relative z-10">
        <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl">
          <Camera className="h-5 w-5 text-white" />
        </div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
          📷 Visual Search
        </h2>
      </div>

      {!selectedImage ? (
        <div
          className={`rounded-2xl border-2 border-dashed p-2 text-center transition-all duration-300 relative z-10 flex items-center justify-center min-h-[250px] max-w-[470px] mx-auto ${dragOver
              ? 'border-purple-400 bg-gradient-to-br from-purple-50 to-blue-50 transform scale-105'
              : 'border-purple-200 hover:border-purple-300 hover:bg-gradient-to-br hover:from-purple-25 hover:to-blue-25'
            }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center space-y-4 w-full">
            <div className={`p-2 rounded-2xl transition-all duration-300 ${dragOver
                ? 'bg-gradient-to-r from-purple-500 to-blue-500 transform scale-105'
                : 'bg-gradient-to-r from-purple-100 to-blue-100'
              }`}>
              <Upload className={`h-5 w-5 transition-colors ${dragOver ? 'text-white' : 'text-purple-600'
                }`} />
            </div>

            <div>
              <p className="text-base font-bold text-gray-800 mb-1">✨ Upload Product Image</p>
              <p className="text-xs text-gray-600">
                Drag & drop an image or click to browse
              </p>
              <p className="text-xs text-purple-600 mt-1">
                🔍 Find similar products instantly!
              </p>
            </div>

            <button
              onClick={() => fileInputRef.current?.click()}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-4 py-2 rounded-xl flex items-center gap-2 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 font-semibold text-xs"
            >
              <Camera className="h-4 w-4" />
              Choose Image
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />

            <p className="text-xs text-gray-500">
              Supports: JPG, PNG, GIF (Max 10MB)
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative group">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-200 to-blue-200 rounded-xl opacity-75 blur-sm"></div>
            <div className="relative bg-white/80 backdrop-blur-sm rounded-xl p-3 border border-white/20">
              <Image
                src={selectedImage}
                alt="Uploaded product"
                width={400}
                height={192}
                className="w-full h-48 object-cover rounded-lg shadow-md"
                unoptimized
              />
              <button
                onClick={clearImage}
                className="absolute top-5 right-5 bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white p-2 rounded-full transition-all duration-300 transform hover:scale-110 shadow-lg"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </div>

          {isUploading && (
            <div className="flex items-center justify-center py-6">
              <div className="relative">
                <div className="animate-spin rounded-full h-10 w-10 border-4 border-purple-200"></div>
                <div className="animate-spin rounded-full h-10 w-10 border-4 border-purple-600 border-t-transparent absolute top-0 left-0"></div>
              </div>
              <span className="ml-3 text-transparent bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text font-medium">
                Analyzing image with AI...
              </span>
            </div>
          )}

          <div className="flex gap-3">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="flex-1 bg-gradient-to-r from-gray-100 to-gray-200 hover:from-gray-200 hover:to-gray-300 text-gray-700 px-6 py-3 rounded-xl transition-all duration-300 font-medium shadow-sm hover:shadow-md transform hover:scale-[1.02]"
            >
              Upload Different Image
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>
        </div>
      )}

      {/* <div className="mt-6 relative">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-100 to-purple-100 rounded-xl opacity-80"></div>
        <div className="relative bg-white/70 backdrop-blur-sm rounded-xl p-4 border border-white/30">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg">
              <Camera className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800 mb-1">
                🔍 Visual Search Powered by AI
              </p>
              <p className="text-xs text-gray-600 leading-relaxed">
                Upload an image and our AI will identify products and find similar items in our catalog.
                Get instant results with smart visual recognition technology.
              </p>
            </div>
          </div>
        </div>
      </div> */}
    </div>
  );
} 