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
    No more copy/paste, no more formatting issues - just beautiful, ready-to-edit docs!
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
        """Initialize Google Drive and Docs services"""
        try:
            # Load existing token
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
            
            # If no valid credentials, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        raise FileNotFoundError(f"Google credentials file '{self.credentials_file}' not found!")
                    
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
    
    def create_blog_assignment_doc(self, 
                                 content: Dict, 
                                 blog_topic: str,
                                 client_info: Dict = None,
                                 folder_id: str = None,
                                 share_emails: List[str] = None,
                                 use_template: bool = True) -> Dict:
        """
        Create a perfectly formatted Google Doc with the blog assignment
        Now with template support AND bulletproof fallback! 🪄
        """
        
        # Try template method first if enabled
        if use_template:
            template_result = self.create_new_templated_doc(
                content=content,
                blog_topic=blog_topic,
                client_info=client_info,
                share_emails=share_emails
            )
            
            # If template method worked, return it
            if template_result.get("success"):
                return template_result
            else:
                print(f"⚠️ Template method failed: {template_result.get('error')}")
                print("🔄 Falling back to complete document creation...")
        
        # Fallback to complete document creation
        return self.create_simple_blog_assignment_doc(
            content=content,
            blog_topic=blog_topic,
            client_info=client_info,
            folder_id=folder_id,
            share_emails=share_emails
        )
    
    def create_new_templated_doc(self, 
                               content: Dict, 
                               blog_topic: str,
                               client_info: Dict = None,
                               share_emails: List[str] = None) -> Dict:
        """
        NEW SIMPLIFIED TEMPLATE METHOD - No copying, just read and create fresh!
        """
        
        try:
            template_doc_id = os.getenv("JASPER_TEMPLATE_DOC_ID")
            
            if not template_doc_id:
                return {
                    "success": False,
                    "error": "No template document ID provided. Set JASPER_TEMPLATE_DOC_ID in environment."
                }
            
            print(f"📄 Using template document ID: {template_doc_id}")
            
            # Get the template content first
            template_doc = self.docs_service.documents().get(documentId=template_doc_id).execute()
            template_content = self.extract_text_from_doc(template_doc)
            
            print(f"📄 Retrieved template content ({len(template_content)} characters)")
            
            # Prepare all the replacement values
            replacements = {
                '<title-tag>': content.get('title', 'N/A'),
                '<meta-description>': content.get('meta', 'N/A'),
                '<primary-keywords>': content.get('primaryKeywords', 'N/A'),
                '<keywords>': ', '.join(content.get('keywords', [])),
                '<cta>': content.get('cta', 'N/A'),
                '<resources>': '\n'.join([f"• {resource}" for resource in content.get('resources', [])])
            }
            
            # Add client-specific placeholders if available
            if client_info:
                replacements.update({
                    '<client-name>': client_info.get('name', ''),
                    '<client-specialty>': client_info.get('specialty', ''),
                    '<client-location>': client_info.get('location', ''),
                    '<client-brand-voice>': client_info.get('brand_voice', ''),
                    '<target-audience>': client_info.get('target_audience', '')
                })
            
            # Replace placeholders in the template content
            final_content = template_content
            replacements_made = 0
            
            for placeholder, replacement in replacements.items():
                if placeholder in final_content:
                    final_content = final_content.replace(placeholder, replacement)
                    replacements_made += 1
                    print(f"  ✅ Replaced '{placeholder}' with '{replacement[:30]}{'...' if len(replacement) > 30 else ''}'")
            
            print(f"🔄 Made {replacements_made} replacements in template content")
            
            # Generate document title
            client_name = client_info.get('name', 'Healthcare Practice') if client_info else 'Healthcare Practice'
            timestamp = datetime.now().strftime('%m/%d/%Y')
            doc_title = f"Blog Assignment - {blog_topic} - {client_name} - {timestamp}"
            
            # Create new document with the processed content
            doc_body = {'title': doc_title}
            doc = self.docs_service.documents().create(body=doc_body).execute()
            new_doc_id = doc.get('documentId')
            
            print(f"✅ Created new doc: {doc_title}")
            
            # Insert the processed content
            requests = [{
                'insertText': {
                    'location': {'index': 1},
                    'text': final_content
                }
            }]
            
            self.docs_service.documents().batchUpdate(
                documentId=new_doc_id,
                body={'requests': requests}
            ).execute()
            
            print("✅ Content inserted successfully!")
            
            # Share with team members
            if share_emails:
                self.share_document(new_doc_id, share_emails)
            
            # Get shareable link
            doc_url = f"https://docs.google.com/document/d/{new_doc_id}/edit"
            
            return {
                "success": True,
                "doc_id": new_doc_id,
                "doc_url": doc_url,
                "doc_title": doc_title,
                "message": f"Created templated blog assignment '{doc_title}' successfully! 📄✨",
                "used_template": True,
                "replacements_made": replacements_made
            }
            
        except Exception as e:
            print(f"❌ New template creation error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Failed to create new templated document: {e}"
            }
    
    def extract_text_from_doc(self, doc) -> str:
        """Extract plain text content from a Google Doc, including tables"""
        
        content = doc.get('body', {}).get('content', [])
        text_parts = []
        
        for element in content:
            # Handle regular paragraphs
            if 'paragraph' in element:
                paragraph = element['paragraph']
                if 'elements' in paragraph:
                    for para_element in paragraph['elements']:
                        if 'textRun' in para_element:
                            text_run = para_element['textRun']
                            text_content = text_run.get('content', '')
                            text_parts.append(text_content)
            
            # Handle tables - THIS IS THE KEY! 🔑
            elif 'table' in element:
                table = element['table']
                if 'tableRows' in table:
                    for row in table['tableRows']:
                        if 'tableCells' in row:
                            for cell in row['tableCells']:
                                if 'content' in cell:
                                    # Recursively extract text from cell content
                                    for cell_element in cell['content']:
                                        if 'paragraph' in cell_element:
                                            paragraph = cell_element['paragraph']
                                            if 'elements' in paragraph:
                                                for para_element in paragraph['elements']:
                                                    if 'textRun' in para_element:
                                                        text_run = para_element['textRun']
                                                        text_content = text_run.get('content', '')
                                                        text_parts.append(text_content)
                                # Add some spacing between cells
                                text_parts.append('\t')
                        # Add line break between rows
                        text_parts.append('\n')
        
        extracted_text = ''.join(text_parts)
        print(f"📄 Extracted text preview: {extracted_text[:200]}...")
        return extracted_text
    
    def create_simple_blog_assignment_doc(self, 
                                         content: Dict, 
                                         blog_topic: str,
                                         client_info: Dict = None,
                                         folder_id: str = None,
                                         share_emails: List[str] = None) -> Dict:
        """
        Create complete blog assignment doc (fallback method with FULL content)
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
            
            print(f"✅ Created complete Google Doc: {doc_title}")
            
            # Add COMPLETE content
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
                "message": f"Created complete blog assignment '{doc_title}' successfully!",
                "used_template": False
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create complete document: {e}"
            }
    
    def add_complete_content_to_doc(self, doc_id: str, content: Dict, blog_topic: str, client_info: Dict = None):
        """Add COMPLETE content to document - including ALL H1/H2/H3 structure!"""
        
        # Build complete content
        content_parts = []
        content_parts.append("🤖 JASPER'S BLOG ASSIGNMENT")
        content_parts.append("=" * 50)
        content_parts.append(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
        content_parts.append("")
        
        # Blog Topic
        content_parts.append("🎯 BLOG TOPIC")
        content_parts.append("-" * 20)
        content_parts.append(f"{blog_topic}")
        content_parts.append("")
        
        # Client Information
        if client_info:
            content_parts.append("🏥 CLIENT INFORMATION")
            content_parts.append("-" * 30)
            content_parts.append(f"Practice: {client_info.get('name', 'N/A')}")
            content_parts.append(f"Specialty: {client_info.get('specialty', 'N/A')}")
            content_parts.append(f"Location: {client_info.get('location', 'N/A')}")
            content_parts.append(f"Brand Voice: {client_info.get('brand_voice', 'Standard')}")
            content_parts.append(f"Target Audience: {client_info.get('target_audience', 'General patients')}")
            content_parts.append("")
        
        # SEO Assignment
        content_parts.append("📋 SEO ASSIGNMENT")
        content_parts.append("-" * 25)
        content_parts.append(f"Title: {content.get('title', 'N/A')}")
        content_parts.append(f"Meta Description: {content.get('meta', 'N/A')}")
        content_parts.append(f"Primary Keywords: {content.get('primaryKeywords', 'N/A')}")
        content_parts.append(f"Keywords: {', '.join(content.get('keywords', []))}")
        content_parts.append(f"Call-to-Action: {content.get('cta', 'N/A')}")
        content_parts.append(f"URL Slug: {content.get('url', 'N/A')}")
        content_parts.append("")
        
        # Resources
        content_parts.append("Resources:")
        for resource in content.get('resources', []):
            content_parts.append(f"• {resource}")
        content_parts.append("")
        
        # CONTENT STRUCTURE - THE IMPORTANT PART! 🎯
        content_parts.append("📝 CONTENT STRUCTURE")
        content_parts.append("-" * 30)
        content_parts.append(f"H1: {content.get('h1', 'N/A')}")
        content_parts.append("")
        
        # H2 Sections with full guidance
        for i, section in enumerate(content.get('h2Sections', []), 1):
            content_parts.append(f"H2: {section.get('heading', '')}")
            content_parts.append("Content Guidelines:")
            content_parts.append(f"{section.get('h3Content', '')}")
            content_parts.append("")
        
        # Jasper's Strategic Insights
        if content.get('jasperNotes'):
            content_parts.append("🤖 JASPER'S STRATEGIC INSIGHTS")
            content_parts.append("-" * 40)
            content_parts.append(f"{content.get('jasperNotes')}")
            content_parts.append("")
        
        # Footer
        content_parts.append("-" * 50)
        content_parts.append("Generated by Jasper 🤖 - Your AI SEO Assistant")
        content_parts.append("Ready to create amazing content!")
        
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
            print("✅ COMPLETE content added successfully!")
        except Exception as e:
            print(f"❌ Error adding complete content: {e}")
    
    def share_document(self, doc_id: str, email_addresses: List[str], role: str = 'writer'):
        """Share the document with specified email addresses"""
        try:
            for email in email_addresses:
                permission = {
                    'type': 'user',
                    'role': role,  # 'reader', 'writer', or 'owner'
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
        """
        Create a perfect template document that definitely works with Jasper
        """
        
        try:
            # Template content exactly as you specified
            template_content = """**Title:** <title-tag>
