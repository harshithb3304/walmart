'use client';

import { Star, ShoppingCart, Heart } from 'lucide-react';
import Image from 'next/image';

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  image_url: string;
  description: string;
  rating: number;
  stock?: number;
}

interface ProductCardProps {
  product: Product;
  onAddToCart: () => void;
}

export default function ProductCard({ product, onAddToCart }: ProductCardProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const renderStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
      );
    }

    if (hasHalfStar) {
      stars.push(
        <Star key="half" className="h-4 w-4 fill-yellow-400/50 text-yellow-400" />
      );
    }

    const emptyStars = 5 - Math.ceil(rating);
    for (let i = 0; i < emptyStars; i++) {
      stars.push(
        <Star key={`empty-${i}`} className="h-4 w-4 text-gray-300" />
      );
    }

    return stars;
  };

  return (
    <div className="bg-white/90 backdrop-blur-sm border border-purple-100 rounded-2xl p-5 hover:shadow-2xl transition-all duration-300 transform hover:scale-[1.02] group relative overflow-hidden">
      {/* Decorative background */}
      <div className="absolute top-0 right-0 w-16 h-16 bg-gradient-to-br from-purple-100/30 to-blue-100/30 rounded-full blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      
      {/* Product Image */}
      <div className="relative mb-4">
        <Image
          src={product.image_url || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop'}
          alt={product.name}
          width={300}
          height={128}
          className="w-full h-32 object-cover rounded-xl shadow-md group-hover:shadow-lg transition-shadow duration-300"
          unoptimized
        />
        <div className="absolute top-3 right-3">
          <button className="bg-white/90 hover:bg-white p-2 rounded-full transition-all duration-200 transform hover:scale-110 shadow-lg">
            <Heart className="h-4 w-4 text-gray-600 hover:text-red-500 transition-colors" />
          </button>
        </div>
        {product.stock && product.stock < 10 && (
          <div className="absolute top-3 left-3 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs px-3 py-1 rounded-full font-semibold shadow-lg animate-pulse">
            Only {product.stock} left!
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="space-y-3 relative z-10">
        <div>
          <h3 className="font-bold text-gray-900 text-sm line-clamp-2 leading-tight group-hover:text-purple-700 transition-colors">
            {product.name}
          </h3>
          <span className="inline-block bg-gradient-to-r from-purple-100 to-blue-100 text-purple-700 text-xs px-2 py-1 rounded-full mt-2 font-medium">
            {product.category}
          </span>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-2">
          <div className="flex">
            {renderStars(product.rating)}
          </div>
          <span className="text-xs text-gray-600 font-medium">({product.rating})</span>
        </div>

        {/* Description */}
        <p className="text-xs text-gray-600 line-clamp-2 leading-relaxed">
          {product.description}
        </p>

        {/* Price */}
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              {formatPrice(product.price)}
            </span>
          </div>
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={onAddToCart}
          className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all duration-300 text-sm font-semibold shadow-lg hover:shadow-xl transform hover:scale-105 group/btn"
        >
          <ShoppingCart className="h-4 w-4 group-hover/btn:animate-bounce" />
          Add to Cart
        </button>
      </div>
    </div>
  );
} 