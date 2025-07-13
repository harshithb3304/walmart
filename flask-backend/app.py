from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import random
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
        model = genai.GenerativeModel('gemini-2.0-flash')
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
    """Enhanced conversational AI shopping assistant"""
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

        # Generate intelligent conversational response
        ai_response, matched_products, related_products, extra_data = generate_conversational_response(user_message)

        # Add assistant response to history
        conversation_history.append({
            "role": "assistant",
            "message": ai_response,
            "timestamp": datetime.now().isoformat()
        })

        # Prepare response with structured data for frontend
        response_data = {
            "response": ai_response,
            "conversation_history": conversation_history[-10:],
            "cart_items": cart_items,
            "timestamp": datetime.now().isoformat()
        }

        # Add extra structured data if available (for cart updates, special displays)
        if extra_data and isinstance(extra_data, dict):
            response_data.update(extra_data)
        
        # Ensure products are displayed properly in frontend table
        if matched_products:
            # Clean product data for display - match the format expected by frontend
            display_products = []
            for p in matched_products[:8]:
                display_product = {
                    "id": p['id'],
                    "name": p['name'],
                    "price": p['price'],
                    "image_url": p['image_url'],
                    "category": p['category'],
                    "rating": p.get('rating', 4.0),
                    "description": p.get('description', ''),
                    "stock": p.get('stock', 0),
                    "tags": p.get('tags', []),
                    "relevance_score": p.get('relevance_score', 0.5)
                }
                display_products.append(display_product)
            
            # Use the same field names as the search endpoint
            response_data["products"] = display_products  # Main field for products display
            response_data["recommended_products"] = display_products  # Backup for compatibility
            response_data["related_products"] = related_products[:4] if related_products else []
            response_data["total_count"] = len(matched_products)
            
        else:
            # When no products found
            response_data["products"] = []
            response_data["recommended_products"] = []
            response_data["related_products"] = []
            response_data["total_count"] = 0
            
        # Log for debugging
        logger.info(f"Returning {len(response_data.get('products', []))} products for query: {user_message}")

        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({"error": "Chat processing failed"}), 500


def generate_conversational_response(user_message):
    """Generate intelligent conversational response with context awareness"""
    user_msg_lower = user_message.lower().strip()
    mock_products = get_mock_products()
    
    # Analyze user intent
    intent = analyze_user_intent(user_message)
    
    # Handle different conversation flows
    if intent['type'] == 'greeting':
        return handle_greeting(intent)
    elif intent['type'] == 'product_search':
        return handle_product_search(user_message, intent, mock_products)
    elif intent['type'] == 'add_to_cart':
        return handle_add_to_cart(user_message, intent, mock_products)
    elif intent['type'] == 'cart_view':
        return handle_cart_view(intent)
    elif intent['type'] == 'product_details':
        return handle_product_details(user_message, intent, mock_products)
    elif intent['type'] == 'recommendations':
        return handle_recommendations(intent, mock_products)
    elif intent['type'] == 'price_inquiry':
        return handle_price_inquiry(user_message, intent, mock_products)
    elif intent['type'] == 'compare':
        return handle_product_comparison(user_message, intent, mock_products)
    else:
        return handle_general_query(user_message, mock_products)


def analyze_user_intent(user_message):
    """Analyze user intent from message"""
    user_msg_lower = user_message.lower().strip()
    
    # Intent patterns
    intent_patterns = {
        'greeting': ['hi', 'hello', 'hey', 'good morning', 'good evening', 'good afternoon'],
        'add_to_cart': ['add to cart', 'buy', 'purchase', 'order', 'add this', 'take this'],
        'cart_view': ['my cart', 'cart', 'what\'s in cart', 'show cart', 'view cart'],
        'product_details': ['tell me more', 'details', 'specifications', 'features', 'info about'],
        'recommendations': ['recommend', 'suggest', 'what should i', 'best for', 'top rated'],
        'price_inquiry': ['price', 'cost', 'how much', 'budget', 'under', 'below'],
        'compare': ['compare', 'difference', 'vs', 'better than', 'which is best'],
        'product_search': ['show me', 'find', 'search', 'looking for', 'need', 'want', 'get me']
    }
    
    # Detect intent
    for intent_type, patterns in intent_patterns.items():
        if any(pattern in user_msg_lower for pattern in patterns):
            return {
                'type': intent_type,
                'confidence': 0.8,
                'entities': extract_entities(user_message)
            }
    
    # Default to product search if no specific intent
    return {
        'type': 'product_search',
        'confidence': 0.6,
        'entities': extract_entities(user_message)
    }


def extract_entities(user_message):
    """Extract entities like product names, categories, price ranges"""
    user_msg_lower = user_message.lower()
    entities = {}
    
    # Extract categories
    category_keywords = {
        "Electronics": ["phone", "smartphone", "mobile", "laptop", "computer", "headphones", "earphones", "speaker", "camera", "watch"],
        "Footwear": ["shoes", "sneakers", "running", "sports", "formal", "casual"],
        "Clothing": ["shirt", "t-shirt", "jeans", "pants", "dress", "kurta", "polo", "clothing"],
        "Home & Kitchen": ["air fryer", "fryer", "pan", "cookware", "kitchen", "appliance", "bulb", "fan"],
        "Beauty & Personal Care": ["face wash", "shampoo", "lipstick", "skincare", "cosmetics", "razor"],
        "Sports & Fitness": ["sports", "fitness", "gym", "yoga", "cricket", "football", "badminton", "dumbbells"],
        "Books & Stationery": ["book", "notebook", "pen", "pencil", "stationery", "novel"],
        "Toys & Baby Products": ["baby", "kids", "toys", "diapers", "children", "lego", "doll"],
        "Groceries": ["groceries", "food", "salt", "atta", "butter", "milk"]
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in user_msg_lower for keyword in keywords):
            entities['category'] = category
            break
    
    # Extract price range
    import re
    price_patterns = [
        r'under (\d+)',
        r'below (\d+)',
        r'less than (\d+)',
        r'(\d+) to (\d+)',
        r'between (\d+) and (\d+)'
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, user_msg_lower)
        if match:
            if len(match.groups()) == 1:
                entities['max_price'] = int(match.group(1))
            else:
                entities['min_price'] = int(match.group(1))
                entities['max_price'] = int(match.group(2))
            break
    
    # Extract brand names
    brands = ["nike", "adidas", "apple", "samsung", "sony", "dell", "hp", "lenovo", "philips", "bajaj"]
    for brand in brands:
        if brand in user_msg_lower:
            entities['brand'] = brand.title()
            break
    
    return entities


