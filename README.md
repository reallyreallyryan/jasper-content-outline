# 🤖 Jasper - Your AI Content SEO Assistant

**AI-powered SEO content generator for healthcare marketing teams.**

Jasper transforms blog topics into complete, client-specific SEO content outlines that match your exact workflow templates. 

## 🚀 What Jasper Does

- **📋 Complete Blog Assignments** - Title, meta, keywords, H1/H2/H3 structure, CTAs, resources
- **🧠 Client Intelligence** - Learns each client's brand voice, services, and preferences  
- **⚡ Instant Generation** - From topic to full content outline in seconds
- **🎯 SEO Optimized** - Built for healthcare marketing that converts patients to appointments
- **📊 Workflow Integration** - Matches your existing content creation process

## 🧠 Client Intelligence System

Jasper's breakthrough feature - **learns about each client** and generates personalized content:

### What Jasper Knows About Each Client:
- **Brand Voice** (Professional, friendly, authoritative, etc.)
- **Medical Services** (Heart surgery, dental implants, etc.)
- **Target Audience** (Adults 45+, families, etc.)
- **Content Preferences** (Include stats, avoid patient stories, etc.)
- **SEO Targets** (Primary keywords and focus areas)
- **Competitors** (For strategic positioning)
- **Location** (Local SEO optimization)

### Example: Austin Heart Center
```json
{
  "client_id": "austin_heart_center",
  "name": "Austin Heart Center", 
  "specialty": "Cardiothoracic Surgery",
  "brand_voice": "Professional, reassuring, authoritative",
  "services": ["Heart Surgery", "Valve Repair", "Bypass Surgery"],
  "seo_focus": ["heart surgery austin", "cardiothoracic surgeon"]
}
```

**Result:** Content specifically tailored to Austin Heart Center's professional tone, heart surgery expertise, and Austin market.

## 🏗️ Architecture

```
📁 jasper-content-outline/
├── 🔧 app.py                 # FastAPI backend with client intelligence
├── 📁 client_profiles/       # JSON files for each client
│   └── 📄 austin_heart_center.json
├── 📁 static/
│   ├── 🎨 index.html         # Client-smart UI interface  
│   ├── 💅 style.css          # Beautiful styling
│   └── 🧠 script.js          # Frontend client intelligence
├── 📋 requirements.txt       # Python dependencies
├── 🔒 .env                   # OpenAI API key (not in repo)
└── 🚀 railway.json          # Deployment config
```

## ⚡ Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/jasper-content-outline.git
cd jasper-content-outline
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3. Run Jasper
```bash
python app.py
# Visit: http://localhost:8000
# Login: jasper-team / jasper-content-2024
```

## 🏥 Adding New Clients

**Super Easy!** Just add a JSON file to `/client_profiles/`:

```json
{
  "client_id": "new_practice_id",
  "name": "Your Practice Name",
  "specialty": "Medical Specialty", 
  "location": "City, State",
  "target_audience": "Your target patients",
  "brand_voice": "Professional tone description",
  "services": [
    "Service 1",
    "Service 2", 
    "Service 3"
  ],
  "competitors": [
    "Competitor 1",
    "Competitor 2"
  ],
  "content_preferences": {
    "tone": "Educational but accessible",
    "include_statistics": true,
    "include_patient_stories": false
  },
  "seo_focus": [
    "primary keyword",
    "secondary keyword",
    "location + service"
  ]
}
```

**Restart Jasper** → New client appears in dropdown → Instant smart generation! 🎯

## 🎨 User Interface

### Client Selection
- **Smart Dropdown** - All clients loaded automatically
- **Client Preview** - Shows key details when selected  
- **Auto-Population** - Practice name, specialty, location filled automatically
- **Intelligence Badge** - Visual indicator when using client profile

### Content Generation  
- **Blog Topic Input** - What you want Jasper to write about
- **Smart Generation** - Uses client intelligence when available
- **Instant Output** - Complete blog assignment in seconds
- **Download Ready** - TXT format for easy use

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main interface |
| `/generate-content` | POST | Generate content outline |
| `/clients` | GET | List all client profiles |
| `/clients/{client_id}` | GET | Get specific client details |
| `/jasper-status` | GET | System status and stats |

## 📋 Content Output Format

Jasper generates complete blog assignments with:

### SEO Metadata
- **Title Tag** (under 60 characters)
- **Meta Description** (under 160 characters)  
- **Primary Keywords**
- **Keyword List** (5 targeted keywords)

### Content Structure
- **H1** - Main page heading
- **H2 Sections** (4-5 sections):
  - Introduction
  - Symptoms/Signs  
  - Treatment Options
  - Why Choose Us
  - Call to Action
- **H3 Content** - Brief guidance for writers
- **URL Slug** - SEO-friendly URL
- **CTA Recommendation**
- **Resource Suggestions**

### Strategic Insights
- **Jasper's Notes** - Additional strategic recommendations
- **Client-Specific Guidance** - When using client profiles

## 🛡️ Security Features

- **HTTP Basic Authentication** - Team access protection
- **Environment Variables** - API keys secured
- **Input Validation** - Prevents malicious content
- **Error Handling** - Graceful failure management

## 🚀 Deployment

### Railway (Current)
```bash
# Automatic deployment from GitHub
git push origin main
```

### Local Development
```bash
python app.py
# Access: http://localhost:8000
```

## 🔧 Technical Stack

- **Backend**: FastAPI (Python)
- **AI**: OpenAI GPT-4
- **Frontend**: HTML/CSS/JavaScript
- **Deployment**: Railway
- **Storage**: JSON files (client profiles)

## 📊 What Makes Jasper Special

### 🧠 **Client Intelligence**
Unlike generic AI tools, Jasper learns each client's unique voice, services, and preferences.

### 📋 **Workflow Integration** 
Generates content in your exact template format - no reformatting needed.

### ⚡ **Speed & Consistency**
From topic to complete outline in under 30 seconds, every time.

### 🎯 **Healthcare Focus**
Built specifically for medical practices and healthcare marketing.

### 💼 **Enterprise Ready**
Secure, scalable, and built for professional teams.

## 🔮 Roadmap

- [ ] **Email Integration** - Send assignments directly to content team
- [ ] **Google Docs Integration** - Create docs automatically  
- [ ] **Batch Processing** - Generate multiple assignments at once
- [ ] **Content Analytics** - Track performance and optimize
- [ ] **Template Customization** - Customize output formats
- [ ] **API Webhooks** - Integrate with other tools

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is proprietary software for internal use.

## 🆘 Support

Having issues? Need a new feature?

- **Documentation**: Check this README
- **Debug Endpoint**: Visit `/debug` for system diagnostics  
- **Status Check**: Visit `/jasper-status` for health check

## 🎉 Success Stories

> "Wow." 
>

---

**Built with ❤️ for by Ryan K**
