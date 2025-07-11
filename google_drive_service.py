# google_drive_service.py - Jasper's Google Drive Magic! 📄🚀

import os
import json
from typing import Dict, List, Optional
from datetime import datetime

# Google API imports
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class JasperGoogleDriveService:
    """
    Jasper's Google Drive integration - creates perfectly formatted Google Docs automatically!
    Now with HTML copy/paste approach for PERFECT tables! 🚀
    """
    
    # Google Drive API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/documents'
    ]
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.drive_service = None
        self.docs_service = None
        self.setup_services()
    
    def setup_services(self):
        """Initialize Google Drive and Docs services - works locally AND on Render!"""
        try:
            # Check if running on Render (with environment variables)
            google_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            google_token_json = os.getenv("GOOGLE_TOKEN_JSON")
            
            if google_creds_json and not os.path.exists(self.credentials_file):
                # Running on Render - create credentials file from environment
                print("🌐 Render detected - creating credentials from environment variable")
                with open(self.credentials_file, 'w') as f:
                    f.write(google_creds_json)
            
            if google_token_json and not os.path.exists(self.token_file):
                # Running on Render - create token file from environment
                print("🌐 Render detected - creating token from environment variable")
                with open(self.token_file, 'w') as f:
                    f.write(google_token_json)
            
            # Load existing token
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(f"Google credentials not found. Set GOOGLE_CREDENTIALS_JSON environment variable or add credentials.json file.")
                    
                    # For Render deployment, we can't do interactive auth
                    if google_creds_json:
                        raise Exception("Interactive authentication required. Please set up authentication locally first, then copy token.json content to GOOGLE_TOKEN_JSON environment variable.")
                    
                    # Local development - interactive auth
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.token_file, 'w') as token:
                    token.write(self.creds.to_json())
            
            # Build services
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            self.docs_service = build('docs', 'v1', credentials=self.creds)
            
            print("✅ Google Drive services initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error setting up Google Drive services: {e}")
            self.drive_service = None
            self.docs_service = None
            raise e
    
    def create_blog_assignment_doc(self, 
                                 content: Dict, 
                                 blog_topic: str,
                                 client_info: Dict = None,
                                 folder_id: str = None,
                                 share_emails: List[str] = None,
                                 use_html_approach: bool = True) -> Dict:
        """
        Create perfectly formatted Google Doc with HTML copy/paste approach! 🎯
        """
        
        if use_html_approach:
            return self.create_html_copy_paste_doc(
                content=content,
                blog_topic=blog_topic,
                client_info=client_info,
                share_emails=share_emails
            )
        else:
            # Fallback to old method
            return self.create_simple_blog_assignment_doc(
                content=content,
                blog_topic=blog_topic,
                client_info=client_info,
                folder_id=folder_id,
                share_emails=share_emails
            )
    
    def create_html_copy_paste_doc(self, 
                                 content: Dict, 
                                 blog_topic: str,
                                 client_info: Dict = None,
                                 share_emails: List[str] = None) -> Dict:
        """
        Create document with HTML content that becomes perfect tables when pasted! 📋✨
        """
        
        try:
            # Generate document title
            client_name = client_info.get('name', 'Healthcare Practice') if client_info else 'Healthcare Practice'
            timestamp = datetime.now().strftime('%B %Y')
            doc_title = f"{client_name} - Blog - {blog_topic} - {timestamp}"
            
            # Create the document
            doc_body = {'title': doc_title}
            doc = self.docs_service.documents().create(body=doc_body).execute()
            doc_id = doc.get('documentId')
            
            print(f"✅ Created HTML copy/paste doc: {doc_title}")
            
            # Generate the HTML content that will become a perfect table
            html_content = self.generate_perfect_html_content(content, blog_topic)
            
            # Create instructions for the user
            instructions = f"""🎯 COPY THE HTML BELOW AND PASTE INTO GOOGLE DOCS FOR PERFECT TABLES!

INSTRUCTIONS:
1. Select and copy the HTML content below (starting from <h2>BLOG ASSIGNMENT</h2>)
2. Open this Google Doc: {f"https://docs.google.com/document/d/{doc_id}/edit"}
3. Paste the HTML content (Ctrl+V or Cmd+V)
4. Google Docs will automatically convert it to perfect tables and formatting!

═══════════════════════════════════════════════════════════════

{html_content}

═══════════════════════════════════════════════════════════════

📋 The HTML above will create EXACTLY the table format you want when pasted into Google Docs!
"""
            
            # Insert the instructions into the Google Doc
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': instructions
                }
            }]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            print("✅ Added HTML copy/paste instructions!")
            
            # Share with team
            if share_emails:
                self.share_document(doc_id, share_emails)
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                "success": True,
                "doc_id": doc_id,
                "doc_url": doc_url,
                "doc_title": doc_title,
                "message": f"Created HTML copy/paste document! Copy the HTML from the doc and paste it for perfect tables! 📋✨",
                "html_content": html_content,
                "used_html_approach": True
            }
            
        except Exception as e:
            print(f"❌ HTML copy/paste error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to create HTML copy/paste document: {e}"
            }
    
    def generate_perfect_html_content(self, content: Dict, blog_topic: str) -> str:
        """
        Generate HTML that creates EXACTLY your table format when pasted into Google Docs! 🎯
        """
        
        # Create HTML that will become a perfect Google Docs table
        html = f'''<h2>BLOG ASSIGNMENT</h2>

<table border="1" style="border-collapse: collapse; width: 100%; margin-bottom: 20px;">
    <tr style="background-color: #f0f0f0;">
        <td style="padding: 12px; font-weight: bold; width: 200px; border: 1px solid #ccc;"><strong>Title:</strong></td>
        <td style="padding: 12px; border: 1px solid #ccc;">{content.get('title', 'N/A')}</td>
    </tr>
    <tr>
        <td style="padding: 12px; font-weight: bold; border: 1px solid #ccc;"><strong>Meta:</strong></td>
        <td style="padding: 12px; border: 1px solid #ccc;">{content.get('meta', 'N/A')}</td>
    </tr>
    <tr style="background-color: #f0f0f0;">
        <td style="padding: 12px; font-weight: bold; border: 1px solid #ccc;"><strong>Primary Keywords:</strong></td>
        <td style="padding: 12px; border: 1px solid #ccc;">{content.get('primaryKeywords', 'N/A')}</td>
    </tr>
    <tr>
        <td style="padding: 12px; font-weight: bold; border: 1px solid #ccc;"><strong>Keywords:</strong></td>
        <td style="padding: 12px; border: 1px solid #ccc;">{', '.join(content.get('keywords', []))}</td>
    </tr>
    <tr style="background-color: #f0f0f0;">
        <td style="padding: 12px; font-weight: bold; border: 1px solid #ccc;"><strong>CTA:</strong></td>
        <td style="padding: 12px; border: 1px solid #ccc;">{content.get('cta', 'N/A')}</td>
    </tr>
    <tr>
        <td style="padding: 12px; font-weight: bold; border: 1px solid #ccc;"><strong>Resources:</strong></td>
        <td style="padding: 12px; border: 1px solid #ccc;">{'<br>'.join([f"• {resource}" for resource in content.get('resources', [])])}</td>
    </tr>
</table>

<h1>{content.get('h1', 'Main Heading')}</h1>

'''
        
        # Add H2 sections
        for section in content.get('h2Sections', []):
            html += f'''<h2>{section.get('heading', 'Section Heading')}</h2>

'''
            
            # Add bullet points
            bullets = section.get('h3Content', '').split('\n')
            for bullet in bullets:
                if bullet.strip():
                    clean_bullet = bullet.strip().replace('- ', '').replace('• ', '')
                    html += f'''<p>• {clean_bullet}</p>
'''
            
            html += '''
'''
        
        # Add Jasper notes if available
        if content.get('jasperNotes'):
            html += f'''<hr>
<p><strong>🤖 Jasper's Strategic Insights:</strong> {content.get('jasperNotes')}</p>'''
        
        return html
    
    def create_simple_blog_assignment_doc(self, 
                                         content: Dict, 
                                         blog_topic: str,
                                         client_info: Dict = None,
                                         folder_id: str = None,
                                         share_emails: List[str] = None) -> Dict:
        """
        FALLBACK METHOD - Create complete blog assignment doc
        """
        
        try:
            # Generate document title
            client_name = client_info.get('name', 'Healthcare Practice') if client_info else 'Healthcare Practice'
            timestamp = datetime.now().strftime('%m/%d/%Y')
            doc_title = f"Blog Assignment - {blog_topic} - {client_name} - {timestamp}"
            
            # Create the document
            doc_body = {'title': doc_title}
            doc = self.docs_service.documents().create(body=doc_body).execute()
            doc_id = doc.get('documentId')
            
            print(f"✅ Created fallback Google Doc: {doc_title}")
            
            # Add content using existing method
            self.add_complete_content_to_doc(doc_id, content, blog_topic, client_info)
            
            # Share with team members
            if share_emails:
                self.share_document(doc_id, share_emails)
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                "success": True,
                "doc_id": doc_id,
                "doc_url": doc_url,
                "doc_title": doc_title,
                "message": f"Created fallback blog assignment '{doc_title}' successfully!",
                "used_fallback": True
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create fallback document: {e}"
            }
    
    def add_complete_content_to_doc(self, doc_id: str, content: Dict, blog_topic: str, client_info: Dict = None):
        """Add content to document - fallback formatting"""
        
        # Build professional content
        content_parts = []
        content_parts.append("BLOG ASSIGNMENT")
        content_parts.append("")
        content_parts.append("-" * 150)
        content_parts.append(f"Title:          {content.get('title', 'N/A')}")
        content_parts.append(f"Meta:           {content.get('meta', 'N/A')}")
        content_parts.append(f"Primary Keywords: {content.get('primaryKeywords', 'N/A')}")
        content_parts.append(f"Keywords:       {', '.join(content.get('keywords', []))}")
        content_parts.append(f"CTA:            {content.get('cta', 'N/A')}")
        content_parts.append(f"Resources:      {' | '.join(content.get('resources', []))}")
        content_parts.append("-" * 150)
        content_parts.append("")
        content_parts.append("")
        
        # H1 Header
        content_parts.append(f"# {content.get('h1', 'Main Heading')}")
        content_parts.append("")
        
        # H2 Sections
        for section in content.get('h2Sections', []):
            content_parts.append(f"## {section.get('heading', 'Section Heading')}")
            content_parts.append("")
            
            bullets = section.get('h3Content', '').split('\n')
            for bullet in bullets:
                if bullet.strip():
                    clean_bullet = bullet.strip().replace('- ', '').replace('• ', '')
                    content_parts.append(f"• {clean_bullet}")
            
            content_parts.append("")
        
        if content.get('jasperNotes'):
            content_parts.append("---")
            content_parts.append(f"🤖 Jasper's Strategic Insights: {content.get('jasperNotes')}")
        
        full_content = "\n".join(content_parts)
        
        # Insert content
        requests = [{
            'insertText': {
                'location': {'index': 1},
                'text': full_content
            }
        }]
        
        try:
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            print("✅ Content added successfully!")
        except Exception as e:
            print(f"❌ Error adding content: {e}")
    
    def share_document(self, doc_id: str, email_addresses: List[str], role: str = 'writer'):
        """Share the document with specified email addresses"""
        try:
            for email in email_addresses:
                permission = {
                    'type': 'user',
                    'role': role,
                    'emailAddress': email.strip()
                }
                
                self.drive_service.permissions().create(
                    fileId=doc_id,
                    body=permission,
                    sendNotificationEmail=True
                ).execute()
                
                print(f"✅ Shared document with {email}")
                
        except Exception as e:
            print(f"❌ Error sharing document: {e}")
    
    def create_perfect_template(self) -> Dict:
        """Create a perfect template document"""
        
        try:
            template_content = """**Title:** <title-tag>
**Meta:** <meta-description>
**Primary Keywords:** <primary-keywords>
**Keywords:** <keywords>
**CTA:** <cta>
**Resources:**
<resources>

**Content Structure:**
[Content writers fill this section based on generated outline]

H1: 

H2: 

H2: 

H2: 

**Notes:**
Generated by Jasper 🤖 - Your AI SEO Assistant
"""
            
            doc_body = {'title': 'Jasper Blog Assignment Template - MASTER'}
            doc = self.docs_service.documents().create(body=doc_body).execute()
            doc_id = doc.get('documentId')
            
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': template_content
                }
            }]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                "success": True,
                "template_doc_id": doc_id,
                "template_url": doc_url,
                "message": f"Perfect template created! Copy this ID to your .env: JASPER_TEMPLATE_DOC_ID={doc_id}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create template: {e}"
            }
    
    def test_connection(self) -> Dict:
        """Test Google Drive connection and permissions"""
        if not self.drive_service:
            return {
                "success": False,
                "error": "Google Drive service not initialized"
            }
        
        try:
            results = self.drive_service.files().list(pageSize=1).execute()
            
            return {
                "success": True,
                "message": "Google Drive connection successful!",
                "can_create_docs": bool(self.docs_service)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Google Drive connection failed: {e}"
            }

# Setup instructions and example usage
if __name__ == "__main__":
    print("🚀 Testing Jasper's Google Drive Integration...")
    
    # Initialize the service
    drive_service = JasperGoogleDriveService()
    
    # Test connection
    test_result = drive_service.test_connection()
    print(f"📄 Connection Test: {test_result}")
    
    if test_result["success"]:
        print("\n✅ Google Drive integration is ready!")
        print("📋 HTML Copy/Paste approach enabled for perfect tables!")
    else:
        print("\n❌ Setup needed")