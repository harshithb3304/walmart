# Product Requirements Document (PRD)
## AI Shopping Agent - Hackathon Project

### 🎯 Executive Summary

**Project**: Voice-enabled AI Shopping Agent with Visual Recognition
**Timeline**: Hackathon (48-72 hours)
**Tech Stack**: NextJS Frontend + Flask Backend + Hugging Face Models
**Core Challenge**: Build intelligent shopping experience WITHOUT Walmart catalog API access in India

---

### 🚫 Key Constraints
- **NO Walmart API access in India**
- **NO real e-commerce catalog APIs**
- **Limited hackathon timeline (2-3 days)**
- **Must use mock/scraped data**

---

### 🤖 AI Agent Features

#### 1. **Voice Interaction (Bidirectional)**
- **Speech-to-Text (STT)**: User speaks product requests
- **Text-to-Speech (TTS)**: Agent responds with voice
- **Natural conversation flow**
- **Voice commands for cart actions**

#### 2. **Visual Product Recognition**
- **Image input**: User uploads product images
- **Product identification**: AI identifies what the product is
- **Similar product recommendations**
- **Visual search capabilities**

#### 3. **Intelligent Product Discovery**
- **Natural language search**: "Find me wireless headphones under $100"
- **Related product suggestions**
- **Category-based recommendations**

#### 4. **Auto Cart Management**
- **Voice-activated adding**: "Add this to my cart"
- **Smart quantity suggestions**
- **Cart optimization recommendations**

---

### 🔧 Technical Architecture

#### Frontend (NextJS)
```
/components
  ├── VoiceInterface/
  │   ├── SpeechInput.jsx
  │   ├── VoiceOutput.jsx
  │   └── ConversationHistory.jsx
  ├── ProductSearch/
  │   ├── ImageUpload.jsx
  │   ├── SearchResults.jsx
  │   └── ProductCard.jsx
  ├── Cart/
  │   ├── CartManager.jsx
  │   └── AutoSuggestions.jsx
  └── Layout/
      ├── Header.jsx
      └── MainLayout.jsx

/pages
  ├── index.js (Main AI Agent Interface)
  ├── products/[id].js
  └── cart.js

/hooks
  ├── useVoiceRecognition.js
  ├── useSpeechSynthesis.js
  └── useImageUpload.js
```

#### Backend (Flask)
```
/app
  ├── routes/
  │   ├── voice_api.py
  │   ├── image_api.py
  │   ├── products_api.py
  │   └── cart_api.py
  ├── models/
  │   ├── voice_handler.py
  │   ├── image_processor.py
  │   └── product_matcher.py
  ├── services/
  │   ├── web_scraper.py
  │   ├── mock_data_generator.py
  │   └── ai_orchestrator.py
  └── data/
      ├── mock_products.json
      └── scraped_catalog.json
```

---

### 🧠 AI Models Strategy (Hugging Face)

#### 1. **Speech-to-Text (STT)**
```python
# Primary: OpenAI Whisper
model: "openai/whisper-large-v3"
# Backup: Wav2Vec2
model: "facebook/wav2vec2-large-960h-lv60-self"

# Implementation
from transformers import WhisperProcessor, WhisperForConditionalGeneration
processor = WhisperProcessor.from_pretrained("openai/whisper-large-v3")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large-v3")
```

#### 2. **Text-to-Speech (TTS)**
```python
# Primary: Microsoft SpeechT5
model: "microsoft/speecht5_tts"
# Alternative: Bark (more natural but slower)
model: "suno/bark"

# Implementation
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
```

#### 3. **Conversational AI**
```python
# Primary: Llama 3.1 (8B for local deployment)
model: "meta-llama/Meta-Llama-3.1-8B-Instruct"
# Alternative: Mistral 7B
model: "mistralai/Mistral-7B-Instruct-v0.3"

# Implementation
from transformers import LlamaTokenizer, LlamaForCausalLM
tokenizer = LlamaTokenizer.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")
model = LlamaForCausalLM.from_pretrained("meta-llama/Meta-Llama-3.1-8B-Instruct")
```

#### 4. **Image Recognition & Product Matching**
```python
# Primary: CLIP for general image understanding
model: "openai/clip-vit-large-patch14"
# Product-specific: BlipForConditionalGeneration
model: "Salesforce/blip-image-captioning-large"

# Implementation
from transformers import CLIPProcessor, CLIPModel
processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
```

---

### 📊 Data Strategy (NO API Access)

#### 1. **Web Scraping Approach**
```python
# Target sites for product data
SCRAPING_TARGETS = [
    "https://www.amazon.in/",
    "https://www.flipkart.com/",
    "https://www.myntra.com/",
    "https://www.bigbasket.com/"
]

# Scraping strategy
- Use Selenium + BeautifulSoup
- Rotate user agents and proxies
- Implement rate limiting
- Store in local JSON/SQLite
- Focus on: name, price, image, category, description
```

#### 2. **Mock Data Generation**
```python
# Generate realistic product catalog
PRODUCT_CATEGORIES = [
    "Electronics", "Clothing", "Groceries", 
    "Home & Kitchen", "Books", "Sports"
]

# Mock data structure
{
    "id": "prod_001",
    "name": "Wireless Bluetooth Headphones",
    "price": 2999,
    "category": "Electronics",
    "image_url": "https://example.com/headphones.jpg",
    "description": "Premium quality wireless headphones...",
    "tags": ["bluetooth", "wireless", "audio", "music"],
    "stock": 50,
    "rating": 4.5
}
```

