import secrets
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Jasper - Your SEO Assistant", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# 🔒 Security Setup
security = HTTPBasic()
TEAM_USERNAME = "jasper-team"
TEAM_PASSWORD = "jasper-content-2024"  # Change if you want

def verify_team_access(credentials: HTTPBasicCredentials = Depends(security)):
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = TEAM_USERNAME.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = TEAM_PASSWORD.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access denied - Contact team lead for credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Set up OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

class ContentRequest(BaseModel):
    blog_topic: str
    client_name: str = ""
    specialty: str = ""
    location: str = ""

class JasperAssistant:
    def __init__(self):
        self.personality = "helpful, smart, and slightly sassy"
        self.expertise = "SEO content strategy for healthcare"
    
    def generate_content_outline(self, request: ContentRequest):
        """Jasper's main content generation function - now matches your real workflow!"""
        
        # UPDATE THE PROMPT in app.py - Replace the prompt section:

        prompt = f"""
Hey! I'm Jasper, your SEO content assistant. I need to create a blog assignment that matches your exact workflow template.

BLOG TOPIC: {request.blog_topic}

CLIENT CONTEXT:
- Practice Name: {request.client_name or 'Healthcare Practice'}
- Medical Specialty: {request.specialty or 'General Healthcare'}  
- Location: {request.location or 'Local Area'}

Please generate content in this EXACT JSON format:
{{
  "title": "SEO optimized title tag under 60 characters",
  "meta": "Compelling meta description under 160 characters",
  "primaryKeywords": "Main target keyword phrase",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "cta": "Specific call-to-action recommendation for this content",
  "resources": ["Resource 1 suggestion", "Resource 2 suggestion", "Resource 3 suggestion"],
  "h1": "Main page heading",
  "h2Sections": [
    {{
      "heading": "H2 section title",
      "h3Content": "• Brief bullet point guidance\n• What key info to include\n• Specific angle or focus"
    }}
  ],
  "url": "/url-slug-format",
  "jasperNotes": "Additional strategic insights from Jasper"
}}

CRITICAL REQUIREMENTS:
- Generate EXACTLY 4-5 H2 sections minimum (not just 1-2)
- H3 content should be 3-4 SHORT bullet points only
- Each bullet should be 5-10 words max, not full sentences
- Follow this H2 structure: Introduction → Symptoms/Signs → Treatment Options → Why Choose Us → Call to Action
- Make it specific to {request.specialty or 'healthcare'} in {request.location or 'the local area'}
- Keep H3 guidance concise - just quick notes for content writers

Example H3 format:
• Define condition simply
• Include prevalence stats  
• Mention patient concerns
• Add reassuring tone
"""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are Jasper, an expert SEO content strategist specializing in healthcare marketing. You create content that converts patients into appointments. CRITICAL: Always respond with ONLY valid JSON format - no extra text before or after the JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Clean up common JSON issues
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            # Debug print
            print("DEBUG - AI Response:")
            print(ai_response[:200] + "..." if len(ai_response) > 200 else ai_response)
            
            # Parse the response
            content = json.loads(ai_response)
            
            return {
                "success": True,
                "content": content,
                "message": "Jasper created your blog assignment template! 📋✨"
            }
            
        except json.JSONDecodeError as e:
            print(f"JSON Error: {e}")
            print(f"Problematic response: {ai_response[:500]}")
            return {
                "success": False,
                "error": f"Jasper got confused parsing the response. JSON Error: {str(e)}",
                "content": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Jasper encountered an issue: {str(e)}",
                "content": None
            }

# Initialize Jasper
jasper = JasperAssistant()

@app.get("/", response_class=HTMLResponse)
async def home(username: str = Depends(verify_team_access)):
    """Serve the main interface - now protected"""
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/generate-content")
async def generate_content(request: ContentRequest, username: str = Depends(verify_team_access)):
    """Generate content - now protected"""
    
    if not request.blog_topic.strip():
        raise HTTPException(status_code=400, detail="Jasper needs a blog topic to work with!")
    
    result = jasper.generate_content_outline(request)
    return result
    pass

@app.get("/jasper-status")
async def jasper_status(username: str = Depends(verify_team_access)):
    """Check status - now protected"""
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    return {
        "status": "ready" if api_key_set else "needs_api_key",
        "message": "Jasper is ready to generate amazing content! 🚀" if api_key_set else "Jasper needs an OpenAI API key to get started.",
        "personality": jasper.personality,
        "expertise": jasper.expertise
    }
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)