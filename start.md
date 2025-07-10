# AI Shopping Agent - Quick Start Guide

## 🚀 Getting Started

### ⚡ Quick Start (Recommended)
```bash
# One-command setup and start
quick-start.bat
```

### Manual Setup

#### Backend Setup (Flask)

1. **Navigate to backend directory:**
   ```bash
   cd flask-backend
   ```

2. **Activate virtual environment:**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux  
   source venv/bin/activate
   ```

3. **Install basic dependencies:**
   ```bash
   pip install -r requirements-basic.txt
   # OR for full AI features: pip install -r requirements.txt
   ```

4. **Start Flask server:**
   ```bash
   python app.py
   ```
   ✅ Backend will run on: http://localhost:5000

### Frontend Setup (NextJS)

1. **Open new terminal and navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Start NextJS development server:**
   ```bash
   npm run dev
   ```
   ✅ Frontend will run on: http://localhost:3000

## 🎯 Features Available

### ✅ **Implemented Features:**
- 🗣️ **Voice Interface**: Speech-to-text using browser Web Speech API
- 🖼️ **Image Upload**: Visual product search with drag & drop
- 💬 **Chat Interface**: Conversational AI with contextual responses
- 🛒 **Shopping Cart**: Add/remove items with real-time updates
- 📱 **Responsive UI**: Clean, modern interface with Tailwind CSS
- 🔍 **Product Search**: Text-based search with filtering
- 📦 **Mock Product Catalog**: 6 sample products across categories

### 🔧 **Backend API Endpoints:**
- `GET /` - Health check
- `POST /api/chat` - Conversational AI
- `POST /api/voice/speech-to-text` - Voice input (mock)
- `POST /api/voice/text-to-speech` - Voice output (mock)
- `GET /api/products/search` - Text search
- `POST /api/products/image-search` - Image search (mock)
- `GET /api/cart` - Get cart items
- `POST /api/cart/add` - Add to cart
- `GET /api/products/recommendations` - Get recommendations

## 🎬 Demo Scenarios

### 1. **Voice Shopping:**
- Click the microphone button
- Say: "I need wireless headphones under 3000 rupees"
- Watch AI respond and show products

### 2. **Image Search:**
- Upload a product image (try electronics)
- See similar products automatically found
- Add items to cart with one click

### 3. **Chat Interaction:**
- Type: "Show me gaming accessories"
- Type: "Add the mouse to my cart"
- See conversation flow with contextual responses

## 🛠️ Development Notes

### **Mock Data Strategy:**
- Products use Unsplash images for demo
- AI responses are rule-based (will integrate real models later)
- Cart persists in memory (resets on server restart)

### **Next Steps for Real Implementation:**
1. **Voice Models**: Replace browser APIs with Whisper/SpeechT5
2. **Image AI**: Integrate CLIP for real visual search
3. **Conversational AI**: Add Llama 3.1 or Mistral
4. **Data Source**: Implement web scraping or real APIs
5. **Persistence**: Add database for cart/user data

## 🎯 Architecture

```
├── frontend/           # NextJS 14 with TypeScript
│   ├── src/app/       # App router pages
│   ├── src/components/ # React components
│   └── public/        # Static assets
│
├── flask-backend/     # Python Flask API
│   ├── app.py         # Main application
│   ├── requirements.txt # Dependencies
│   └── venv/          # Virtual environment
│
└── PRD.md             # Product requirements
```

## 🚨 Troubleshooting

### **Voice not working?**
- Use Chrome or Safari (WebKit Speech API required)
- Allow microphone permissions
- Check console for errors

### **Backend not connecting?**
- Ensure Flask runs on port 5000
- Check CORS is enabled
- Verify frontend requests correct URL

### **Images not loading?**
- Unsplash images require internet connection
- Fallback images will load on error

## 📱 Browser Compatibility

- ✅ Chrome (recommended)
- ✅ Safari 
- ⚠️ Firefox (limited voice support)
- ❌ IE/Edge Legacy

---

**🎉 Ready to demo! Open http://localhost:3000 and start shopping with AI!** 