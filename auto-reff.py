import random
import string
import json
import requests
from solders.keypair import Keypair
from solders.message import Message
from colorama import init, Fore, Style
import time

# Initialize colorama
init()

def print_success(message):
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message):
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_info(message):
    print(f"{Fore.CYAN}ℹ️ {message}{Style.RESET_ALL}")

def print_wait(message):
    print(f"{Fore.YELLOW}⏳ {message}{Style.RESET_ALL}")

def generate_random_username(length=16):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# def generate_wallet():
#     keypair = Keypair()
#     return keypair.public_key, keypair.secret_key, keypair

def generate_wallet():
    keypair = Keypair()  # Generate a new keypair
    return keypair.public(), keypair.secret()  # Use 'public()' to get the public key

def fetch_nonce(public_key):
    url = "https://solpot.com/api/auth/nonce"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
    }
    payload = {
        "publicKey": str(public_key)
    }
    
    print_wait("Fetching nonce from API...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('success') and 'data' in response_data:
                print_success("Nonce fetched successfully!")
                return response_data['data']['nonce']
            else:
                print_error(f"Invalid response structure: {response_data}")
                return None
    except Exception as e:
        print_error(f"Error fetching nonce: {str(e)}")
        return None

def sign_message(keypair, message):
    try:
        encoded_message = message.encode()
        signature = keypair.sign(encoded_message)
        # Convert signature bytes directly to list of integers
        return [int(b) for b in bytes(signature)]
    except Exception as e:
        print_error(f"Error signing message: {str(e)}")
        return None

def create_user(public_key, nonce, signature):
    url = "https://solpot.com/api/auth/create"
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0',
    }
    
    random_username = generate_random_username()
    
    payload = {
        "name": random_username,
        "tos": True,
        "referralCode": "ahst", 
        "nonce": nonce,
        "publicKey": str(public_key),
        "signature": signature  # This will be the array of integers
    }
    
    print_wait("Creating user account...")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('success'):
            print_success("User created successfully! 🎉")
            print_info(f"Username: {random_username}")
            # print_info(f"Response: {response.text}")
            return True
        else:
            error_msg = response_data.get('error', 'Unknown error')
            print_error(f"Failed to create user: {error_msg}")
            print_info(f"Response: {json.dumps(response_data, indent=2)}")
            return False
            
    except Exception as e:
        print_error(f"Error creating user: {str(e)}")
        return False

def main():
    try: 
        while True:
            # Generate wallet
            print_wait("Generating new wallet...")
            public_key, private_key, keypair = generate_wallet()
            print_success("Wallet generated successfully!")
            print_info(f"Public Key: {public_key}")
            
            # Save address and private key to result.txt
            with open("result.txt", "a") as file:  # 'a' for append mode
                file.write(f"{public_key} | {private_key.hex()}\n") 
            
            # Fetch nonce
            nonce = fetch_nonce(public_key)
            if nonce is None:
                continue
            
            print_info(f"Nonce: {nonce[:20]}...")
            
            # Prepare and sign message
            message = f"Welcome to SolPot!\nThis request will not trigger a blockchain transaction or cost any gas fees. \n\nWallet address: {public_key}\nNonce: {nonce}"
            
            print_wait("Signing message...")
            signature = sign_message(keypair, message)
            
            if signature is None:
                continue
            
            print_success("Message signed successfully!")
            
            # Create user
            if not create_user(public_key, nonce, signature):
                print_error("Failed to complete account creation.")
                continue
            
            print_success("Account creation process completed! 🎊\n\n")
            
            # Optional: Add a delay between each iteration to avoid overwhelming the system
            time.sleep(5)
        
    except KeyboardInterrupt:
        print_error("\nProcess interrupted by user.")
    except Exception as e:
        print_error(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        print_info("\nThank you for using Solpot Account Generator! 👋")
        time.sleep(2)

if __name__ == "__main__":
    main()
