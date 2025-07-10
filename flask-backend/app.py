from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import logging
import base64
import urllib.parse
import re

# Try to import optional dependencies with fallbacks
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    print("⚠️  Google GenerativeAI not available - using fallback responses")
    GEMINI_AVAILABLE = False
    genai = None

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    print("⚠️  python-dotenv not available - using os.environ")
    DOTENV_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    print("⚠️  requests not available - web search disabled")
    REQUESTS_AVAILABLE = False
    requests = None

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    print("⚠️  BeautifulSoup not available - web scraping disabled")
    BEAUTIFULSOUP_AVAILABLE = False
    BeautifulSoup = None

try:
    from googlesearch import search
    GOOGLESEARCH_AVAILABLE = True
except ImportError:
    print("⚠️  googlesearch not available - google search disabled")
    GOOGLESEARCH_AVAILABLE = False
    search = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_AVAILABLE and GEMINI_API_KEY and genai:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Gemini AI configured successfully")
    except Exception as e:
        logger.warning(f"Failed to configure Gemini: {e}")
        model = None
else:
    logger.warning("GEMINI_API_KEY not found or Gemini not available")
    model = None

app = Flask(__name__)
CORS(app)

# Global variables for cart and session
cart_items = []
conversation_history = []

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "AI Shopping Agent Backend",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/voice/speech-to-text', methods=['POST'])
def speech_to_text():
    """Convert speech audio to text using Whisper"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        
        # For now, return mock response (will integrate Whisper later)
        mock_text = "I need wireless headphones under 3000 rupees"
        
        return jsonify({
            "text": mock_text,
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Speech-to-text error: {str(e)}")
        return jsonify({"error": "Speech processing failed"}), 500

@app.route('/api/voice/text-to-speech', methods=['POST'])
def text_to_speech():
    """Convert text to speech using SpeechT5"""
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({"error": "No text provided"}), 400
        
        # For now, return mock response (will integrate SpeechT5 later)
        return jsonify({
            "audio_url": "/api/audio/mock_response.wav",
            "text": text,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Text-to-speech error: {str(e)}")
        return jsonify({"error": "TTS processing failed"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle conversational AI requests using Gemini"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        # Add to conversation history
        conversation_history.append({
            "role": "user",
            "message": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate enhanced AI response with web search
        ai_response, walmart_results, search_results = enhanced_ai_response(user_message)
        
        conversation_history.append({
            "role": "assistant", 
            "message": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        return jsonify({
            "response": ai_response,
            "conversation_history": conversation_history[-10:],  # Last 10 messages
            "walmart_results": walmart_results[:3] if walmart_results else [],
            "web_results": search_results[:3] if search_results else [],
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Chat processing failed"}), 500


def search_walmart(query, max_results=5):
    """Search Walmart website for products"""
    if not REQUESTS_AVAILABLE or not BEAUTIFULSOUP_AVAILABLE:
        logger.warning("Web scraping not available - returning mock results")
        return get_mock_walmart_results(query)
    
    try:
        # Format the search URL for Walmart
        search_url = f"https://www.walmart.com/search?q={urllib.parse.quote(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        
        # Look for product containers (Walmart's structure may change)
        product_elements = soup.find_all(['div', 'article'], class_=re.compile(r'search-result|product-card', re.I))[:max_results]
        
        for element in product_elements:
            try:
                # Extract product name
                name_elem = element.find(['h3', 'h4', 'span'], class_=re.compile(r'product-title|name', re.I))
                name = name_elem.get_text(strip=True) if name_elem else "Product Name"
                
                # Extract price
                price_elem = element.find(['span', 'div'], class_=re.compile(r'price|cost', re.I))
                price = price_elem.get_text(strip=True) if price_elem else "Price not available"
                
                # Extract rating if available
                rating_elem = element.find(['span', 'div'], class_=re.compile(r'rating|star', re.I))
                rating = rating_elem.get_text(strip=True) if rating_elem else "No rating"
                
                # Extract link
                link_elem = element.find('a', href=True)
                link = f"https://www.walmart.com{link_elem['href']}" if link_elem and link_elem['href'].startswith('/') else link_elem['href'] if link_elem else ""
                
                if name and name != "Product Name":
                    products.append({
                        'name': name[:100],  # Limit length
                        'price': price,
                        'rating': rating,
                        'link': link,
                        'source': 'Walmart'
                    })
            except Exception as e:
                logger.debug(f"Error parsing product element: {e}")
                continue
        
        return products
    
    except Exception as e:
        logger.error(f"Walmart search error: {e}")
        return []


def get_mock_walmart_results(query):
    """Return mock Walmart search results when scraping isn't available"""
    query_lower = query.lower()
    mock_results = []
    
    if any(word in query_lower for word in ["iphone", "phone"]):
        mock_results.append({
            'name': 'Apple iPhone 15 Pro Max',
            'price': '$1,199.00',
            'rating': '4.8/5',
            'link': 'https://www.walmart.com/iphone-15',
            'source': 'Walmart (Mock)'
        })
    elif any(word in query_lower for word in ["headphones", "audio"]):
        mock_results.append({
            'name': 'Sony WH-CH720N Wireless Headphones',
            'price': '$89.99',
            'rating': '4.5/5',
            'link': 'https://www.walmart.com/sony-headphones',
            'source': 'Walmart (Mock)'
        })
    elif any(word in query_lower for word in ["laptop", "computer"]):
        mock_results.append({
            'name': 'HP Pavilion Gaming Laptop',
            'price': '$699.99',
            'rating': '4.3/5',
            'link': 'https://www.walmart.com/hp-laptop',
            'source': 'Walmart (Mock)'
        })
    
    return mock_results