def handle_greeting(intent):
    """Handle greeting messages"""
    responses = [
        "Hello! 👋 I'm your AI Shopping Assistant. I'm here to help you find the perfect products!",
        "Hi there! 🛍️ Welcome to our store! What can I help you discover today?",
        "Hey! 😊 Ready to find some amazing deals? What are you looking for?"
    ]
    
    import random
    response = random.choice(responses)
    response += "\n\n💡 **I can help you with:**\n"
    response += "• Finding products by category or name\n"
    response += "• Comparing prices and features\n"
    response += "• Adding items to your cart\n"
    response += "• Personalized recommendations\n"
    response += "• Answering questions about products\n\n"
    response += "🔍 **Try asking me:**\n"
    response += "• 'Show me wireless headphones under ₹5000'\n"
    response += "• 'I need a laptop for work'\n"
    response += "• 'What's the best smartphone?'\n"
    response += "• 'Recommend some kitchen appliances'"
    
    return response, [], [], None


def handle_product_search(user_message, intent, mock_products):
    """Handle product search with AI-powered intelligent matching"""
    if model:
        # Use Gemini AI for intelligent product filtering
        matched_products = ai_powered_product_search(user_message, mock_products)
    else:
        # Fallback to basic search if AI not available
        entities = intent['entities']
        matched_products = []
        
        for product in mock_products:
            score = calculate_product_relevance(user_message, product, entities)
            if score > 0.3:
                product['relevance_score'] = score
                matched_products.append(product)
        
        matched_products.sort(key=lambda x: (x['relevance_score'], x['rating']), reverse=True)
    
    if matched_products:
        response = create_ai_product_response(user_message, matched_products)
        related_products = get_related_products(matched_products[:3], mock_products)
        
        # Return structured data for frontend display
        display_data = {
            "action": "product_search",
            "search_query": user_message,
            "total_results": len(matched_products),
            "categories_found": list(set(p['category'] for p in matched_products))
        }
        
        return response, matched_products, related_products, display_data
    else:
        return handle_no_products_found(user_message, mock_products)