**Meta:** <meta-description>
**Primary Keywords:** <primary-keywords>
**Keywords:** <keywords>
**CTA:** <cta>
**Resources:**
<resources>

**Client Information:**
Practice: <client-name>
Specialty: <client-specialty>
Location: <client-location>
Brand Voice: <client-brand-voice>
Target Audience: <target-audience>

**Content Structure:**
[Content writers fill this section based on generated outline]

H1: 

H2: 

H2: 

H2: 

H2: 

**Notes:**
Generated by Jasper 🤖 - Your AI SEO Assistant
"""
            
            # Create new document
            doc_body = {
                'title': 'Jasper Blog Assignment Template - MASTER'
            }
            
            doc = self.docs_service.documents().create(body=doc_body).execute()
            doc_id = doc.get('documentId')
            
            print(f"✅ Created template document: {doc_id}")
            
            # Add template content
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
            
            print("✅ Template content added successfully!")
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            return {
                "success": True,
                "template_doc_id": doc_id,
                "template_url": doc_url,
                "message": f"Perfect template created! Copy this ID to your .env: JASPER_TEMPLATE_DOC_ID={doc_id}"
            }
            
        except Exception as e:
            print(f"❌ Error creating template: {e}")
            return {
                "success": False,
                "error": f"Failed to create template: {e}"
            }
    
    def create_content_folder(self, folder_name: str = "Jasper Blog Assignments") -> Optional[str]:
        """Create a dedicated folder for blog assignments"""
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            folder = self.drive_service.files().create(body=folder_metadata).execute()
            folder_id = folder.get('id')
            
            print(f"✅ Created folder: {folder_name}")
            return folder_id
            
        except Exception as e:
            print(f"❌ Error creating folder: {e}")
            return None
    
    def list_recent_assignments(self, folder_id: str = None, limit: int = 10) -> List[Dict]:
        """List recent blog assignment documents"""
        try:
            query = "name contains 'Blog Assignment'"
            if folder_id:
                query += f" and parents in '{folder_id}'"
            
            results = self.drive_service.files().list(
                q=query,
                orderBy='modifiedTime desc',
                pageSize=limit,
                fields="nextPageToken, files(id, name, webViewLink, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            return files
            
        except Exception as e:
            print(f"❌ Error listing documents: {e}")
            return []
    
    def test_connection(self) -> Dict:
        """Test Google Drive connection and permissions"""
        if not self.drive_service:
            return {
                "success": False,
                "error": "Google Drive service not initialized"
            }
        
        try:
            # Test by listing files
            results = self.drive_service.files().list(pageSize=1).execute()
            
            return {
                "success": True,
                "message": "Google Drive connection successful!",
                "can_create_docs": bool(self.docs_service),
                "user_email": self.creds.token if hasattr(self.creds, 'token') else "Unknown"
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
        print("📋 To use with Jasper:")
        print("1. Add CONTENT_TEAM_EMAILS to your .env file")
        print("2. Call create_blog_assignment_doc() with your content")
        print("3. Beautiful Google Doc created and shared automatically!")
    else:
        print("\n❌ Setup needed:")
        print("1. Download credentials.json from Google Cloud Console")
        print("2. Enable Google Drive and Docs APIs")
        print("3. Run this script to authenticate")