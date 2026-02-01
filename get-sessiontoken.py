import aiohttp
import asyncio
import json
import os

# 1. Configuration
API_URL = "https://api.dawninternet.com/auth"

# REMOVED 'br' from Accept-Encoding to prevent 'Please install Brotli' error
HEADERS_BASE = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate", 
    "Content-Type": "application/json",
    "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
}

async def exchange_token(account):
    email = account.get("email")
    privy_token = account.get("privyToken")
    
    print(f"[*] Exchanging token for: {email}...")
    
    if not privy_token:
        print(f"[!] No privyToken found for {email}")
        return account

    # Prepare request
    headers = HEADERS_BASE.copy()
    headers["X-Privy-Token"] = privy_token
    
    params = {
        "jwt": "true",
        "role": "extension"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    new_session_token = data.get("token") or data.get("session_token")
                    
                    if new_session_token:
                        print(f"[SUCCESS] Got new Session Token!")
                        account["sessionToken"] = new_session_token
                    else:
                        print(f"[ERROR] Response did not contain a token: {data}")
                else:
                    print(f"[FAIL] HTTP {response.status}: {await response.text()}")
    except Exception as e:
        print(f"[ERROR] Exception occurred: {e}")
        
    return account

async def main():
    filename = "tokens.json"
    
    if not os.path.exists(filename):
        print("tokens.json not found!")
        return

    # Load existing tokens
    try:
        with open(filename, 'r') as f:
            accounts = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not read tokens.json: {e}")
        return

    # Process each account
    new_accounts = []
    if isinstance(accounts, list):
        for acc in accounts:
            updated_acc = await exchange_token(acc)
            new_accounts.append(updated_acc)
    else:
        print("tokens.json format is incorrect (should be a list)")
        return

    # Save back to file
    with open(filename, 'w') as f:
        json.dump(new_accounts, f, indent=4)
    
    print("\n[DONE] tokens.json has been updated with valid earning tokens.")

if __name__ == "__main__":
    asyncio.run(main())
