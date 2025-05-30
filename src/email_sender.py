#!/usr/bin/env python3
"""
Standalone Email Sender Module
Email notification system for CFP Scout traditional mode
Supports both SMTP and Mailgun API
"""

import os
import platform
import tempfile
import subprocess
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
        # Email configuration
        self.to_email = os.getenv('TO_EMAIL')
        
        # Mailgun configuration (preferred)
        self.mailgun_api_key = os.getenv('MAILGUN_API_KEY')
        self.mailgun_domain = os.getenv('MAILGUN_DOMAIN') 
        self.mailgun_from_email = os.getenv('MAILGUN_FROM_EMAIL')
        
        # SMTP configuration (fallback)
        self.email_address = os.getenv('EMAIL_ADDRESS')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Display configuration
        self.show_external_terminal = os.getenv('SHOW_EXTERNAL_TERMINAL', 'true').lower() == 'true'
        
        # Determine which method to use
        self.use_mailgun = bool(self.mailgun_api_key and self.mailgun_domain)
        
        if not self.to_email:
            print("⚠️ Warning: TO_EMAIL not configured")
        
        if not self.use_mailgun and not all([self.email_address, self.email_password]):
            print("⚠️ Warning: Email configuration incomplete")
            print("   For Mailgun: Set MAILGUN_API_KEY, MAILGUN_DOMAIN, MAILGUN_FROM_EMAIL")
            print("   For SMTP: Set EMAIL_ADDRESS, EMAIL_PASSWORD")
        
        print(f"📧 Email Sender initialized")
        if self.use_mailgun:
            print(f"🚀 Using Mailgun API (domain: {self.mailgun_domain})")
        else:
            print(f"📨 Using SMTP ({self.smtp_server}:{self.smtp_port})")
    
    def _display_email_preview(self, subject: str, text_content: str, events: List[Dict]) -> None:
        """Display email content in terminal for preview"""
        print("\n" + "="*80)
        print("📧 EMAIL PREVIEW")
        print("="*80)
        print(f"📤 From: {self.mailgun_from_email if self.use_mailgun else self.email_address}")
        print(f"📥 To: {self.to_email}")
        print(f"📝 Subject: {subject}")
        print("="*80)
        
        # Display summary
        print(f"\n🎯 SUMMARY:")
        print(f"📊 Found {len(events)} relevant CFP events")
        print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Display events in a nice table format
        print(f"\n📋 CFP EVENTS:")
        print("-" * 80)
        
        for i, event in enumerate(events, 1):
            relevance_score = event.get('relevance_score', 0)
            score_emoji = "🟢" if relevance_score >= 0.8 else "🟡" if relevance_score >= 0.6 else "🔴"
            
            print(f"\n{i:2}. {event.get('title', 'Unknown Event')}")
            print(f"    📍 Location: {event.get('location', 'Unknown')}")
            print(f"    ⏰ Deadline: {event.get('cfp_deadline', 'Unknown')}")
            print(f"    🔗 Link: {event.get('link', 'No link')}")
            print(f"    {score_emoji} Relevance: {relevance_score:.2f}/1.0")
            
            if event.get('tags'):
                tags_str = ', '.join(event.get('tags', [])[:5])  # Show first 5 tags
                print(f"    🏷️  Topics: {tags_str}")
            
            if event.get('description'):
                description = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                print(f"    📄 Description: {description}")
        
        print("\n" + "="*80)
        print("🤖 This is the content that would be sent via email")
        print("="*80)
    
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
    
    def _launch_external_terminal(self, subject: str, content: str, events: List[Dict]) -> bool:
        """Launch external terminal window to display email content"""
        try:
            # Create a temporary script file with the email content
            script_content = f'''#!/bin/bash

# Clear the terminal
clear

# Display beautiful email preview
echo "╔══════════════════════════════════════════════════════════════════════════════════════╗"
echo "║                               📧 CFP SCOUT EMAIL PREVIEW                            ║" 
echo "╚══════════════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📤 From: CFP Scout <noreply@sandbox123.mailgun.org>"
echo "📥 To: {self.to_email}"
echo "📝 Subject: {subject}"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════════════╗"
echo "║                                   🎯 SUMMARY                                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════════╝"
echo "📊 Found {len(events)} relevant CFP events"
echo "⏰ Generated: $(date)"
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════════════╗"
echo "║                               📋 CFP EVENTS                                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════════════════╝"
'''
            
            # Add each event with beautiful formatting
            for i, event in enumerate(events, 1):
                relevance = event.get('relevance_score', 0)
                # Choose emoji based on relevance score
                if relevance >= 0.8:
                    relevance_emoji = "🟢"
                elif relevance >= 0.6:
                    relevance_emoji = "🟡"
                else:
                    relevance_emoji = "🔴"
                
                tags_str = ", ".join(event.get('tags', []))
                
                script_content += f'''
echo ""
echo "────────────────────────────────────────────────────────────────────────────────────────"
echo ""
echo "{i:2d}. {event.get('title', 'Unknown Event')}"
echo "    📍 Location: {event.get('location', 'Unknown')}"
echo "    ⏰ Deadline: {event.get('cfp_deadline', 'Unknown')}"
echo "    🔗 Link: {event.get('link', 'No link available')}"
echo "    {relevance_emoji} Relevance: {relevance:.2f}/1.0"'''
                
                if tags_str:
                    script_content += f'''
echo "    🏷️  Topics: {tags_str}"'''
                
                if event.get('description'):
                    description = event['description'][:100] + "..." if len(event['description']) > 100 else event['description']
                    script_content += f'''
echo "    📄 Description: {description}"'''
            
            script_content += f'''

echo ""
echo "════════════════════════════════════════════════════════════════════════════════════════"
echo "🤖 This is the content that would be sent via email"
echo "════════════════════════════════════════════════════════════════════════════════════════"
echo ""
echo "💡 This terminal window shows your CFP Scout email preview!"
echo "   You can keep this window open for reference while working."
echo ""
echo "Press any key to close this window..."
read -n 1
'''
            
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as tmp_file:
                tmp_file.write(script_content)
                script_path = tmp_file.name
            
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Launch new terminal window based on OS
            system = platform.system().lower()
            
            if system == 'darwin':  # macOS
                # Use osascript to open new Terminal window
                applescript = f'''
                tell application "Terminal"
                    do script "{script_path}"
                    activate
                end tell
                '''
                subprocess.run(['osascript', '-e', applescript], check=False)
                print("🚀 External terminal launched with email preview!")
                return True
                
            elif system == 'linux':
                # Try different terminal emulators
                terminals = ['gnome-terminal', 'konsole', 'xterm', 'terminal']
                for terminal in terminals:
                    try:
                        if terminal == 'gnome-terminal':
                            subprocess.Popen([terminal, '--', 'bash', script_path])
                        elif terminal == 'konsole':
                            subprocess.Popen([terminal, '-e', 'bash', script_path])
                        else:
                            subprocess.Popen([terminal, '-e', f'bash {script_path}'])
                        print(f"🚀 External terminal ({terminal}) launched with email preview!")
                        return True
                    except FileNotFoundError:
                        continue
                        
            elif system == 'windows':
                # Windows command prompt
                subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k', f'bash {script_path}'])
                print("🚀 External terminal launched with email preview!")
                return True
            
            print("⚠️ Could not detect compatible terminal emulator")
            return False
            
        except Exception as e:
            print(f"⚠️ Could not launch external terminal: {e}")
            return False
    
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
            
            # Display email preview in terminal
            self._display_email_preview(subject, text_content, events)
            
            # Try to send email
            if self.use_mailgun:
                print("\n📧 Sending email via Mailgun...")
                success = self._send_via_mailgun(subject, html_content, text_content)
            else:
                print("\n📧 Sending email via SMTP...")
                success = self._send_via_smtp(subject, html_content, text_content)
            
            if not success:
                print("\n💡 Don't worry! The email content above shows what would be sent.")
                print("   Once email is configured, this same content will be delivered.")
            
            # Launch external terminal if enabled
            if self.show_external_terminal:
                self._launch_external_terminal(subject, html_content, events)
            
            return success
            
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
            'title': 'AI & Machine Learning Summit 2025',
            'location': 'San Francisco, CA',
            'cfp_deadline': '2025-06-15',
            'link': 'https://example.com/ai-summit-cfp',
            'relevance_score': 0.95,
            'tags': ['AI', 'Machine Learning', 'Deep Learning', 'NLP'],
            'description': 'Join the premier AI conference featuring cutting-edge research, industry applications, and networking opportunities with leading experts in artificial intelligence and machine learning.'
        },
        {
            'title': 'DevOps World Conference',
            'location': 'Online',
            'cfp_deadline': '2025-07-01',
            'link': 'https://example.com/devops-world-cfp',
            'relevance_score': 0.78,
            'tags': ['DevOps', 'Cloud Computing', 'Infrastructure', 'Automation'],
            'description': 'Learn about the latest DevOps practices, cloud infrastructure, and automation tools from industry leaders and practitioners.'
        },
        {
            'title': 'FinTech Innovation Forum',
            'location': 'London, UK',
            'cfp_deadline': '2025-05-30',
            'link': 'https://example.com/fintech-forum-cfp',
            'relevance_score': 0.82,
            'tags': ['FinTech', 'Blockchain', 'Digital Banking', 'Innovation'],
            'description': 'Explore the future of financial technology with blockchain innovations, digital banking solutions, and regulatory insights.'
        }
    ]
    
    print("\n🧪 Testing email sending with sample events...")
    success = send_cfp_email(test_events)
    if success:
        print("✅ Email test successful!")
    else:
        print("❌ Email sending failed - but preview shown above") 