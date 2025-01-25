import os
import sys
import time
from datetime import datetime, timezone
import json
import requests
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama
init()

# Emojis for better visual feedback
EMOJI = {
    "rocket": "🚀",
    "check": "✅",
    "error": "❌", 
    "warn": "⚠️",
    "info": "ℹ️",
    "time": "⏰",
    "cycle": "🔄",
    "user": "👤",
    "box": "📦",
    "phone": "📱"
}

# API Configuration
API_URL = "https://solpot.com"
API_ENDPOINTS = {
    "profile": "/api/profile/info",
    "daily_case": "/api/daily-case/open"
}

# Default headers
HEADERS = {
    "authority": "solpot.com",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://solpot.com",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/131.0.0.0",
    "referer": "https://solpot.com/",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"'
}

class Logger:
    """Handles all logging with colors and emojis"""
    
    @staticmethod
    def info(msg):
        print(f"{EMOJI['info']} {Fore.CYAN}{msg}{Style.RESET_ALL}")
    
    @staticmethod
    def success(msg):
        print(f"{EMOJI['check']} {Fore.GREEN}{msg}{Style.RESET_ALL}")
    
    @staticmethod
    def error(msg):
        print(f"{EMOJI['error']} {Fore.RED}{msg}{Style.RESET_ALL}")
    
    @staticmethod
    def warn(msg):
        print(f"{EMOJI['warn']} {Fore.YELLOW}{msg}{Style.RESET_ALL}")
    
    @staticmethod
    def profile(msg):
        print(f"{EMOJI['user']} {Fore.MAGENTA}{msg}{Style.RESET_ALL}")
def countdown(seconds, message="Time remaining"):
    """Display countdown timer"""
    for remaining in range(seconds, 0, -1):
        sys.stdout.write(f"\r{EMOJI['time']} {Fore.YELLOW}{message}: ")
        sys.stdout.write(f"{Fore.CYAN}{datetime.fromtimestamp(remaining, timezone.utc).strftime('%H:%M:%S')}")
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.flush()
        time.sleep(1)
    print("\r" + " " * 70 + "\r", end="")

def parse_cookie_string(cookie_string):
    """Parse cookie string into a dictionary"""
    cookie_dict = {}
    items = cookie_string.strip().split(';')
    for item in items:
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookie_dict[name.strip()] = value.strip()
    return cookie_dict

def load_accounts():
    """Load accounts from data.txt file"""
    try:
        with open("data.txt", "r") as file:
            accounts = [line.strip() for line in file if line.strip()]
        
        if not accounts:
            Logger.error("No accounts found in data.txt")
            sys.exit(1)
            
        return accounts
    
    except Exception as e:
        Logger.error(f"Failed to read data.txt: {str(e)}")
        sys.exit(1)

def create_session(cookie_string):
    """Create requests session with proper cookie handling"""
    session = requests.Session()
    session.headers.update(HEADERS)
    
    # Parse and set cookies properly
    cookies = parse_cookie_string(cookie_string)
    for name, value in cookies.items():
        session.cookies.set(name, value, domain="solpot.com")
    
    return session

def check_profile(session, account_num):
    """Check account profile"""
    try:
        response = session.post(f"{API_URL}{API_ENDPOINTS['profile']}")
        data = response.json()
        
        if data["success"]:
            Logger.profile(f"Account {account_num} Profile:")
            Logger.info(f"Telegram: {data['data']['telegram']['username']}") 
            return True
            
        Logger.error(f"Account {account_num} - Profile check failed: {data.get('error', 'Unknown error')}")
        return False
        
    except Exception as e:
        Logger.error(f"Account {account_num} - Profile error: {str(e)}")
        return False

def open_daily_case(session, account_num):
    """Try to open daily case"""
    try:
        response = session.post(f"{API_URL}{API_ENDPOINTS['daily_case']}", json={"demo": False})
        data = response.json()
        
        if data["success"]:
            Logger.success(f"Account {account_num} - Daily case opened!")
            Logger.info(f"{EMOJI['box']} Target Block: {data['data']['targetBlock']}")
            return True
            
        if "once per day" in str(data.get("error", "")).lower():
            Logger.info(f"Case already claimed today\n")
            return True
            
        Logger.error(f"Account {account_num} - Failed to open case: {data.get('error', 'Unknown error')}")
        return False
        
    except Exception as e:
        Logger.error(f"Account {account_num} - Case error: {str(e)}")
        return False

def process_account(cookie, index, total):
    """Process a single account"""
    account_num = f"{index + 1}/{total}"
    
    session = create_session(cookie)
    
    if not check_profile(session, account_num):
        return False
        
    if not open_daily_case(session, account_num):
        return False
        
    return True

def main():
    """Main program loop"""
    Logger.info("""Starting Solpot automation...
░▀▀█░█▀█░▀█▀░█▀█
░▄▀░░█▀█░░█░░█░█
░▀▀▀░▀░▀░▀▀▀░▀░▀
╔══════════════════════════════════╗
║                                  ║
║  ZAIN ARAIN                      ║
║  AUTO SCRIPT MASTER              ║
║                                  ║
║  JOIN TELEGRAM CHANNEL NOW!      ║
║  https://t.me/AirdropScript6     ║
║  @AirdropScript6 - OFFICIAL      ║
║  CHANNEL                         ║
║                                  ║
║  FAST - RELIABLE - SECURE        ║
║  SCRIPTS EXPERT                  ║
║                                  ║
╚══════════════════════════════════╝""")
    
    try:
        while True:
            accounts = load_accounts()
            Logger.info(f"Loaded {len(accounts)} accounts\n")
            
            # Process each account
            for i, cookie in enumerate(accounts): 
                process_account(cookie, i, len(accounts))
                
                # Delay between accounts
                if i < len(accounts) - 1:
                    countdown(5, "Next account in")
            
            Logger.success(f"{EMOJI['check']} Cycle completed!")
            Logger.info("Waiting for next cycle...")
            countdown(24 * 60 * 60, "Next cycle in")
            
    except KeyboardInterrupt:
        Logger.warn("Shutting down...")
        sys.exit(0)
        
    except Exception as e:
        Logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()