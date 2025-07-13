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
      console.log('Loading cart...');
      const response = await fetch('http://localhost:5000/api/cart');
      const data = await response.json();
      console.log('Cart loaded:', data);
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

      // Check if the chat response includes products and display them
      if (data.products && data.products.length > 0) {
        console.log('Products found in chat response:', data.products.length);
        setProducts(data.products);
      } else {
        // Trigger product search for relevant queries if no products in response
        const searchKeywords = ['headphones', 'phone', 'iphone', 'smartphone', 'electronics', 'gadgets', 'shoes', 'nike', 'mouse', 'gaming', 'search', 'show', 'find'];
        if (searchKeywords.some(keyword => chatInput.toLowerCase().includes(keyword))) {
          console.log('No products in chat response, triggering search for:', chatInput);
          searchProducts(chatInput);
        }
      }

      // Check if cart was updated through chat (add to cart via chat)
      if (data.action === 'cart_updated' || 
          data.cart_summary || 
          data.message?.toLowerCase().includes('added to cart') ||
          data.response?.toLowerCase().includes('added to cart') ||
          data.response?.includes('✅') ||
          chatInput.toLowerCase().includes('add') && chatInput.toLowerCase().includes('cart')) {
        console.log('Cart updated through chat, reloading cart...');
        loadCart();
      }
    } catch (error) {
      console.error('Chat error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const searchProducts = async (query: string) => {
    try {
      console.log('Searching products for query:', query);
      const response = await fetch(`http://localhost:5000/api/products/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      console.log('Search API response:', data);
      
      if (data.products && data.products.length > 0) {
        console.log('Setting products from search:', data.products.length);
        setProducts(data.products);
      } else {
        console.log('No products found in search');
        setProducts([]);
        // Add message about no results
        const noResultsMessage = { 
          role: 'assistant' as const, 
          message: `I couldn't find any products matching "${query}". Try being more specific or browse our recommended products.`, 
          timestamp: new Date().toISOString() 
        };
        setMessages(prev => [...prev, noResultsMessage]);
      }
    } catch (error) {
      console.error('Search error:', error);
      setProducts([]);
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
      if (data.products && data.products.length > 0) {
        setProducts(data.products);
        
        // Add message about image search
        const message = { 
          role: 'assistant' as const, 
          message: `I found ${data.products.length} products matching your image in the ${data.recognized_category || 'various'} category. Check the search results on the right!`, 
          timestamp: new Date().toISOString() 
        };
        setMessages(prev => [...prev, message]);
      } else {
        // No products found
        const message = { 
          role: 'assistant' as const, 
          message: `I couldn't find any products matching your image. Try uploading a clearer image or describe what you're looking for in the chat.`, 
          timestamp: new Date().toISOString() 
        };
        setMessages(prev => [...prev, message]);
      }
    } catch (error) {
      console.error('Image search error:', error);
      const errorMessage = { 
        role: 'assistant' as const, 
        message: 'Sorry, there was an error processing your image. Please try again or describe what you\'re looking for in the chat.', 
        timestamp: new Date().toISOString() 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const addToCart = async (productId: string) => {
    try {
      console.log('Adding product to cart:', productId);
      const response = await fetch('http://localhost:5000/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
      });

      if (response.ok) {
        console.log('Product added successfully, reloading cart...');
        loadCart();
        const message = { 
          role: 'assistant' as const, 
          message: 'Item added to your cart successfully! Check your cart in the top-right corner.', 
          timestamp: new Date().toISOString() 
        };
        setMessages(prev => [...prev, message]);
      } else {
        console.error('Failed to add to cart, response not ok');
        const errorMessage = { 
          role: 'assistant' as const, 
          message: 'Sorry, there was an error adding the item to your cart. Please try again.', 
          timestamp: new Date().toISOString() 
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Add to cart error:', error);
      const errorMessage = { 
        role: 'assistant' as const, 
        message: 'Sorry, there was an error adding the item to your cart. Please try again.', 
        timestamp: new Date().toISOString() 
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg shadow-xl border-b border-purple-200/50 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-purple-600 via-blue-600 to-indigo-600 p-3 rounded-2xl shadow-lg transform hover:scale-105 transition-transform duration-200">
                <ShoppingCart className="h-8 w-8 text-white" />
              </div>
              <div className="ml-4">
                <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  AI Shopping Agent
                </h1>
                <p className="text-sm text-gray-600 font-medium">✨ Voice & Visual Shopping Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsCartOpen(true)}
              className="relative bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-6 py-3 rounded-2xl flex items-center gap-3 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              <ShoppingCart className="h-5 w-5" />
              <span className="font-semibold">Cart ({cartItems.length})</span>
              {cartItems.length > 0 && (
                <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center animate-pulse">
                  {cartItems.length}
                </div>
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 min-h-[800px]">
          
          {/* Left Column - Chat Interface Only */}
          <div className="flex flex-col">
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8 h-full flex flex-col relative overflow-hidden">
              {/* Decorative background */}
              <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-200/30 to-blue-200/30 rounded-full blur-3xl"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-gradient-to-tr from-indigo-200/30 to-purple-200/30 rounded-full blur-2xl"></div>
              
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl">
                  <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
                </div>
                <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  💬 Chat with AI Assistant
                </h2>
              </div>
              
              {/* Messages */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-6 relative z-10 scrollbar-thin scrollbar-thumb-purple-300 scrollbar-track-purple-100">
                {messages.length === 0 && (
                  <div className="text-center text-gray-600 mt-12 space-y-4">
                    <div className="text-6xl mb-4">🤖</div>
                    <p className="text-lg font-semibold text-gray-700">👋 Hi! I'm your AI shopping assistant.</p>
                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-6 space-y-3">
                      <p className="flex items-center gap-2"><span className="text-2xl">🗣️</span> <strong>Voice:</strong> Click the mic and say "show me red iphones"</p>
                      <p className="flex items-center gap-2"><span className="text-2xl">⌨️</span> <strong>Type:</strong> "I need headphones under 3000"</p>
                      <p className="flex items-center gap-2"><span className="text-2xl">📷</span> <strong>Visual:</strong> Upload a product image on the right</p>
                    </div>
                    <p className="text-sm mt-4 text-purple-600 font-medium">✨ Try any combination - I understand all!</p>
                  </div>
                )}
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                    <div className={`max-w-xs lg:max-w-md px-6 py-4 rounded-2xl shadow-lg ${
                      msg.role === 'user' 
                        ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white transform hover:scale-105 transition-transform duration-200' 
                        : 'bg-white border border-gray-200 text-gray-800 shadow-md'
                    }`}>
                      <p className="text-sm leading-relaxed">{msg.message}</p>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start animate-fadeIn">
                    <div className="bg-white border border-gray-200 text-gray-800 px-6 py-4 rounded-2xl shadow-lg">
                      <div className="flex items-center gap-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-indigo-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                        <p className="text-sm ml-2">AI is thinking...</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Input Area */}
              <div className="flex gap-3 relative z-10">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Type your message or use voice..."
                  className="flex-1 border-2 border-purple-200 rounded-2xl px-6 py-4 focus:outline-none focus:ring-4 focus:ring-purple-300/50 focus:border-purple-400 text-gray-800 bg-white/80 backdrop-blur-sm placeholder-gray-500 transition-all duration-200 shadow-lg"
                />
                <VoiceInterface 
                  isListening={isListening}
                  setIsListening={setIsListening}
                  onVoiceInput={(text) => {
                    setChatInput(text);
                    // Send voice input immediately to backend
                    setTimeout(() => {
                      if (text.trim()) {
                        // Create a custom send function to ensure we use the voice text
                        const sendVoiceMessage = async () => {
                          const userMessage = { role: 'user' as const, message: text, timestamp: new Date().toISOString() };
                          setMessages(prev => [...prev, userMessage]);
                          setChatInput(''); // Clear input after sending
                          setIsLoading(true);

                          try {
                            const response = await fetch('http://localhost:5000/api/chat', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ message: text }),
                            });

                            const data = await response.json();
                            const assistantMessage = { 
                              role: 'assistant' as const, 
                              message: data.response, 
                              timestamp: new Date().toISOString() 
                            };
                            setMessages(prev => [...prev, assistantMessage]);

                            // Check if the chat response includes products and display them
                            if (data.products && data.products.length > 0) {
                              console.log('Products found in voice chat response:', data.products.length);
                              setProducts(data.products);
                            } else {
                              // Trigger product search for relevant queries if no products in response
                              const searchKeywords = ['headphones', 'phone', 'iphone', 'smartphone', 'electronics', 'gadgets', 'shoes', 'nike', 'mouse', 'gaming', 'search', 'show', 'find'];
                              if (searchKeywords.some(keyword => text.toLowerCase().includes(keyword))) {
                                console.log('No products in voice chat response, triggering search for:', text);
                                searchProducts(text);
                              }
                            }

                            // Check if cart was updated through voice chat
                            if (data.action === 'cart_updated' || 
                                data.cart_summary || 
                                data.message?.toLowerCase().includes('added to cart') ||
                                data.response?.toLowerCase().includes('added to cart') ||
                                data.response?.includes('✅') ||
                                text.toLowerCase().includes('add') && text.toLowerCase().includes('cart')) {
                              console.log('Cart updated through voice chat, reloading cart...');
                              loadCart();
                            }
                          } catch (error) {
                            console.error('Voice chat error:', error);
                            const errorMessage = { 
                              role: 'assistant' as const, 
                              message: 'Sorry, there was an error processing your voice input. Please try again.', 
                              timestamp: new Date().toISOString() 
                            };
                            setMessages(prev => [...prev, errorMessage]);
                          } finally {
                            setIsLoading(false);
                          }
                        };
                        sendVoiceMessage();
                      }
                    }, 150); // Slightly longer delay to ensure state updates
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim() || isLoading}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-4 rounded-2xl transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
                >
                  <Send className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Products on Top, Image Upload on Bottom */}
          <div className="flex flex-col gap-8">
            {/* Product Results */}
            <div className="bg-white/90 backdrop-blur-sm rounded-3xl shadow-2xl border border-white/20 p-8 relative overflow-hidden flex-1">
              {/* Decorative background */}
              <div className="absolute top-0 left-0 w-20 h-20 bg-gradient-to-br from-purple-200/20 to-blue-200/20 rounded-full blur-2xl"></div>
              
              <div className="flex items-center gap-3 mb-6 relative z-10">
                <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl">
                  <div className="w-3 h-3 bg-white rounded-full"></div>
                </div>
                <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  {products.length > 0 ? `🔍 Search Results (${products.length})` : '⭐ Recommended Products'}
                </h2>
              </div>
              
              <div className="space-y-4 max-h-[400px] overflow-y-auto relative z-10 scrollbar-thin scrollbar-thumb-purple-300 scrollbar-track-purple-100">
                {products.length > 0 ? (
                  products.map((product, index) => (
                    <div key={product.id} className="animate-fadeIn" style={{animationDelay: `${index * 0.1}s`}}>
                      <ProductCard
                        product={product}
                        onAddToCart={() => addToCart(product.id)}
                      />
                    </div>
                  ))
                ) : (
                  <div className="text-center text-gray-500 py-12 space-y-4">
                    <div className="text-5xl mb-4">🛍️</div>
                    <p className="text-lg font-semibold text-gray-600">💡 Start chatting to discover products!</p>
                    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-4 space-y-2">
                      <p className="text-sm text-purple-600 font-medium">✨ Try asking:</p>
                      <p className="text-xs text-gray-600">"Show me wireless headphones"</p>
                      <p className="text-xs text-gray-600">"I need a laptop"</p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Image Upload */}
            <div className="flex-shrink-0">
              <ImageUpload onImageUpload={handleImageSearch} />
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
