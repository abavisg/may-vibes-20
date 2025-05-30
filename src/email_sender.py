#!/usr/bin/env python3
"""
Standalone Email Sender Module
Email notification system for CFP Scout traditional mode
Supports both SMTP and Mailgun API
"""

import os
import smtplib
import requests
from typing import List, Dict, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailSender:
    """Email sender for CFP notifications with Mailgun and SMTP support"""
    
    def __init__(self):
        # Mailgun settings (preferred for production)
        self.mailgun_api_key = os.getenv('MAILGUN_API_KEY')
        self.mailgun_domain = os.getenv('MAILGUN_DOMAIN')
        self.mailgun_from_email = os.getenv('MAILGUN_FROM_EMAIL')
        
        # SMTP settings (fallback)
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # Common settings
        self.to_email = os.getenv('TO_EMAIL')
        
        # Determine which method to use
        self.use_mailgun = bool(self.mailgun_api_key and self.mailgun_domain and self.mailgun_from_email)
        
        if not self.to_email:
            print("⚠️ Warning: TO_EMAIL not configured")
        
        if not self.use_mailgun and not all([self.email_address, self.email_password]):
            print("⚠️ Warning: Email configuration incomplete")
            print("   For Mailgun: Set MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_FROM_EMAIL")
            print("   For SMTP: Set EMAIL_ADDRESS, EMAIL_PASSWORD")
    
    def _send_via_mailgun(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email via Mailgun API"""
        try:
            response = requests.post(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages",
                auth=("api", self.mailgun_api_key),
                data={
                    "from": self.mailgun_from_email,
                    "to": [self.to_email],
                    "subject": subject,
                    "text": text_content,
                    "html": html_content
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Email sent successfully via Mailgun to {self.to_email}")
                return True
            else:
                print(f"❌ Mailgun API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Mailgun sending failed: {e}")
            return False
    
    def _send_via_smtp(self, subject: str, html_content: str, text_content: str) -> bool:
        """Send email via SMTP"""
        try:
            if not all([self.email_address, self.email_password]):
                print("⚠️ SMTP configuration incomplete - skipping email sending")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_address
            msg['To'] = self.to_email
            
            # Attach parts
            text_part = MIMEText(text_content, 'plain')
            html_part = MIMEText(html_content, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully via SMTP to {self.to_email}")
            return True
            
        except Exception as e:
            print(f"❌ SMTP sending failed: {e}")
            return False
    
    def _test_smtp_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_address, self.email_password)
                return True
        except Exception as e:
            print(f"SMTP connection failed: {e}")
            return False
    
    def _test_mailgun_connection(self) -> bool:
        """Test Mailgun API connection"""
        try:
            response = requests.get(
                f"https://api.mailgun.net/v3/{self.mailgun_domain}",
                auth=("api", self.mailgun_api_key)
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Mailgun connection failed: {e}")
            return False
    
    def _format_events_html(self, events: List[Dict]) -> str:
        """Format events as HTML email content"""
        if not events:
            return "<p>No relevant CFP events found.</p>"
        
        html = """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background-color: #4CAF50; color: white; padding: 20px; text-align: center; }
                .event { border: 1px solid #ddd; margin: 15px 0; padding: 15px; border-radius: 5px; }
                .event-title { font-size: 18px; font-weight: bold; color: #2E7D32; margin-bottom: 10px; }
                .event-meta { color: #666; font-size: 14px; margin: 5px 0; }
                .event-tags { margin: 10px 0; }
                .tag { background-color: #E8F5E8; color: #2E7D32; padding: 2px 8px; border-radius: 3px; margin-right: 5px; font-size: 12px; }
                .deadline { color: #D32F2F; font-weight: bold; }
                .relevance { background-color: #FFF3E0; padding: 5px; border-radius: 3px; margin: 5px 0; }
                .footer { margin-top: 30px; padding: 20px; background-color: #f5f5f5; text-align: center; font-size: 12px; color: #666; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📢 CFP Scout Daily Report</h1>
                <p>Your personalized conference CFP recommendations</p>
            </div>
        """
        
        html += f"<p><strong>Found {len(events)} relevant CFP events for you:</strong></p>"
        
        for i, event in enumerate(events, 1):
            relevance_score = event.get('relevance_score', 0)
            relevance_color = "#4CAF50" if relevance_score >= 0.8 else "#FF9800" if relevance_score >= 0.6 else "#F44336"
            
            html += f"""
            <div class="event">
                <div class="event-title">{i}. {event.get('title', 'Unknown Event')}</div>
                <div class="event-meta">📍 <strong>Location:</strong> {event.get('location', 'Unknown')}</div>
                <div class="event-meta deadline">⏰ <strong>CFP Deadline:</strong> {event.get('cfp_deadline', 'Unknown')}</div>
                <div class="event-meta">🔗 <strong>Link:</strong> <a href="{event.get('link', '#')}">{event.get('link', 'No link available')}</a></div>
                <div class="relevance" style="border-left: 4px solid {relevance_color};">
                    <strong>Relevance Score:</strong> {relevance_score:.2f}/1.0
                </div>
            """
            
            if event.get('tags'):
                html += '<div class="event-tags"><strong>Topics:</strong> '
                for tag in event.get('tags', []):
                    html += f'<span class="tag">{tag}</span>'
                html += '</div>'
            
            if event.get('description'):
                description = event['description'][:200] + "..." if len(event['description']) > 200 else event['description']
                html += f'<div class="event-meta"><strong>Description:</strong> {description}</div>'
            
            html += '</div>'
        
        html += f"""
            <div class="footer">
                <p>🤖 Generated by CFP Scout using Ollama AI • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>This email was automatically generated based on your interests in AI, machine learning, engineering leadership, and more.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_cfp_email(self, events: List[Dict]) -> bool:
        """Send CFP events via email - supports both Mailgun and SMTP"""
        try:
            if not self.to_email:
                print("⚠️ TO_EMAIL not configured - skipping email sending")
                return False
            
            # Prepare email content
            subject = f"📢 CFP Scout: {len(events)} Relevant Conference CFPs Found"
            html_content = self._format_events_html(events)
            
            # Create plain text content
            text_content = f"CFP Scout Daily Report\n{'='*50}\n\n"
            text_content += f"Found {len(events)} relevant CFP events:\n\n"
            
            for i, event in enumerate(events, 1):
                text_content += f"{i}. {event.get('title', 'Unknown Event')}\n"
                text_content += f"   Location: {event.get('location', 'Unknown')}\n"
                text_content += f"   Deadline: {event.get('cfp_deadline', 'Unknown')}\n"
                text_content += f"   Link: {event.get('link', 'No link')}\n"
                text_content += f"   Relevance: {event.get('relevance_score', 0):.2f}/1.0\n\n"
            
            text_content += f"\nGenerated by CFP Scout • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Try Mailgun first (preferred), then fallback to SMTP
            if self.use_mailgun:
                print("📧 Sending email via Mailgun...")
                return self._send_via_mailgun(subject, html_content, text_content)
            else:
                print("📧 Sending email via SMTP...")
                return self._send_via_smtp(subject, html_content, text_content)
            
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False

# Global instance for easy access
_email_sender = EmailSender()

def send_cfp_email(events: List[Dict]) -> bool:
    """
    Main function interface for sending CFP emails
    This is the function that event_orchestrator.py expects
    
    Args:
        events: List of event dictionaries
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    return _email_sender.send_cfp_email(events)

def test_email_configuration() -> None:
    """Test email configuration and connectivity"""
    print("🧪 Testing Email Configuration...")
    print(f"📧 TO_EMAIL: {_email_sender.to_email}")
    
    if _email_sender.use_mailgun:
        print("🚀 Using Mailgun API")
        print(f"📧 Mailgun Domain: {_email_sender.mailgun_domain}")
        print(f"📧 From Email: {_email_sender.mailgun_from_email}")
        print(f"🔑 API Key: {'*' * 20 if _email_sender.mailgun_api_key else 'Not set'}")
        
        if _email_sender._test_mailgun_connection():
            print("✅ Mailgun connection successful")
        else:
            print("❌ Mailgun connection failed")
    else:
        print("📨 Using SMTP")
        print(f"📧 SMTP Server: {_email_sender.smtp_server}:{_email_sender.smtp_port}")
        print(f"📧 Email Address: {_email_sender.email_address}")
        
        if _email_sender.email_address and _email_sender.email_password:
            if _email_sender._test_smtp_connection():
                print("✅ SMTP connection successful")
            else:
                print("❌ SMTP connection failed")
        else:
            print("⚠️ SMTP credentials not configured")

if __name__ == "__main__":
    # Test the email configuration
    test_email_configuration()
    
    # Test sending an email
    test_events = [
        {
            'title': 'Test Conference',
            'location': 'Online',
            'cfp_deadline': '2025-06-01',
            'link': 'https://example.com',
            'relevance_score': 0.85,
            'tags': ['AI', 'Machine Learning'],
            'description': 'A test conference for CFP Scout email testing'
        }
    ]
    
    print("\n🧪 Testing email sending...")
    success = send_cfp_email(test_events)
    if success:
        print("✅ Email test successful!")
    else:
        print("❌ Email test failed - check your configuration") 