#### 3. **Hybrid Approach**
- **Base catalog**: 500-1000 mock products across categories
- **Real-time enhancement**: Scrape specific products when user searches
- **Image matching**: Use scraped product images for visual search
- **Fallback**: Always have mock alternatives when scraping fails

---

### 🏗️ Implementation Roadmap

#### **Day 1: Foundation (8-10 hours)**
1. **Setup & Architecture** (2 hours)
   - NextJS project initialization
   - Flask backend setup
   - Basic project structure

2. **Mock Data Creation** (2 hours)
   - Generate product catalog JSON
   - Create product images dataset
   - Setup basic API endpoints

3. **Voice Integration** (4 hours)
   - Implement Whisper STT
   - Setup SpeechT5 TTS
   - Basic voice UI components

#### **Day 2: AI Features (8-10 hours)**
1. **Image Recognition** (3 hours)
   - CLIP model integration
   - Image upload and processing
   - Product matching algorithm

2. **Conversational AI** (3 hours)
   - Llama/Mistral integration
   - Context management
   - Natural language processing

3. **Web Scraping** (2 hours)
   - Amazon/Flipkart scrapers
   - Data normalization
   - Real-time product enrichment

#### **Day 3: Integration & Polish (6-8 hours)**
1. **Auto Cart Features** (2 hours)
   - Voice-activated cart management
   - Smart recommendations
   - Cart optimization

2. **UI/UX Polish** (2 hours)
   - Responsive design
   - Voice indicators
   - Loading states

3. **Testing & Demo Prep** (2 hours)
   - End-to-end testing
   - Demo scenarios
   - Bug fixes

---

### 🎬 Demo Scenarios

#### **Scenario 1: Voice Shopping**
```
User: "Hey, I need wireless headphones under 3000 rupees"
Agent: "I found 5 wireless headphones under ₹3000. The top rated is Sony WH-CH720N at ₹2,999. Would you like me to add it to your cart?"
User: "Yes, add it"
Agent: "Added Sony WH-CH720N to your cart. Would you like to see similar products or checkout?"
```

#### **Scenario 2: Image Search**
```
User: [Uploads image of Nike shoes]
Agent: "I can see you're looking for Nike running shoes. I found similar products: Nike Air Max 270 at ₹8,995 and Nike Revolution 6 at ₹4,995. Which one interests you?"
User: "Add the cheaper one to cart"
Agent: "Added Nike Revolution 6 to your cart for ₹4,995."
```

#### **Scenario 3: Smart Recommendations**
```
User: "I'm buying ingredients for pasta"
Agent: "Great! I've found pasta, tomato sauce, and cheese. Based on popular combinations, customers also buy garlic bread and oregano. Should I add those too?"
User: "Yes, add everything"
Agent: "Perfect! Added complete pasta meal kit to your cart - total ₹850."
```

---

### 🚀 Success Metrics

#### **Technical Metrics**
- **Voice Recognition Accuracy**: >85%
- **Image Recognition Success**: >80%
- **Response Time**: <3 seconds per interaction
- **System Uptime**: >95% during demo

#### **User Experience Metrics**
- **Conversation Flow**: Natural, contextual responses
- **Cart Conversion**: >70% of searched items added to cart
- **Multi-modal Usage**: Users successfully combine voice + image
- **Demo Impact**: Clear value proposition demonstration

#### **Innovation Metrics**
- **Feature Completeness**: All 5 core features working
- **AI Integration**: Seamless model orchestration
- **Fallback Handling**: Graceful degradation when APIs fail
- **Scalability**: Code ready for real API integration

---

### 🔧 Quick Start Commands

```bash
# Frontend setup
npx create-next-app@latest walmart-ai-agent
cd walmart-ai-agent
npm install axios socket.io-client

# Backend setup
mkdir flask-backend && cd flask-backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install flask transformers torch soundfile opencv-python requests beautifulsoup4 selenium

# Model downloads (run first time)
python -c "
from transformers import WhisperProcessor, WhisperForConditionalGeneration
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech
from transformers import CLIPProcessor, CLIPModel

# Download models (this will take time)
WhisperProcessor.from_pretrained('openai/whisper-large-v3')
SpeechT5Processor.from_pretrained('microsoft/speecht5_tts')
CLIPProcessor.from_pretrained('openai/clip-vit-large-patch14')
print('Models downloaded successfully!')
"
```

---

### 💡 Hackathon Strategy

#### **Win Factors**
1. **Complete Voice Integration**: Both STT and TTS working smoothly
2. **Visual Search Demo**: Upload image → find products → add to cart
3. **Natural Conversations**: AI understands context and responds naturally
4. **Technical Innovation**: Creative solution to API constraints
5. **Real-world Applicability**: Clear path from hack to production

#### **Risk Mitigation**
- **Model Fallbacks**: Multiple options for each AI component
- **Data Redundancy**: Mock data + scraping + hardcoded examples
- **Simple UI**: Focus on functionality over complex design
- **Incremental Development**: Core features first, enhancements later

#### **Presentation Points**
- **Problem Solved**: Shopping made conversational and intuitive
- **Technical Challenge**: No APIs → Creative data solutions
- **AI Innovation**: Multi-modal AI agent (voice + vision + text)
- **Market Potential**: Applicable to any e-commerce platform
- **Future Roadmap**: Clear scaling strategy

---

**Ready to start building? 🚀** 