import secrets
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from typing import Optional, List, Dict
from pathlib import Path

# Load environment variables
load_dotenv()

app = FastAPI(title="Jasper - Your SEO Assistant", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Security Setup
security = HTTPBasic()
TEAM_USERNAME = "jasper-team"
TEAM_PASSWORD = "jasper-content-2024"

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

# CLIENT PROFILE MANAGER
class ClientProfileManager:
    def __init__(self, profiles_directory: str = "client_profiles"):
        self.profiles_directory = Path(profiles_directory)
        self.clients = {}
        self.load_all_clients()
    
    def load_all_clients(self) -> None:
        try:
            if not self.profiles_directory.exists():
                print(f"Creating client profiles directory: {self.profiles_directory}")
                self.profiles_directory.mkdir(exist_ok=True)
                return
            
            json_files = list(self.profiles_directory.glob("*.json"))
            
            if not json_files:
                print("No client profiles found. Ready to learn about new clients!")
                return
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        client_data = json.load(f)
                        client_id = client_data.get('client_id')
                        
                        if client_id:
                            self.clients[client_id] = client_data
                            print(f"Loaded client: {client_data.get('name', client_id)}")
                        else:
                            print(f"Client profile {json_file.name} missing 'client_id'")
                            
                except json.JSONDecodeError as e:
                    print(f"Error parsing {json_file.name}: {e}")
                except Exception as e:
                    print(f"Error loading {json_file.name}: {e}")
                    
            print(f"Jasper loaded {len(self.clients)} client profiles!")
            
        except Exception as e:
            print(f"Error loading client profiles: {e}")
    
    def get_all_clients(self) -> Dict[str, Dict]:
        return self.clients.copy()
    
    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        return self.clients.get(client_id)
    
    def get_client_list_for_dropdown(self) -> List[Dict[str, str]]:
        dropdown_list = []
        
        for client_id, client_data in self.clients.items():
            dropdown_list.append({
                "id": client_id,
                "name": client_data.get("name", "Unknown Practice"),
                "specialty": client_data.get("specialty", ""),
                "location": client_data.get("location", "")
            })
        
        dropdown_list.sort(key=lambda x: x["name"])
        return dropdown_list
    
    def get_client_context_for_ai(self, client_id: str) -> str:
        client = self.get_client_by_id(client_id)
        
        if not client:
            return ""
        
        context_parts = [
            f"CLIENT: {client.get('name', 'Unknown Practice')}",
            f"SPECIALTY: {client.get('specialty', 'General Healthcare')}",
            f"LOCATION: {client.get('location', 'Local Area')}",
            f"TARGET AUDIENCE: {client.get('target_audience', 'General patients')}"
        ]
        
        brand_voice = client.get('brand_voice', '')
        if brand_voice:
            context_parts.append(f"BRAND VOICE: {brand_voice}")
        
        services = client.get('services', [])
        if services:
            context_parts.append(f"SERVICES: {', '.join(services)}")
        
        content_prefs = client.get('content_preferences', {})
        if content_prefs:
            prefs_text = []
            if content_prefs.get('tone'):
                prefs_text.append(f"tone should be {content_prefs['tone']}")
            if content_prefs.get('include_statistics'):
                prefs_text.append("include relevant statistics")
            if content_prefs.get('include_patient_stories') == False:
                prefs_text.append("avoid patient stories")
            
            if prefs_text:
                context_parts.append(f"CONTENT PREFERENCES: {', '.join(prefs_text)}")
        
        seo_focus = client.get('seo_focus', [])
        if seo_focus:
            context_parts.append(f"PRIMARY SEO TARGETS: {', '.join(seo_focus)}")
        
        competitors = client.get('competitors', [])
        if competitors:
            context_parts.append(f"MAIN COMPETITORS: {', '.join(competitors)}")
        
        return "\n".join(context_parts)

# Initialize Client Manager
client_manager = ClientProfileManager()

# REQUEST MODEL
class ContentRequest(BaseModel):
    blog_topic: str
    client_id: Optional[str] = None
    client_name: str = ""
    specialty: str = ""
    location: str = ""

class JasperAssistant:
    def __init__(self, client_manager: ClientProfileManager):
        self.personality = "helpful, smart, and slightly witty"
        self.expertise = "SEO content strategy for healthcare"
        self.client_manager = client_manager
    
    def generate_content_outline(self, request: ContentRequest):
        client_context = ""
        client_info = {
            "name": request.client_name or 'Healthcare Practice',
            "specialty": request.specialty or 'General Healthcare',
            "location": request.location or 'Local Area'
        }
        
        if request.client_id:
            client_context = self.client_manager.get_client_context_for_ai(request.client_id)
            if client_context:
                client_data = self.client_manager.get_client_by_id(request.client_id)
                if client_data:
                    client_info = {
                        "name": client_data.get("name", client_info["name"]),
                        "specialty": client_data.get("specialty", client_info["specialty"]),
                        "location": client_data.get("location", client_info["location"])
                    }

        # Build the prompt parts separately to avoid f-string backslash issues
        client_context_section = f"ADDITIONAL CLIENT INTELLIGENCE:\n{client_context}\n" if client_context else ""
        client_alignment_note = "- Align with the client's brand voice and content preferences shown above" if client_context else ""
        
        prompt = f"""Hey! I'm Jasper, your SEO content assistant. I need to create a blog assignment that matches your exact workflow template.

BLOG TOPIC: {request.blog_topic}

CLIENT CONTEXT:
- Practice Name: {client_info['name']}
- Medical Specialty: {client_info['specialty']}  
- Location: {client_info['location']}

{client_context_section}

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
      "h3Content": "- Brief bullet point guidance\\n- What key info to include\\n- Specific angle or focus"
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
- Make it specific to {client_info['specialty']} in {client_info['location']}
- Keep H3 guidance concise - just quick notes for content writers
{client_alignment_note}

Example H3 format:
- Define condition simply
- Include prevalence stats  
- Mention patient concerns
- Add reassuring tone"""
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are Jasper, an expert SEO content strategist specializing in healthcare marketing. You create content that converts patients into appointments. {f'You have deep knowledge about this specific client and should tailor content accordingly.' if client_context else ''} CRITICAL: Always respond with ONLY valid JSON format - no extra text before or after the JSON."
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
            
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            
            print("DEBUG - AI Response:")
            print(ai_response[:200] + "..." if len(ai_response) > 200 else ai_response)
            
            content = json.loads(ai_response)
            
            success_message = "Jasper created your blog assignment template! 📋✨"
            if client_context:
                success_message = f"Jasper created a personalized blog assignment for {client_info['name']}! 🎯✨"
            
            return {
                "success": True,
                "content": content,
                "message": success_message,
                "used_client_profile": bool(client_context)
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

# Initialize Enhanced Jasper
jasper = JasperAssistant(client_manager)

# API ENDPOINTS
@app.get("/clients")
async def get_clients(username: str = Depends(verify_team_access)):
    try:
        clients = client_manager.get_client_list_for_dropdown()
        return {
            "success": True,
            "clients": clients,
            "total": len(clients)
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Error loading clients: {str(e)}",
            "clients": []
        }

@app.get("/clients/{client_id}")
async def get_client_details(client_id: str, username: str = Depends(verify_team_access)):
    try:
        client = client_manager.get_client_by_id(client_id)
        if not client:
            raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found")
        
        return {
            "success": True,
            "client": client
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "success": False,
            "error": f"Error loading client: {str(e)}"
        }

@app.get("/", response_class=HTMLResponse)
async def home(username: str = Depends(verify_team_access)):
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/generate-content")
async def generate_content(request: ContentRequest, username: str = Depends(verify_team_access)):
    if not request.blog_topic.strip():
        raise HTTPException(status_code=400, detail="Jasper needs a blog topic to work with!")
    
    result = jasper.generate_content_outline(request)
    return result

@app.get("/jasper-status")
async def jasper_status(username: str = Depends(verify_team_access)):
    api_key_set = bool(os.getenv("OPENAI_API_KEY"))
    client_count = len(client_manager.get_all_clients())
    
    status_message = "Jasper is ready to generate amazing content! 🚀"
    if api_key_set and client_count > 0:
        status_message = f"Jasper is ready with {client_count} client profiles loaded! 🧠✨"
    elif not api_key_set:
        status_message = "Jasper needs an OpenAI API key to get started."
    
    return {
        "status": "ready" if api_key_set else "needs_api_key",
        "message": status_message,
        "personality": jasper.personality,
        "expertise": jasper.expertise,
        "client_profiles_loaded": client_count,
        "intelligence_level": "ENHANCED" if client_count > 0 else "BASIC"
    }

@app.get("/debug")
async def debug_files():
    import os
    try:
        files = os.listdir(".")
        static_exists = os.path.exists("static")
        static_files = os.listdir("static") if static_exists else []
        profiles_exists = os.path.exists("client_profiles")
        profile_files = os.listdir("client_profiles") if profiles_exists else []
        
        return {
            "current_directory": os.getcwd(),
            "files_in_root": files,
            "static_folder_exists": static_exists,
            "static_files": static_files,
            "client_profiles_folder_exists": profiles_exists,
            "client_profile_files": profile_files,
            "loaded_clients": len(client_manager.get_all_clients())
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)