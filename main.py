# main.py - SEMUA LOGIC DALAM 1 FILE (FIXED VERSION)
import imaplib
import email
from email.header import decode_header
import time
import threading
import tkinter as tk
from tkinter import ttk
import sys
import os
import webbrowser

# Import config
from config import GMAIL_CONFIG, IMPORTANT_CONTACTS, URGENT_KEYWORDS

class EmailNotifier:
    def __init__(self):
        self.last_checked_uids = set()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup system tray icon (nanti kita tambah)"""
        print("🚀 Email Notifier AI Started...")
        print(f"📧 Monitoring: {GMAIL_CONFIG['email']}")
        print("⏰ Check interval: 40 seconds")
        print("💡 Popup duration: 5 seconds")
        print("──────────────────────────────")
        
    def create_popup(self, email_data):
        """Buat popup seperti WhatsApp/Discord di pojok kanan bawah"""
        popup = tk.Toplevel()
        popup.wm_overrideredirect(True)  # Remove window decorations
        popup.attributes('-topmost', True)  # Selalu di atas
        popup.configure(bg='#2d2d2d')  # Dark theme seperti Discord
        
        # Position di pojok kanan bawah
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        popup_width = 300
        popup_height = 120
        
        x_position = screen_width - popup_width - 20  # 20px dari kanan
        y_position = screen_height - popup_height - 50  # 50px dari bawah
        
        popup.geometry(f'{popup_width}x{popup_height}+{x_position}+{y_position}')
        
        # Determine priority color
        priority_color = '#ff6b6b' if email_data['priority'] == 'HIGH' else '#4ecdc4'
        
        # Email content frame
        content_frame = tk.Frame(popup, bg='#2d2d2d', padx=15, pady=10)
        content_frame.pack(fill='both', expand=True)
        
        # Priority badge
        priority_label = tk.Label(
            content_frame, 
            text=f"📧 {email_data['priority']} PRIORITY",
            fg=priority_color,
            bg='#2d2d2d',
            font=('Arial', 9, 'bold')
        )
        priority_label.pack(anchor='w')
        
        # Sender info
        sender_label = tk.Label(
            content_frame,
            text=f"From: {email_data['sender']}",
            fg='white',
            bg='#2d2d2d',
            font=('Arial', 9),
            wraplength=250
        )
        sender_label.pack(anchor='w', pady=(5, 0))
        
        # Subject
        subject_label = tk.Label(
            content_frame,
            text=f"Subject: {email_data['subject']}",
            fg='white',
            bg='#2d2d2d',
            font=('Arial', 8),
            wraplength=250
        )
        subject_label.pack(anchor='w', pady=(2, 0))
        
        # Click to view link
        def open_gmail():
            webbrowser.open('https://mail.google.com')
            popup.destroy()
            
        link_btn = tk.Label(
            content_frame,
            text="📩 Click to view in Gmail",
            fg='#7289da',
            bg='#2d2d2d',
            font=('Arial', 8, 'underline'),
            cursor='hand2'
        )
        link_btn.pack(anchor='w', pady=(8, 0))
        link_btn.bind('<Button-1>', lambda e: open_gmail())
        
        # Auto-close setelah beberapa detik
        popup.after(GMAIL_CONFIG['popup_duration'] * 1000, popup.destroy)
        
        # Hover effects
        def on_enter(e):
            if hasattr(popup, 'auto_close'):
                popup.after_cancel(popup.auto_close)  # Cancel auto-close saat hover
            
        def on_leave(e):
            popup.auto_close = popup.after(3000, popup.destroy)  # Close setelah 3 detik
            
        popup.auto_close = popup.after(GMAIL_CONFIG['popup_duration'] * 1000, popup.destroy)
        popup.bind('<Enter>', on_enter)
        popup.bind('<Leave>', on_leave)
        
        # Animate entrance - FIXED LINE!
        popup.attributes('-alpha', 0.0)  # Start transparent
        def fade_in():
            for i in range(1, 11):
                popup.attributes('-alpha', i/10)
                popup.update()
                time.sleep(0.02)
        
        # Run fade in animation
        popup.after(100, fade_in)
    
    def analyze_priority(self, sender, subject):
        """AI sederhana untuk deteksi priority email"""
        priority_score = 0
        
        # Check sender importance
        if any(contact in sender for contact in IMPORTANT_CONTACTS):
            priority_score += 3
            
        # Check urgent keywords
        subject_lower = subject.lower()
        if any(keyword in subject_lower for keyword in URGENT_KEYWORDS):
            priority_score += 2
            
        # Return priority level
        if priority_score >= 3:
            return 'HIGH'
        elif priority_score >= 1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def check_emails(self):
        """Smart email checking dengan connection management yang proper"""
        try:
            print(f"🔄 Checking emails at {time.strftime('%H:%M:%S')}...")
            
            # SETUP FRESH CONNECTION SETIAP KALI (ini kunci anti-restart!)
            mail = imaplib.IMAP4_SSL(GMAIL_CONFIG['imap_server'])
            mail.login(GMAIL_CONFIG['email'], GMAIL_CONFIG['app_password'])
            mail.select('inbox')
            
            # Search UNSEEN emails
            status, messages = mail.search(None, 'UNSEEN')
            email_ids = messages[0].split()
            
            current_uids = set(email_ids)
            new_uids = current_uids - self.last_checked_uids
            
            if new_uids:
                print(f"📨 Found {len(new_uids)} new email(s)")
                
                for email_id in new_uids:
                    # Fetch email data
                    status, msg_data = mail.fetch(email_id, '(RFC822)')
                    msg = email.message_from_bytes(msg_data[0][1])
                    
                    # Decode subject
                    subject, encoding = decode_header(msg['Subject'])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')
                    if subject is None:
                        subject = "No Subject"
                    
                    # Get sender
                    sender = msg['From'] or "Unknown Sender"
                    
                    # Analyze priority
                    priority = self.analyze_priority(sender, subject)
                    
                    # Prepare email data
                    email_data = {
                        'sender': sender,
                        'subject': subject,
                        'priority': priority,
                        'timestamp': time.strftime('%H:%M:%S')
                    }
                    
                    # Show popup di main thread
                    root.after(0, lambda ed=email_data: self.create_popup(ed))
                    
                    print(f"   📬 {priority} - From: {sender[:30]}...")
            
            self.last_checked_uids = current_uids
            
            # CLEANUP - Tutup koneksi dengan proper
            mail.close()
            mail.logout()
            print("✅ Check completed. Connection closed properly.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Retrying in 60 seconds...")
            time.sleep(60)  # Wait longer jika error
    
    def start_monitoring(self):
        """Start background monitoring dengan proper timing"""
        def monitoring_loop():
            while True:
                self.check_emails()
                
                # Cooldown period sebelum reconnect
                print(f"💤 Waiting {GMAIL_CONFIG['check_interval']} seconds...")
                print("──────────────────────────────")
                time.sleep(GMAIL_CONFIG['check_interval'])
        
        # Run di background thread
        monitor_thread = threading.Thread(target=monitoring_loop, daemon=True)
        monitor_thread.start()

# Setup main application
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    notifier = EmailNotifier()
    notifier.start_monitoring()
    
    print("🎯 Email Notifier AI is running in background!")
    print("💡 Close this window to stop the application")
    print("──────────────────────────────")
    
    # Keep the application running
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n👋 Shutting down Email Notifier AI...")
        sys.exit(0)