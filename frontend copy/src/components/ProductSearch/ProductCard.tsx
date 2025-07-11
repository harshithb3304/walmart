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
    <div className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      {/* Product Image */}
      <div className="relative mb-3">
        <Image
          src={product.image_url || 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=300&h=200&fit=crop'}
          alt={product.name}
          width={300}
          height={128}
          className="w-full h-32 object-cover rounded-md"
          unoptimized
        />
        <div className="absolute top-2 right-2">
          <button className="bg-white/80 hover:bg-white p-1 rounded-full transition-colors">
            <Heart className="h-4 w-4 text-gray-600" />
          </button>
        </div>
        {product.stock && product.stock < 10 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white text-xs px-2 py-1 rounded">
            Only {product.stock} left
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="space-y-2">
        <div>
          <h3 className="font-semibold text-gray-900 text-sm line-clamp-2 leading-tight">
            {product.name}
          </h3>
          <p className="text-xs text-gray-600 mt-1">{product.category}</p>
        </div>

        {/* Rating */}
        <div className="flex items-center gap-1">
          <div className="flex">
            {renderStars(product.rating)}
          </div>
          <span className="text-xs text-gray-600">({product.rating})</span>
        </div>

        {/* Description */}
        <p className="text-xs text-gray-600 line-clamp-2">
          {product.description}
        </p>

        {/* Price */}
        <div className="flex items-center justify-between">
          <div>
            <span className="text-lg font-bold text-gray-900">
              {formatPrice(product.price)}
            </span>
          </div>
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={onAddToCart}
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-3 rounded-md flex items-center justify-center gap-2 transition-colors text-sm font-medium"
        >
          <ShoppingCart className="h-4 w-4" />
          Add to Cart
        </button>
      </div>
    </div>
  );
} 