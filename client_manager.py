import json
import os
from typing import List, Dict, Optional
from pathlib import Path

class ClientProfileManager:
    """
    Jasper's client intelligence system - knows everything about your PE healthcare clients!
    Loads, manages, and serves client profiles for personalized content generation.
    """
    
    def __init__(self, profiles_directory: str = "client_profiles"):
        self.profiles_directory = Path(profiles_directory)
        self.clients = {}
        self.load_all_clients()
    
    def load_all_clients(self) -> None:
        """Load all client profiles from JSON files - Jasper's getting to know the clients!"""
        try:
            if not self.profiles_directory.exists():
                print(f"⚠️ Client profiles directory '{self.profiles_directory}' not found. Creating it...")
                self.profiles_directory.mkdir(exist_ok=True)
                return
            
            # Load all JSON files in the client_profiles directory
            json_files = list(self.profiles_directory.glob("*.json"))
            
            if not json_files:
                print("📝 No client profiles found. Jasper is ready to learn about new clients!")
                return
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        client_data = json.load(f)
                        client_id = client_data.get('client_id')
                        
                        if client_id:
                            self.clients[client_id] = client_data
                            print(f"✅ Loaded client profile: {client_data.get('name', client_id)}")
                        else:
                            print(f"⚠️ Client profile {json_file.name} missing 'client_id' field")
                            
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing {json_file.name}: {e}")
                except Exception as e:
                    print(f"❌ Error loading {json_file.name}: {e}")
                    
            print(f"🎉 Jasper loaded {len(self.clients)} client profiles!")
            
        except Exception as e:
            print(f"❌ Error loading client profiles: {e}")
    
    def get_all_clients(self) -> Dict[str, Dict]:
        """Get all loaded client profiles"""
        return self.clients.copy()
    
    def get_client_by_id(self, client_id: str) -> Optional[Dict]:
        """Get a specific client profile by ID"""
        return self.clients.get(client_id)
    
    def get_client_list_for_dropdown(self) -> List[Dict[str, str]]:
        """Get simplified client list perfect for UI dropdown"""
        dropdown_list = []
        
        for client_id, client_data in self.clients.items():
            dropdown_list.append({
                "id": client_id,
                "name": client_data.get("name", "Unknown Practice"),
                "specialty": client_data.get("specialty", ""),
                "location": client_data.get("location", "")
            })
        
        # Sort by name for better UX
        dropdown_list.sort(key=lambda x: x["name"])
        
        return dropdown_list
    
    def get_client_context_for_ai(self, client_id: str) -> str:
        """
        Generate rich context about a client for AI content generation
        This is where Jasper gets SMART about each client! 🤖
        """
        client = self.get_client_by_id(client_id)
        
        if not client:
            return "No specific client context available."
        
        # Build comprehensive context for the AI
        context_parts = [
            f"CLIENT: {client.get('name', 'Unknown Practice')}",
            f"SPECIALTY: {client.get('specialty', 'General Healthcare')}",
            f"LOCATION: {client.get('location', 'Local Area')}",
            f"TARGET AUDIENCE: {client.get('target_audience', 'General patients')}"
        ]
        
        # Add brand voice guidance
        brand_voice = client.get('brand_voice', '')
        if brand_voice:
            context_parts.append(f"BRAND VOICE: {brand_voice}")
        
        # Add services they offer
        services = client.get('services', [])
        if services:
            context_parts.append(f"SERVICES: {', '.join(services)}")
        
        # Add content preferences
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
        
        # Add SEO focus keywords
        seo_focus = client.get('seo_focus', [])
        if seo_focus:
            context_parts.append(f"PRIMARY SEO TARGETS: {', '.join(seo_focus)}")
        
        # Add competitor awareness
        competitors = client.get('competitors', [])
        if competitors:
            context_parts.append(f"MAIN COMPETITORS: {', '.join(competitors)}")
        
        return "\n".join(context_parts)
    
    def validate_client_profile(self, client_data: Dict) -> List[str]:
        """Validate a client profile and return any issues found"""
        issues = []
        
        required_fields = ['client_id', 'name', 'specialty', 'location']
        for field in required_fields:
            if not client_data.get(field):
                issues.append(f"Missing required field: {field}")
        
        # Check for reasonable data types
        if client_data.get('services') and not isinstance(client_data['services'], list):
            issues.append("'services' should be a list")
        
        if client_data.get('competitors') and not isinstance(client_data['competitors'], list):
            issues.append("'competitors' should be a list")
        
        if client_data.get('seo_focus') and not isinstance(client_data['seo_focus'], list):
            issues.append("'seo_focus' should be a list")
        
        return issues
    
    def add_client_profile(self, client_data: Dict) -> bool:
        """Add a new client profile (for future client management features)"""
        try:
            # Validate the profile
            issues = self.validate_client_profile(client_data)
            if issues:
                print(f"❌ Client profile validation failed: {issues}")
                return False
            
            client_id = client_data['client_id']
            
            # Save to file
            file_path = self.profiles_directory / f"{client_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(client_data, f, indent=2, ensure_ascii=False)
            
            # Add to memory
            self.clients[client_id] = client_data
            
            print(f"✅ Added new client profile: {client_data['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Error adding client profile: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get some fun stats about loaded clients"""
        if not self.clients:
            return {"total_clients": 0}
        
        specialties = {}
        locations = {}
        
        for client in self.clients.values():
            specialty = client.get('specialty', 'Unknown')
            location = client.get('location', 'Unknown')
            
            specialties[specialty] = specialties.get(specialty, 0) + 1
            locations[location] = locations.get(location, 0) + 1
        
        return {
            "total_clients": len(self.clients),
            "specialties": specialties,
            "locations": locations,
            "most_common_specialty": max(specialties.items(), key=lambda x: x[1])[0] if specialties else "None",
            "most_common_location": max(locations.items(), key=lambda x: x[1])[0] if locations else "None"
        }

# Example usage and testing
if __name__ == "__main__":
    print("🚀 Testing Jasper's Client Profile Manager...")
    
    # Initialize the manager
    client_manager = ClientProfileManager()
    
    # Show stats
    stats = client_manager.get_stats()
    print(f"\n📊 Client Stats: {stats}")
    
    # Show dropdown data
    dropdown_data = client_manager.get_client_list_for_dropdown()
    print(f"\n📋 Dropdown Data: {dropdown_data}")
    
    # Test AI context generation
    if dropdown_data:
        test_client_id = dropdown_data[0]['id']
        ai_context = client_manager.get_client_context_for_ai(test_client_id)
        print(f"\n🤖 AI Context for {test_client_id}:")
        print(ai_context)
    
    print("\n✅ Client Profile Manager is ready to rock!")