def web_search(query, max_results=3):
    """Perform a general web search"""
    if not GOOGLESEARCH_AVAILABLE or not REQUESTS_AVAILABLE:
        logger.warning("Web search not available - returning mock results")
        return get_mock_web_results(query)
        
    try:
        search_results = []
        
        # Use Google search
        for url in search(query, num_results=max_results, sleep_interval=1):
            try:
                # Get page content
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract title and snippet
                title = soup.find('title')
                title_text = title.get_text(strip=True) if title else "No title"
                
                # Try to get meta description or first paragraph
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and hasattr(meta_desc, 'get'):
                    snippet = meta_desc.get('content', '')[:200]
                else:
                    # Get first paragraph or div with text
                    paragraphs = soup.find_all(['p', 'div'], string=True)
                    snippet = ""
                    for p in paragraphs[:3]:
                        text = p.get_text(strip=True)
                        if len(text) > 50:
                            snippet = text[:200]
                            break
                
                search_results.append({
                    'title': title_text[:100],
                    'snippet': snippet,
                    'url': url
                })
                
            except Exception as e:
                logger.debug(f"Error fetching search result: {e}")
                continue
        
        return search_results
    
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return []


def enhanced_ai_response(user_message):
    """Generate AI response with web search and Walmart search capabilities"""
    try:
        user_msg_lower = user_message.lower()
        
        # Determine if this is a product search vs general query
        product_keywords = ['buy', 'purchase', 'price', 'cost', 'product', 'item', 'shopping', 'cart', 'store', 'walmart']
        tech_keywords = ['tech', 'technology', 'computer', 'software', 'hardware', 'phone', 'laptop', 'gaming', 'electronics']
        support_keywords = ['help', 'support', 'how to', 'problem', 'issue', 'fix', 'troubleshoot', 'error']
        
        is_product_search = any(keyword in user_msg_lower for keyword in product_keywords)
        is_tech_query = any(keyword in user_msg_lower for keyword in tech_keywords)
        is_support_query = any(keyword in user_msg_lower for keyword in support_keywords)
        
        search_results = []
        walmart_results = []
        
        # Perform appropriate searches
        if is_product_search or 'walmart' in user_msg_lower:
            # Search Walmart for products
            walmart_results = search_walmart(user_message)
        
        if is_tech_query or is_support_query or not is_product_search:
            # Perform web search for general information
            search_results = web_search(user_message)
        
        # Create context for Gemini with search results
        context_parts = [
            "You are an advanced AI shopping and tech support assistant. You help users with:",
            "1. Product searches and shopping advice",
            "2. Technical support and troubleshooting", 
            "3. General information and guidance",
            "4. Price comparisons and recommendations",
            "",
            f"User Query: {user_message}",
            ""
        ]
        
        if walmart_results:
            context_parts.append("=== WALMART SEARCH RESULTS ===")
            for i, product in enumerate(walmart_results[:3], 1):
                context_parts.append(f"{i}. {product['name']}")
                context_parts.append(f"   Price: {product['price']}")
                context_parts.append(f"   Rating: {product['rating']}")
                context_parts.append(f"   Link: {product['link']}")
                context_parts.append("")
        
        if search_results:
            context_parts.append("=== WEB SEARCH RESULTS ===")
            for i, result in enumerate(search_results, 1):
                context_parts.append(f"{i}. {result['title']}")
                context_parts.append(f"   {result['snippet']}")
                context_parts.append(f"   Source: {result['url']}")
                context_parts.append("")
        
        context_parts.extend([
            "Guidelines:",
            "- Use the search results to provide accurate, helpful information",
            "- For products, mention specific prices and features from Walmart results",
            "- For tech support, provide step-by-step solutions",
            "- Be conversational and helpful",
            "- Include relevant links when helpful",
            "- If no good results found, provide general guidance",
            "- Use Indian currency (₹) when applicable"
        ])
        
        full_context = "\n".join(context_parts)
        
        if model:
            response = model.generate_content(full_context)
            return response.text, walmart_results, search_results
        else:
            return get_fallback_response(user_message), walmart_results, search_results
            
    except Exception as e:
        logger.error(f"Enhanced AI response error: {e}")
        return get_fallback_response(user_message), [], []