def ai_powered_product_search(user_message, mock_products):
    """Use Gemini AI to intelligently filter products based on user intent"""
    try:
        # Create a simplified prompt for Gemini
        product_list = []
        for product in mock_products:
            product_list.append({
                'id': product['id'],
                'name': product['name'],
                'category': product['category'],
                'price': product['price'],
                'description': product['description'][:100],  # Truncate description
                'rating': product['rating'],
                'tags': product.get('tags', [])
            })
        
        prompt = f"""
You are an expert product search AI. A customer searched for: "{user_message}"

Product catalog: {str(product_list)}

Task: Return only the product IDs that are highly relevant to the search query.
- For "phone", "mobile", "smartphone" queries, return phones/smartphones only
- For "laptop" queries, only return laptops  
- For "headphones" queries, only return headphones
- Be strict about relevance but include all relevant products

Return format: ["prod_002", "prod_004"] (JSON array of product IDs only)
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        logger.info(f"AI response for '{user_message}': {response_text}")
        
        # Parse response
        import json
        try:
            if '[' in response_text and ']' in response_text:
                start = response_text.find('[')
                end = response_text.rfind(']') + 1
                json_str = response_text[start:end]
                selected_ids = json.loads(json_str)
            else:
                selected_ids = []
            
            logger.info(f"Selected product IDs: {selected_ids}")
            
            # Get matching products
            matched_products = []
            for product_id in selected_ids:
                for product in mock_products:
                    if product['id'] == product_id:
                        product_copy = product.copy()
                        product_copy['relevance_score'] = 1.0 - (selected_ids.index(product_id) * 0.1)
                        matched_products.append(product_copy)
                        break
            
            logger.info(f"Found {len(matched_products)} matching products")
            return matched_products
            
        except Exception as parse_error:
            logger.error(f"Failed to parse AI response: {parse_error}")
            return basic_product_search(user_message, mock_products)
            
    except Exception as e:
        logger.error(f"AI search error: {e}")
        return basic_product_search(user_message, mock_products)


def basic_product_search(user_message, mock_products):
    """Fallback search when AI fails"""
    user_lower = user_message.lower()
    matched = []
    
    # Define search keywords for better matching
    phone_keywords = ['phone', 'mobile', 'smartphone', 'iphone', 'galaxy', 'samsung', 'apple']
    laptop_keywords = ['laptop', 'computer', 'notebook', 'dell', 'hp', 'macbook']
    headphone_keywords = ['headphone', 'earphone', 'airpod', 'headset', 'earbuds']
    
    for product in mock_products:
        score = 0.0
        product_text = f"{product['name']} {product['description']} {product['category']} {' '.join(product.get('tags', []))}".lower()
        
        # Phone/mobile search
        if any(keyword in user_lower for keyword in phone_keywords):
            if any(keyword in product_text for keyword in phone_keywords) or 'electronics' in product['category'].lower():
                if any(phone_word in product_text for phone_word in ['iphone', 'galaxy', 'smartphone', 'mobile']):
                    score += 1.0
        
        # Laptop search  
        elif any(keyword in user_lower for keyword in laptop_keywords):
            if any(keyword in product_text for keyword in laptop_keywords):
                score += 1.0
                
        # Headphone search
        elif any(keyword in user_lower for keyword in headphone_keywords):
            if any(keyword in product_text for keyword in headphone_keywords):
                score += 1.0
        
        # General keyword matching
        else:
            for word in user_lower.split():
                if len(word) > 2 and word in product_text:
                    score += 0.4
        
        # Category matching bonus
        if any(word in product['category'].lower() for word in user_lower.split()):
            score += 0.3
            
        if score > 0.3:
            product_copy = product.copy()
            product_copy['relevance_score'] = min(score, 1.0)
            matched.append(product_copy)
    
    logger.info(f"Basic search found {len(matched)} products for '{user_message}'")
    return sorted(matched, key=lambda x: x['relevance_score'], reverse=True)[:10]


def create_ai_product_response(user_message, products):
    """Create conversational response for products with structured data for frontend"""
    if not products:
        return "I couldn't find any products matching your search. Could you try being more specific?"
    
    response = f"🎯 **Found {len(products)} great matches for '{user_message}'!**\n\n"
    
    for i, product in enumerate(products[:6]):
        emoji = get_category_emoji(product['category'])
        discount_price = int(product['price'] * 1.15)  # Show original higher price
        savings = discount_price - product['price']
        
        response += f"{emoji} **{product['name']}**\n"
        response += f"   💰 ₹{product['price']:,} ~~₹{discount_price:,}~~ (Save ₹{savings:,}!)\n"
        response += f"   ⭐ {product['rating']}/5 | 📦 {product['stock']} in stock\n"
        response += f"   📝 {product['description'][:80]}...\n\n"
    
    response += "💬 **What next?**\n"
    response += "• Say 'add [product name] to cart' to buy\n"
    response += "• Ask 'tell me more about [product]' for details\n"
    response += "• Try 'show me similar products' for alternatives\n\n"
    
    return response


def get_category_emoji(category):
    """Get emoji for product category"""
    emoji_map = {
        "Electronics": "📱",
        "Footwear": "👟", 
        "Clothing": "👕",
        "Home & Kitchen": "🏠",
        "Beauty & Personal Care": "💄",
        "Sports & Fitness": "⚽",
        "Books & Stationery": "📚",
        "Toys & Baby Products": "🧸",
        "Groceries": "🛒"
    }
    return emoji_map.get(category, "🛍️")


def calculate_product_relevance(user_message, product, entities):
    """Calculate how relevant a product is to user query"""
    score = 0.0
    user_words = user_message.lower().split()
    product_text = f"{product['name']} {product['description']} {' '.join(product.get('tags', []))}"
    
    # Keyword matching
    for word in user_words:
        if len(word) > 2 and word in product_text.lower():
            score += 0.2
    
    # Category matching
    if 'category' in entities and entities['category'].lower() == product['category'].lower():
        score += 0.4
    
    # Price range matching
    if 'max_price' in entities and product['price'] <= entities['max_price']:
        score += 0.3
    if 'min_price' in entities and product['price'] >= entities['min_price']:
        score += 0.2
    
    # Brand matching
    if 'brand' in entities and entities['brand'].lower() in product['name'].lower():
        score += 0.5
    
    # Rating boost
    score += product['rating'] * 0.1
    
    return min(score, 1.0)


def create_product_search_response(user_message, products, entities):
    """Create structured response for product search"""
    response = f"🛍️ **Found {len(products)} products for '{user_message}'**\n\n"
    
    # Add filter information
    if entities:
        response += "📋 **Applied Filters:**\n"
        if 'category' in entities:
            response += f"• Category: {entities['category']}\n"
        if 'max_price' in entities:
            response += f"• Max Price: ₹{entities['max_price']}\n"
        if 'brand' in entities:
            response += f"• Brand: {entities['brand']}\n"
        response += "\n"
    
    # Group by category for better presentation
    categories = {}
    for product in products[:8]:  # Show top 8 products
        category = product['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(product)
    
    # Display products by category
    for category, category_products in categories.items():
        response += f"📂 **{category}**\n"
        for i, p in enumerate(category_products, 1):
            response += f"   {i}. **{p['name']}** - ₹{p['price']:,}\n"
            response += f"      💭 {p['description'][:100]}{'...' if len(p['description']) > 100 else ''}\n"
            response += f"      ⭐ {p['rating']}/5 stars | 📦 {p['stock']} in stock\n"
            
            # Add special tags
            if p['rating'] >= 4.5:
                response += f"      🏆 **Top Rated**\n"
            if p['stock'] < 20:
                response += f"      🔥 **Limited Stock**\n"
            
            response += f"      🏷️ ID: {p['id']}\n\n"
    
    if len(products) > 8:
        response += f"➕ **{len(products) - 8} more products available!**\n\n"
    
    response += "🎯 **Quick Actions:**\n"
    response += "• Say 'add [product name] to cart' to purchase\n"
    response += "• Ask 'tell me more about [product]' for details\n"
    response += "• Try 'compare [product1] vs [product2]'\n"
    response += "• Say 'show me cheaper alternatives'"
    
    return response


def handle_add_to_cart(user_message, intent, mock_products):
    """Handle adding products to cart with smart recommendations"""
    # Find the product to add
    product_to_add = identify_product_from_message(user_message, mock_products)
    
    if not product_to_add:
        return "❌ **Product not found!**\n\nPlease specify which product you'd like to add. You can use the product name or ID.\n\n💡 **Example:** 'Add Sony headphones to cart'", [], [], None
    
    # Use the actual cart API endpoint to add item
    try:
        # Simulate API call to add to cart (since we're in the same app, we can call the function directly)
        existing_item = next((item for item in cart_items if item['id'] == product_to_add['id']), None)
        
        if existing_item:
            existing_item['quantity'] += 1
            cart_action = "updated"
            quantity_text = f"Quantity increased to {existing_item['quantity']}"
        else:
            cart_items.append({
                "id": product_to_add['id'],
                "name": product_to_add['name'],
                "price": product_to_add['price'],
                "image_url": product_to_add['image_url'],
                "category": product_to_add['category'],
                "quantity": 1,
                "added_at": datetime.now().isoformat()
            })
            cart_action = "added"
            quantity_text = "Added 1 item"
    
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return "❌ **Failed to add to cart!**\n\nPlease try again or contact support.", [], [], None
    
    # Generate smart recommendations
    recommendations = generate_smart_recommendations(product_to_add, cart_items, mock_products)
    
    # Create response with structured data for frontend
    total_items = sum(item['quantity'] for item in cart_items)
    total_value = sum(item['price'] * item['quantity'] for item in cart_items)
    
    # Text response for chat
    response = f"✅ **{cart_action.title()} to Cart!**\n\n"
    response += f"🛒 **{product_to_add['name']}** - ₹{product_to_add['price']:,}\n"
    response += f"📦 {quantity_text}\n\n"
    response += f"💰 **Cart Summary:**\n"
    response += f"• Total Items: {total_items}\n"
    response += f"• Cart Value: ₹{total_value:,}\n\n"
    
    if recommendations:
        response += "🤖 **Smart Recommendations:**\n"
        response += "Based on your selection, you might also like:\n\n"
        for i, rec in enumerate(recommendations[:3], 1):
            response += f"{i}. **{rec['name']}** - ₹{rec['price']:,}\n"
            response += f"   💭 {rec['reason']}\n"
            response += f"   ⭐ {rec['rating']}/5 stars\n\n"
    
    response += "🎯 **What's Next?**\n"
    response += "• Continue shopping: 'Show me more [category]'\n"
    response += "• View cart: 'Show my cart'\n"
    response += "• Get recommendations: 'What else do I need?'\n"
    response += "• Checkout: 'I'm ready to checkout'"
    
    # Structured data for frontend display
    display_data = {
        "action": "cart_updated",
        "added_product": {
            "id": product_to_add['id'],
            "name": product_to_add['name'],
            "price": product_to_add['price'],
            "image_url": product_to_add['image_url'],
            "category": product_to_add['category'],
            "rating": product_to_add.get('rating', 4.0),
            "description": product_to_add.get('description', '')
        },
        "cart_summary": {
            "total_items": total_items,
            "total_value": total_value,
            "items": cart_items
        },
        "recommendations": [
            {
                "id": rec['id'],
                "name": rec['name'],
                "price": rec['price'],
                "image_url": rec['image_url'],
                "rating": rec['rating'],
                "reason": rec['reason'],
                "category": rec['category']
            } for rec in recommendations[:3]
        ] if recommendations else []
    }
    
    return response, [], recommendations, display_data


def identify_product_from_message(user_message, mock_products):
    """Identify which product user wants to add to cart"""
    user_msg_lower = user_message.lower()
    
    # Check for product ID
    for product in mock_products:
        if product['id'] in user_message:
            return product
    
    # Check for product name words
    best_match = None
    max_score = 0
    
    for product in mock_products:
        score = 0
        product_words = product['name'].lower().split()
        
        # Count matching words
        for word in product_words:
            if word in user_msg_lower:
                score += 1
        
        # Normalize score
        score = score / len(product_words)
        
        if score > max_score and score > 0.3:
            max_score = score
            best_match = product
    
    return best_match


def generate_smart_recommendations(added_product, cart_items, all_products):
    """Generate intelligent product recommendations"""
    recommendations = []
    
    # Get complementary products
    complementary_rules = {
        "Electronics": {
            "phone": ["case", "charger", "headphones", "power bank"],
            "laptop": ["mouse", "keyboard", "bag", "external drive"],
            "headphones": ["case", "cable", "adapter"],
            "camera": ["memory card", "tripod", "case", "lens"]
        },
        "Clothing": {
            "shirt": ["pants", "belt", "tie"],
            "jeans": ["shirt", "belt", "shoes"],
            "kurta": ["bottom", "dupatta"]
        },
        "Footwear": {
            "shoes": ["socks", "shoe care", "insoles"],
            "sneakers": ["sports wear", "socks"]
        },
        "Home & Kitchen": {
            "air fryer": ["oil", "recipes", "accessories"],
            "pan": ["oil", "spices", "utensils"]
        }
    }
    
    category = added_product['category']
    product_name_lower = added_product['name'].lower()
    
    # Find complementary products
    if category in complementary_rules:
        for product_type, complements in complementary_rules[category].items():
            if product_type in product_name_lower:
                for complement in complements:
                    for product in all_products:
                        if (complement in product['name'].lower() or 
                            complement in product['description'].lower()) and \
                           product['id'] != added_product['id']:
                            recommendations.append({
                                **product,
                                'reason': f"Perfect companion for your {added_product['name']}"
                            })
                break
    
    # Add products from same category (different brands/models)
    same_category_products = [p for p in all_products 
                             if p['category'] == category and 
                             p['id'] != added_product['id'] and
                             p['price'] <= added_product['price'] * 1.5]
    
    for product in same_category_products[:2]:
        recommendations.append({
            **product,
            'reason': f"Another great {category.lower()} option"
        })
    
    # Add frequently bought together (based on cart history)
    cart_categories = set(item['category'] for item in cart_items)
    if len(cart_categories) >= 2:
        cross_category_products = [p for p in all_products 
                                 if p['category'] not in cart_categories and 
                                 p['rating'] >= 4.0]
        
        if cross_category_products:
            recommendations.append({
                **cross_category_products[0],
                'reason': "Customers who bought similar items also purchased this"
            })
    
    # Remove duplicates and limit
    seen_ids = set()
    unique_recommendations = []
    for rec in recommendations:
        if rec['id'] not in seen_ids:
            seen_ids.add(rec['id'])
            unique_recommendations.append(rec)
    
    return unique_recommendations[:5]


def handle_cart_view(intent):
    """Handle cart viewing requests"""
    if not cart_items:
        return "🛒 **Your Cart is Empty**\n\nReady to start shopping? I can help you find:\n• Electronics & Gadgets\n• Clothing & Footwear\n• Home & Kitchen Items\n• Sports & Fitness\n• Books & Stationery\n\n💡 **Just tell me what you're looking for!**", [], [], None
    
    total_value = sum(item['price'] * item['quantity'] for item in cart_items)
    total_items = sum(item['quantity'] for item in cart_items)
    
    response = f"🛒 **Your Shopping Cart** ({total_items} items)\n\n"
    
    # Group by category
    categories = {}
    for item in cart_items:
        category = item.get('category', 'Other')
        if category not in categories:
            categories[category] = []
        categories[category].append(item)
    
    for category, items in categories.items():
        response += f"📂 **{category}**\n"
        for item in items:
            response += f"   • **{item['name']}**\n"
            response += f"     ₹{item['price']:,} × {item['quantity']} = ₹{item['price'] * item['quantity']:,}\n"
            response += f"     🏷️ ID: {item['id']}\n\n"
    
    response += f"💰 **Total: ₹{total_value:,}**\n\n"
    response += "🎯 **Quick Actions:**\n"
    response += "• 'Remove [product name]' to delete items\n"
    response += "• 'Update quantity of [product]' to change amounts\n"
    response += "• 'What else do I need?' for recommendations\n"
    response += "• 'Checkout' to proceed with payment\n"
    response += "• 'Clear cart' to start fresh"
    
    return response, [], [], None


def handle_no_products_found(user_message, mock_products):
    """Handle when no products match the search"""
    # Suggest alternatives
    popular_products = sorted(mock_products, key=lambda x: x['rating'], reverse=True)[:6]
    
    response = f"🔍 **No exact matches found for '{user_message}'**\n\n"
    response += "But don't worry! Here are some popular items you might like:\n\n"
    
    for i, product in enumerate(popular_products, 1):
        response += f"{i}. **{product['name']}** - ₹{product['price']:,}\n"
        response += f"   💭 {product['description'][:80]}{'...' if len(product['description']) > 80 else ''}\n"
        response += f"   ⭐ {product['rating']}/5 stars | 📂 {product['category']}\n\n"
    
    response += "💡 **Try these search tips:**\n"
    response += "• Use broader terms: 'phone' instead of 'iPhone 15 Pro Max'\n"
    response += "• Include category: 'electronics', 'clothing', 'kitchen'\n"
    response += "• Mention your budget: 'headphones under ₹5000'\n"
    response += "• Ask for recommendations: 'What's the best laptop?'"
    
    return response, popular_products, [], None


def handle_general_query(user_message, mock_products):
    """Handle general queries and provide helpful responses"""
    user_msg_lower = user_message.lower()
    
    if any(word in user_msg_lower for word in ['help', 'what can you do', 'how does this work']):
        return handle_help_query()
    elif any(word in user_msg_lower for word in ['popular', 'trending', 'best sellers']):
        return handle_popular_products(mock_products)
    elif any(word in user_msg_lower for word in ['categories', 'what do you sell']):
        return handle_categories_query(mock_products)
    else:
        return handle_fallback_response(user_message, mock_products)


def handle_help_query():
    """Handle help requests"""
    response = "🤖 **I'm your AI Shopping Assistant!**\n\n"
    response += "💡 **What I can do:**\n"
    response += "• 🔍 Find products by name, category, or description\n"
    response += "• 💰 Filter by price range and features\n"
    response += "• 🛒 Add items to your cart\n"
    response += "• 📊 Compare products and features\n"
    response += "• 🎯 Provide personalized recommendations\n"
    response += "• 💬 Answer questions about products\n\n"
    response += "🗣️ **How to talk to me:**\n"
    response += "• 'Show me wireless headphones under ₹3000'\n"
    response += "• 'I need a laptop for gaming'\n"
    response += "• 'Add iPhone to cart'\n"
    response += "• 'What's the difference between these phones?'\n"
    response += "• 'Recommend something for cooking'\n\n"
    response += "🎯 **Ready to shop?** Just tell me what you're looking for!"
    
    return response, [], [], None


def handle_popular_products(mock_products):
    """Show popular/trending products"""
    popular = sorted(mock_products, key=lambda x: x['rating'], reverse=True)[:8]
    
    response = "🔥 **Popular Products Right Now**\n\n"
    
    categories = {}
    for product in popular:
        category = product['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(product)
    
    for category, products in categories.items():
        response += f"📂 **{category}**\n"
        for product in products:
            response += f"   🏆 **{product['name']}** - ₹{product['price']:,}\n"
            response += f"      ⭐ {product['rating']}/5 stars | 📦 {product['stock']} in stock\n\n"
    
    response += "🎯 **Want to add any of these to your cart?**\n"
    response += "Just say 'add [product name] to cart'!"
    
    return response, popular, [], None


def handle_categories_query(mock_products):
    """Show available categories"""
    categories = {}
    for product in mock_products:
        category = product['category']
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    response = "🏪 **Shop by Category**\n\n"
    
    for category, count in sorted(categories.items()):
        response += f"📂 **{category}** ({count} products)\n"
        
        # Show sample products
        sample_products = [p for p in mock_products if p['category'] == category][:2]
        for product in sample_products:
            response += f"   • {product['name']} - ₹{product['price']:,}\n"
        response += "\n"
    
    response += "🎯 **To explore a category, just say:**\n"
    response += "• 'Show me Electronics'\n"
    response += "• 'I need something from Home & Kitchen'\n"
    response += "• 'Browse Clothing options'"
    
    return response, [], [], None


def handle_fallback_response(user_message, mock_products):
    """Fallback response for unrecognized queries"""
    response = "🤔 **I'd love to help you find what you're looking for!**\n\n"
    response += f"You mentioned: '{user_message}'\n\n"
    response += "💡 **Here's how I can assist:**\n"
    response += "• 🔍 **Search products:** 'Show me headphones'\n"
    response += "• 💰 **Set budget:** 'Find phones under ₹20000'\n"
    response += "• 🛒 **Add to cart:** 'Add this laptop to cart'\n"
    response += "• 📊 **Compare:** 'Compare iPhone vs Samsung'\n"
    response += "• 🎯 **Get recommendations:** 'What's best for gaming?'\n\n"
    response += "**Popular searches:**\n"
    response += "• Electronics & Gadgets\n"
    response += "• Clothing & Fashion\n"
    response += "• Home & Kitchen\n"
    response += "• Sports & Fitness\n\n"
    response += "What would you like to explore?"
    
    return response, [], [], None


def get_related_products(base_products, all_products):
    """Get related products based on category and rating"""
    if not base_products:
        return []
    
    base_categories = set(p['category'] for p in base_products)
    related = []
    
    for product in all_products:
        if (product['category'] in base_categories and 
            product not in base_products and 
            product['rating'] >= 4.0):
            related.append(product)
    
    return sorted(related, key=lambda x: x['rating'], reverse=True)[:5]


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
            
    except Exception as e:
        logger.error(f"Enhanced AI response error: {e}")

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
    # Expanded mock product catalog (50+ items)
    return [
        # Electronics
        {"id": "prod_001", "name": "Sony WH-CH720N Wireless Headphones", "price": 2999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300", "description": "Premium wireless noise-canceling headphones with 35-hour battery life", "tags": ["bluetooth", "wireless", "noise-canceling"], "stock": 50, "rating": 4.5},
        {"id": "prod_002", "name": "Apple iPhone 15", "price": 79999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=300", "description": "Latest iPhone with advanced camera system and A17 chip", "tags": ["smartphone", "apple", "camera"], "stock": 25, "rating": 4.8},
        {"id": "prod_003", "name": "Wireless Gaming Mouse", "price": 1999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=300", "description": "High-precision wireless gaming mouse with RGB lighting", "tags": ["gaming", "wireless", "precision"], "stock": 40, "rating": 4.4},
        {"id": "prod_004", "name": "Samsung Galaxy S24 Ultra", "price": 84999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=300", "description": "Flagship Android smartphone with 200MP camera", "tags": ["smartphone", "android", "camera"], "stock": 30, "rating": 4.7},
        {"id": "prod_005", "name": "Dell XPS 13 Laptop", "price": 109999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300", "description": "Ultra-thin laptop with Intel i7 processor", "tags": ["laptop", "dell", "ultrabook"], "stock": 20, "rating": 4.6},
        {"id": "prod_006", "name": "JBL Flip 6 Bluetooth Speaker", "price": 8999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1465101046530-73398c7f28ca?w=300", "description": "Portable waterproof speaker with deep bass", "tags": ["speaker", "bluetooth", "portable"], "stock": 60, "rating": 4.4},
        {"id": "prod_007", "name": "Mi Smart Band 7", "price": 3499, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Fitness tracker with heart rate monitor", "tags": ["fitness", "tracker", "smart"], "stock": 80, "rating": 4.3},
        {"id": "prod_008", "name": "Canon EOS 1500D DSLR Camera", "price": 42999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1519183071298-a2962be56693?w=300", "description": "Entry-level DSLR with 24MP sensor", "tags": ["camera", "dslr", "canon"], "stock": 15, "rating": 4.5},
        {"id": "prod_009", "name": "Amazon Echo Dot (5th Gen)", "price": 4499, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=300", "description": "Smart speaker with Alexa voice assistant", "tags": ["smart", "speaker", "alexa"], "stock": 70, "rating": 4.4},
        {"id": "prod_010", "name": "HP DeskJet 2331 Printer", "price": 3999, "category": "Electronics", "image_url": "https://images.unsplash.com/photo-1519985176271-adb1088fa94c?w=300", "description": "All-in-one color printer for home use", "tags": ["printer", "hp", "color"], "stock": 35, "rating": 4.2},
        # Footwear
        {"id": "prod_011", "name": "Nike Air Max 270", "price": 8995, "category": "Footwear", "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=300", "description": "Comfortable running shoes with Air Max technology", "tags": ["running", "sports", "comfortable"], "stock": 30, "rating": 4.3},
        {"id": "prod_012", "name": "Adidas Ultraboost 22", "price": 12999, "category": "Footwear", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "High-performance running shoes with Boost cushioning", "tags": ["running", "adidas", "boost"], "stock": 25, "rating": 4.6},
        {"id": "prod_013", "name": "Puma Smash v2 Sneakers", "price": 2999, "category": "Footwear", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Classic sneakers for everyday wear", "tags": ["sneakers", "puma", "casual"], "stock": 40, "rating": 4.2},
        {"id": "prod_014", "name": "Skechers Go Walk 5", "price": 4999, "category": "Footwear", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Lightweight walking shoes with memory foam", "tags": ["walking", "skechers", "memory-foam"], "stock": 35, "rating": 4.4},
        {"id": "prod_015", "name": "Bata Formal Leather Shoes", "price": 2599, "category": "Footwear", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Elegant formal shoes for office wear", "tags": ["formal", "leather", "bata"], "stock": 20, "rating": 4.1},
        # Clothing
        {"id": "prod_016", "name": "Cotton T-Shirt", "price": 599, "category": "Clothing", "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300", "description": "100% cotton comfortable t-shirt in various colors", "tags": ["cotton", "comfortable", "casual"], "stock": 75, "rating": 4.2},
        {"id": "prod_017", "name": "Levi's 511 Slim Jeans", "price": 2499, "category": "Clothing", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Slim fit jeans for men", "tags": ["jeans", "levis", "slim-fit"], "stock": 50, "rating": 4.5},
        {"id": "prod_018", "name": "Raymond Formal Shirt", "price": 1299, "category": "Clothing", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Premium formal shirt for office wear", "tags": ["formal", "shirt", "raymond"], "stock": 40, "rating": 4.3},
        {"id": "prod_019", "name": "Allen Solly Polo T-Shirt", "price": 899, "category": "Clothing", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Classic polo t-shirt for men", "tags": ["polo", "allen-solly", "casual"], "stock": 60, "rating": 4.4},
        {"id": "prod_020", "name": "W Women Kurta", "price": 1599, "category": "Clothing", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Elegant kurta for women", "tags": ["kurta", "women", "w"], "stock": 45, "rating": 4.5},
        # Groceries
        {"id": "prod_021", "name": "Instant Pasta - Maggi", "price": 15, "category": "Groceries", "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc1ece3b1?w=300", "description": "Quick 2-minute pasta with masala flavor", "tags": ["instant", "pasta", "quick-meal"], "stock": 100, "rating": 4.1},
        {"id": "prod_022", "name": "Tata Salt", "price": 25, "category": "Groceries", "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300", "description": "Iodized salt for daily use", "tags": ["salt", "tata", "groceries"], "stock": 200, "rating": 4.3},
        {"id": "prod_023", "name": "Aashirvaad Atta 5kg", "price": 299, "category": "Groceries", "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300", "description": "Whole wheat flour for soft rotis", "tags": ["atta", "wheat", "groceries"], "stock": 80, "rating": 4.4},
        {"id": "prod_024", "name": "Amul Butter 500g", "price": 275, "category": "Groceries", "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300", "description": "Fresh and creamy butter", "tags": ["butter", "amul", "dairy"], "stock": 60, "rating": 4.5},
        {"id": "prod_025", "name": "Nestle Everyday Milk Powder", "price": 399, "category": "Groceries", "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=300", "description": "Milk powder for tea and coffee", "tags": ["milk", "powder", "nestle"], "stock": 90, "rating": 4.2},
        # Home & Kitchen
        {"id": "prod_026", "name": "Philips HD9200 Air Fryer", "price": 8999, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Healthy air fryer with rapid air technology, 4L capacity", "tags": ["air-fryer", "philips", "healthy-cooking", "kitchen"], "stock": 25, "rating": 4.6},
        {"id": "prod_027", "name": "Wonderchef Prato Air Fryer", "price": 5999, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Compact air fryer with digital display, 3L capacity", "tags": ["air-fryer", "wonderchef", "compact", "digital"], "stock": 30, "rating": 4.4},
        {"id": "prod_028", "name": "Prestige Non-Stick Fry Pan", "price": 799, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Durable non-stick fry pan for healthy cooking", "tags": ["fry-pan", "prestige", "non-stick"], "stock": 40, "rating": 4.3},
        {"id": "prod_029", "name": "Milton Thermosteel Flask 1L", "price": 699, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Keeps beverages hot or cold for hours", "tags": ["flask", "milton", "thermosteel"], "stock": 35, "rating": 4.4},
        {"id": "prod_030", "name": "Cello Plastic Water Bottle Set", "price": 349, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Set of 6 BPA-free water bottles", "tags": ["water-bottle", "cello", "plastic"], "stock": 50, "rating": 4.2},
        {"id": "prod_031", "name": "Bajaj Majesty Air Fryer", "price": 4999, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Affordable air fryer with 2.5L capacity and preset cooking modes", "tags": ["air-fryer", "bajaj", "affordable", "preset-modes"], "stock": 35, "rating": 4.2},
        {"id": "prod_032", "name": "Philips LED Bulb 9W", "price": 99, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "Energy-saving LED bulb", "tags": ["led", "bulb", "philips"], "stock": 100, "rating": 4.5},
        {"id": "prod_033", "name": "Havells Ceiling Fan", "price": 2499, "category": "Home & Kitchen", "image_url": "https://images.unsplash.com/photo-1519864600265-abb23847ef2c?w=300", "description": "High-speed ceiling fan for cool air", "tags": ["fan", "havells", "ceiling"], "stock": 20, "rating": 4.3},
        # Beauty & Personal Care
        {"id": "prod_034", "name": "Nivea Men Face Wash", "price": 199, "category": "Beauty & Personal Care", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Deep cleansing face wash for men", "tags": ["face-wash", "nivea", "men"], "stock": 60, "rating": 4.2},
        {"id": "prod_035", "name": "Lakme Absolute Lipstick", "price": 499, "category": "Beauty & Personal Care", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Long-lasting matte lipstick", "tags": ["lipstick", "lakme", "beauty"], "stock": 45, "rating": 4.4},
        {"id": "prod_036", "name": "Dove Intense Repair Shampoo", "price": 349, "category": "Beauty & Personal Care", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Shampoo for damaged hair", "tags": ["shampoo", "dove", "hair"], "stock": 70, "rating": 4.3},
        {"id": "prod_037", "name": "Gillette Fusion Razor", "price": 299, "category": "Beauty & Personal Care", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "5-blade razor for smooth shave", "tags": ["razor", "gillette", "shave"], "stock": 55, "rating": 4.5},
        {"id": "prod_038", "name": "Himalaya Neem Face Pack", "price": 199, "category": "Beauty & Personal Care", "image_url": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f?w=300", "description": "Herbal face pack for clear skin", "tags": ["face-pack", "himalaya", "herbal"], "stock": 40, "rating": 4.2},
        # Toys & Baby Products
        {"id": "prod_039", "name": "LEGO Classic Bricks Set", "price": 1499, "category": "Toys & Baby Products", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Creative building blocks for kids", "tags": ["lego", "blocks", "kids"], "stock": 30, "rating": 4.7},
        {"id": "prod_040", "name": "Hot Wheels Car Pack", "price": 499, "category": "Toys & Baby Products", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Set of 5 die-cast cars", "tags": ["hot-wheels", "cars", "toys"], "stock": 50, "rating": 4.5},
        {"id": "prod_041", "name": "Fisher-Price Baby Rattle", "price": 199, "category": "Toys & Baby Products", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Colorful rattle for infants", "tags": ["rattle", "fisher-price", "baby"], "stock": 60, "rating": 4.3},
        {"id": "prod_042", "name": "Barbie Dreamhouse Doll", "price": 2999, "category": "Toys & Baby Products", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Barbie doll with accessories", "tags": ["barbie", "doll", "toys"], "stock": 25, "rating": 4.6},
        {"id": "prod_043", "name": "Mee Mee Baby Diapers", "price": 499, "category": "Toys & Baby Products", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Pack of 40 ultra-soft diapers", "tags": ["diapers", "mee-mee", "baby"], "stock": 80, "rating": 4.4},
        # Books & Stationery
        {"id": "prod_044", "name": "The Alchemist by Paulo Coelho", "price": 299, "category": "Books & Stationery", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Inspirational novel", "tags": ["book", "alchemist", "paulo-coelho"], "stock": 40, "rating": 4.8},
        {"id": "prod_045", "name": "Classmate Spiral Notebook", "price": 79, "category": "Books & Stationery", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "200 pages ruled notebook", "tags": ["notebook", "classmate", "stationery"], "stock": 100, "rating": 4.5},
        {"id": "prod_046", "name": "Faber-Castell Color Pencils", "price": 199, "category": "Books & Stationery", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Pack of 24 color pencils", "tags": ["color-pencils", "faber-castell", "stationery"], "stock": 60, "rating": 4.6},
        {"id": "prod_047", "name": "Camlin Geometry Box", "price": 149, "category": "Books & Stationery", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Complete geometry set for students", "tags": ["geometry-box", "camlin", "stationery"], "stock": 80, "rating": 4.4},
        {"id": "prod_048", "name": "Pilot V5 Hi-Tecpoint Pen", "price": 35, "category": "Books & Stationery", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Smooth writing pen", "tags": ["pen", "pilot", "stationery"], "stock": 120, "rating": 4.3},
        # Sports & Fitness
        {"id": "prod_049", "name": "Yonex GR 303 Badminton Racquet", "price": 599, "category": "Sports & Fitness", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Lightweight racquet for beginners", "tags": ["badminton", "yonex", "sports"], "stock": 30, "rating": 4.5},
        {"id": "prod_050", "name": "Nivia Football Size 5", "price": 499, "category": "Sports & Fitness", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Durable football for outdoor play", "tags": ["football", "nivia", "sports"], "stock": 40, "rating": 4.4},
        {"id": "prod_051", "name": "Cosco Yoga Mat", "price": 799, "category": "Sports & Fitness", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Non-slip yoga mat for workouts", "tags": ["yoga-mat", "cosco", "fitness"], "stock": 50, "rating": 4.6},
        {"id": "prod_052", "name": "SG Cricket Bat", "price": 1499, "category": "Sports & Fitness", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "English willow cricket bat", "tags": ["cricket-bat", "sg", "sports"], "stock": 20, "rating": 4.7},
        {"id": "prod_053", "name": "Decathlon Dumbbell Set 10kg", "price": 1299, "category": "Sports & Fitness", "image_url": "https://images.unsplash.com/photo-1519125323398-675f0ddb6308?w=300", "description": "Set of 2 dumbbells for home workouts", "tags": ["dumbbell", "decathlon", "fitness"], "stock": 25, "rating": 4.5}
    ]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)