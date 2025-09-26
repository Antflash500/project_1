# config.py - Ganti dengan data kamu
GMAIL_CONFIG = {
    'email': 'email kamu',  # Ganti dengan emailmu
    'app_password': 'code 16 digit',  # Ganti dengan app password
    'imap_server': 'imap.gmail.com',
    'check_interval': 40,  # Detik antara setiap check cycle
    'popup_duration': 5,   # Detik popup tampil
}

# List kontak penting untuk priority detection
IMPORTANT_CONTACTS = [
    'boosku@perusahaan.com',
    'contoh@gmail.com'
]

# Keywords untuk detect email urgent
URGENT_KEYWORDS = ['cepat', 'asap', 'important', 'meeting', 'deadline']