def get_fallback_response(user_message):
    """Fallback response logic when Gemini is not available"""
    user_msg_lower = user_message.lower()
    
    if any(word in user_msg_lower for word in ["iphone", "phone", "smartphone"]):
        if "red" in user_msg_lower:
            return "I found red smartphones for you! Check the Apple iPhone 15 in red color for ₹79,999. Would you like me to add it to your cart?"
        else:
            return "I found several smartphones including the latest iPhone 15 for ₹79,999. Would you like to see more options?"
    elif any(word in user_msg_lower for word in ["headphones", "earphones", "audio"]):
        return "I found 5 wireless headphones under ₹3000. The top rated is Sony WH-CH720N at ₹2,999. Would you like me to add it to your cart?"
    elif any(word in user_msg_lower for word in ["electronics", "gadgets", "tech"]):
        return "Here are popular electronics: iPhone 15, Sony headphones, and gaming mouse. What specific type interests you?"
    elif any(word in user_msg_lower for word in ["shoes", "nike", "footwear"]):
        return "I found Nike Air Max 270 running shoes for ₹8,995. Great for sports and casual wear!"
    elif "add to cart" in user_msg_lower:
        return "I'll add that item to your cart! Which specific product would you like me to add?"
    elif any(word in user_msg_lower for word in ["search", "show", "find", "get", "want", "need"]):
        return "I'm ready to help you find products! I can search for electronics, clothing, shoes, or any other items. What are you looking for?"
    else:
        return "Hello! I can help you find and shop for products. Try saying 'show me phones' or 'I need headphones'. What can I help you find today?"

