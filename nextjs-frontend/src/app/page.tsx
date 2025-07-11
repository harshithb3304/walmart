'use client';

import { useState, useEffect } from 'react';
import { ShoppingCart, Send } from 'lucide-react';
import VoiceInterface from '@/components/VoiceInterface/VoiceInterface';
import ImageUpload from '@/components/ProductSearch/ImageUpload';
import ProductCard from '@/components/ProductSearch/ProductCard';
import CartSidebar from '@/components/Cart/CartSidebar';

interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
  image_url: string;
  description: string;
  rating: number;
}

interface Message {
  role: 'user' | 'assistant';
  message: string;
  timestamp: string;
}

export default function Home() {
  const [isListening, setIsListening] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);

interface CartItem {
  id: string;
  name: string;
  price: number;
  image_url: string;
  quantity: number;
  added_at: string;
}
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Load initial recommendations
  useEffect(() => {
    loadRecommendations();
    loadCart();
  }, []);

  const loadRecommendations = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/products/recommendations');
      const data = await response.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Failed to load recommendations:', error);
    }
  };

  const loadCart = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/cart');
      const data = await response.json();
      setCartItems(data.items || []);
    } catch (error) {
      console.error('Failed to load cart:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userMessage = { role: 'user' as const, message: chatInput, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: chatInput }),
      });

      const data = await response.json();
      const assistantMessage = { 
        role: 'assistant' as const, 
        message: data.response, 
        timestamp: new Date().toISOString() 
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Trigger product search for relevant queries
      const searchKeywords = ['headphones', 'phone', 'iphone', 'smartphone', 'electronics', 'gadgets', 'shoes', 'nike', 'mouse', 'gaming', 'search', 'show', 'find'];
      if (searchKeywords.some(keyword => chatInput.toLowerCase().includes(keyword))) {
        searchProducts(chatInput);
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchProducts = async (query: string) => {
    try {
      const response = await fetch(`http://localhost:5000/api/products/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const handleImageSearch = async (file: File) => {
    const formData = new FormData();
    formData.append('image', file);

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:5000/api/products/image-search', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setProducts(data.products || []);
      
      // Add message about image search
      const message = { 
        role: 'assistant' as const, 
        message: `I found ${data.products?.length || 0} products matching your image in the ${data.recognized_category} category.`, 
        timestamp: new Date().toISOString() 
      };
      setMessages(prev => [...prev, message]);
    } catch (error) {
      console.error('Image search error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (productId: string) => {
    try {
      const response = await fetch('http://localhost:5000/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });

      if (response.ok) {
        loadCart();
        const message = { 
          role: 'assistant' as const, 
          message: 'Item added to your cart successfully!', 
          timestamp: new Date().toISOString() 
        };
        setMessages(prev => [...prev, message]);
      }
    } catch (error) {
      console.error('Add to cart error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-blue-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <ShoppingCart className="h-8 w-8 text-white" />
              </div>
              <div className="ml-3">
                <h1 className="text-2xl font-bold text-gray-900">AI Shopping Agent</h1>
                <p className="text-sm text-gray-600">Voice & Visual Shopping Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors"
            >
              <ShoppingCart className="h-5 w-5" />
              Cart ({cartItems.length})
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Chat Interface */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-lg p-6 h-96 flex flex-col">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Chat with AI Assistant</h2>
              
              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4">
                {messages.length === 0 && (
                  <div className="text-center text-gray-500 mt-8">
                    <p>👋 Hi! I&apos;m your AI shopping assistant.</p>
                    <p>🗣️ <strong>Voice:</strong> Click the mic and say &quot;show me red iphones&quot;</p>
                    <p>⌨️ <strong>Type:</strong> &quot;I need headphones under 3000&quot;</p>
                    <p>📷 <strong>Visual:</strong> Upload a product image below</p>
                    <p className="text-sm mt-2">Try any combination - I understand all!</p>
                  </div>
                )}
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.role === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm">{msg.message}</p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg">
                      <p className="text-sm">AI is thinking...</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type your message or use voice..."
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-500"
                />
                <VoiceInterface 
                  isListening={isListening}
                  setIsListening={setIsListening}
                  onVoiceInput={(text) => {
                    setChatInput(text);
                    // Auto-send voice input after a short delay
                    setTimeout(() => {
                      if (text.trim()) {
                        handleSendMessage();
                      }
                    }, 500);
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim() || isLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>

            {/* Image Upload */}
            <div className="mt-6">
              <ImageUpload onImageUpload={handleImageSearch} />
            </div>
          </div>

          {/* Product Results */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                {products.length > 0 ? 'Search Results' : 'Recommended Products'}
              </h2>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {products.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={() => addToCart(product.id)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Cart Sidebar */}
      <CartSidebar 
        isOpen={isCartOpen}
        onClose={() => setIsCartOpen(false)}
        items={cartItems}
        onUpdateCart={loadCart}
      />
    </div>
  );
}