@app.route('/api/search/web', methods=['POST'])
def web_search_endpoint():
    """Web search endpoint for general queries"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        search_type = data.get('type', 'general')  # 'general', 'tech', 'walmart'
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        results = {
            "query": query,
            "walmart_results": [],
            "web_results": [],
            "ai_response": ""
        }
        
        if search_type == 'walmart' or search_type == 'product':
            results["walmart_results"] = search_walmart(query)
        
        if search_type == 'general' or search_type == 'tech':
            results["web_results"] = web_search(query)
        
        # Generate AI summary if Gemini is available
        if model and (results["walmart_results"] or results["web_results"]):
            try:
                context = f"Query: {query}\n\n"
                if results["walmart_results"]:
                    context += "Walmart Products Found:\n"
                    for product in results["walmart_results"][:3]:
                        context += f"- {product['name']} - {product['price']}\n"
                    context += "\n"
                
                if results["web_results"]:
                    context += "Web Search Results:\n"
                    for result in results["web_results"][:3]:
                        context += f"- {result['title']}: {result['snippet'][:100]}...\n"
                    context += "\n"
                
                context += "Provide a helpful summary based on these results. Be concise and actionable."
                
                response = model.generate_content(context)
                results["ai_response"] = response.text
            except Exception as e:
                logger.error(f"AI summary error: {e}")
                results["ai_response"] = "Search completed successfully. Check the results above."
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Web search endpoint error: {str(e)}")
        return jsonify({"error": "Search failed"}), 500


@app.route('/api/products/search', methods=['GET'])
def search_products():
    """Search products by text query"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        max_price = request.args.get('max_price', type=float)
        
        # Load mock products
        mock_products = get_mock_products()
        
        # Filter products based on query
        filtered_products = []
        for product in mock_products:
            if query.lower() in product['name'].lower() or query.lower() in product['description'].lower():
                if category and category.lower() != product['category'].lower():
                    continue
                if max_price and product['price'] > max_price:
                    continue
                filtered_products.append(product)
        
        return jsonify({
            "products": filtered_products[:10],  # Limit to 10 results
            "total_count": len(filtered_products),
            "query": query,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Product search error: {str(e)}")
        return jsonify({"error": "Product search failed"}), 500

@app.route('/api/products/image-search', methods=['POST'])
def image_search():
    """Search products by uploaded image using CLIP"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        
        # For now, return mock response (will integrate CLIP later)
        mock_products = get_mock_products()
        # Return electronics products as mock image recognition result
        electronics_products = [p for p in mock_products if p['category'] == 'Electronics'][:5]
        
        return jsonify({
            "products": electronics_products,
            "confidence": 0.87,
            "recognized_category": "Electronics",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Image search error: {str(e)}")
        return jsonify({"error": "Image search failed"}), 500

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get current cart items"""
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return jsonify({
        "items": cart_items,
        "total_price": total_price,
        "item_count": len(cart_items),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Find product in mock data
        mock_products = get_mock_products()
        product = next((p for p in mock_products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Check if item already in cart
        existing_item = next((item for item in cart_items if item['id'] == product_id), None)
        
        if existing_item:
            existing_item['quantity'] += quantity
        else:
            cart_items.append({
                "id": product['id'],
                "name": product['name'],
                "price": product['price'],
                "image_url": product['image_url'],
                "quantity": quantity,
                "added_at": datetime.now().isoformat()
            })
        
        return jsonify({
            "message": f"Added {product['name']} to cart",
            "cart_items": len(cart_items),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Add to cart error: {str(e)}")
        return jsonify({"error": "Failed to add to cart"}), 500

@app.route('/api/cart/update', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Find and update cart item
        existing_item = next((item for item in cart_items if item['id'] == product_id), None)
        
        if existing_item:
            existing_item['quantity'] = quantity
            return jsonify({
                "message": "Cart updated successfully",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Item not found in cart"}), 404
    
    except Exception as e:
        logger.error(f"Update cart error: {str(e)}")
        return jsonify({"error": "Failed to update cart"}), 500

@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        global cart_items
        cart_items = [item for item in cart_items if item['id'] != product_id]
        
        return jsonify({
            "message": "Item removed from cart",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Remove from cart error: {str(e)}")
        return jsonify({"error": "Failed to remove from cart"}), 500

@app.route('/api/cart/clear', methods=['POST'])
def clear_cart():
    """Clear all cart items"""
    try:
        global cart_items
        cart_items = []
        
        return jsonify({
            "message": "Cart cleared successfully",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Clear cart error: {str(e)}")
        return jsonify({"error": "Failed to clear cart"}), 500

@app.route('/api/products/recommendations', methods=['GET'])
def get_recommendations():
    """Get product recommendations based on cart or search history"""
    try:
        # Simple recommendation logic - return popular products
        mock_products = get_mock_products()
        recommended = sorted(mock_products, key=lambda x: x.get('rating', 0), reverse=True)[:6]
        
        return jsonify({
            "products": recommended,
            "type": "popular",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Recommendations error: {str(e)}")
        return jsonify({"error": "Failed to get recommendations"}), 500

def get_mock_products():
    """Return mock product catalog"""
    return [
        {
            "id": "prod_001",
            "name": "Sony WH-CH720N Wireless Headphones",
            "price": 2999,
            "category": "Electronics",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300",
            "description": "Premium wireless noise-canceling headphones with 35-hour battery life",
            "tags": ["bluetooth", "wireless", "noise-canceling"],
            "stock": 50,
            "rating": 4.5
        },
        {
            "id": "prod_002", 
            "name": "Nike Air Max 270",
            "price": 8995,
            "category": "Footwear",
            "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300",
            "description": "Comfortable running shoes with Air Max technology",
            "tags": ["running", "sports", "comfortable"],
            "stock": 30,
            "rating": 4.3
        },
        {
            "id": "prod_003",
            "name": "Apple iPhone 15",
            "price": 79999,
            "category": "Electronics", 
            "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300",
            "description": "Latest iPhone with advanced camera system and A17 chip",
            "tags": ["smartphone", "apple", "camera"],
            "stock": 25,
            "rating": 4.8
        },
        {
            "id": "prod_004",
            "name": "Instant Pasta - Maggi",
            "price": 15,
            "category": "Groceries",
            "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc1ece3b1?w=300", 
            "description": "Quick 2-minute pasta with masala flavor",
            "tags": ["instant", "pasta", "quick-meal"],
            "stock": 100,
            "rating": 4.1
        },
        {
            "id": "prod_005",
            "name": "Wireless Gaming Mouse",
            "price": 1999,
            "category": "Electronics",
            "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300",
            "description": "High-precision wireless gaming mouse with RGB lighting",
            "tags": ["gaming", "wireless", "precision"],
            "stock": 40,
            "rating": 4.4
        },
        {
            "id": "prod_006",
            "name": "Cotton T-Shirt",
            "price": 599,
            "category": "Clothing",
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300",
            "description": "100% cotton comfortable t-shirt in various colors",
            "tags": ["cotton", "comfortable", "casual"],
            "stock": 75,
            "rating": 4.2
        }
    ]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 