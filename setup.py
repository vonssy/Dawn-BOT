from aiohttp import ClientResponseError, ClientSession, ClientTimeout, BasicAuth
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, uuid, json, pytz, re, os

wib = pytz.timezone('Asia/Jakarta')

class Dawn:
    def __init__(self) -> None:
        self.BASE_API = "https://api.dawninternet.com"
        self.PRIVY_API = "https://auth.privy.io/api/v1"
        self.REF_CODE = "VCDXB2W3" # U can change it with yours
        self.BASE_HEADERS = {}
        self.PRIVY_HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def log_status(self, action, status, message="", error=None):
        if status == "success":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Action :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {action} {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Success {Style.RESET_ALL}"
                f"{(Fore.MAGENTA+Style.BRIGHT + '- ' + Style.RESET_ALL + Fore.WHITE+Style.BRIGHT + message + Style.RESET_ALL) if message else ''}"
            )
        elif status == "failed":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Action :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {action} {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(error)} {Style.RESET_ALL}"
            )
        elif status == "retry":
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Action :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {action} {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Retrying {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {message} {Style.RESET_ALL}"
            )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Dawn {Fore.BLUE + Style.BRIGHT}Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        
    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

            self.log_status("Save Tokens", "success", "Tokens saved to file")

        except Exception as e:
            self.log_status("Save Tokens", "failed", error=e)
            return []
        
    async def load_proxies(self):
        filename = "proxy.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                return
            with open(filename, 'r') as f:
                self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, account):
        if account not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[account] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def build_proxy_config(self, proxy=None):
        if not proxy:
            return None, None, None

        if proxy.startswith("socks"):
            connector = ProxyConnector.from_url(proxy)
            return connector, None, None

        elif proxy.startswith("http"):
            match = re.match(r"http://(.*?):(.*?)@(.*)", proxy)
            if match:
                username, password, host_port = match.groups()
                clean_url = f"http://{host_port}"
                auth = BasicAuth(username, password)
                return None, clean_url, auth
            else:
                return None, proxy, None

        raise Exception("Unsupported Proxy Type.")
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run Without Proxy{Style.RESET_ALL}")
                proxy_choice = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                if proxy_choice in [1, 2]:
                    proxy_type = (
                        "With" if proxy_choice == 1 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1  or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1  or 2).{Style.RESET_ALL}")

        rotate_proxy = False
        if proxy_choice == 1:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    rotate_proxy = rotate_proxy == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return proxy_choice, rotate_proxy
    
    async def check_connection(self, proxy_url=None):
        connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=10)) as session:
                async with session.get(url="https://api.ipify.org?format=json", proxy=proxy, proxy_auth=proxy_auth) as response:
                    response.raise_for_status()
                    self.log_status("Check Connection", "success", "Connection OK")
                    return True
        except (Exception, ClientResponseError) as e:
            self.log_status("Check Connection", "failed", error=e)
            return None
        
    async def request_otp(self, email: str, proxy_url=None, retries=5):
        url = f"{self.PRIVY_API}/passwordless/init"
        data = json.dumps({"email": email})
        headers = {
            **self.PRIVY_HEADERS[email],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()
                        self.log_status("Request OTP", "success", "OTP request sent")
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    self.log_status("Request OTP", "retry", f"Attempt {attempt + 1}/{retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    self.log_status("Request OTP", "failed", error=e)
                    return None
        
    async def authenticate_otp(self, email: str, otp_code: str, proxy_url=None, retries=5):
        url = f"{self.PRIVY_API}/passwordless/authenticate"
        data = json.dumps({"email": email, "code": otp_code, "mode": "login-or-sign-up"})
        headers = {
            **self.PRIVY_HEADERS[email],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()
                        self.log_status("Authenticate OTP", "success", "OTP verified successfully")
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    self.log_status("Authenticate OTP", "retry", f"Attempt {attempt + 1}/{retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    self.log_status("Authenticate OTP", "failed", error=e)
                    return None
        
    async def auth_jwt(self, email: str, privy_token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/auth?jwt=true&role=extension"
        headers = {
            **self.BASE_HEADERS[email],
            "X-Privy-Token": privy_token
        }
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, proxy=proxy, proxy_auth=proxy_auth) as response:
                        response.raise_for_status()
                        result = await response.json()
                        self.log_status("JWT Authentication", "success", "JWT token obtained")
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    self.log_status("JWT Authentication", "retry", f"Attempt {attempt + 1}/{retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    self.log_status("JWT Authentication", "failed", error=e)
                    return None
        
    async def use_referral(self, email: str, session_token: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/referral/use"
        data = json.dumps({"referralCode":self.REF_CODE})
        headers = {
            **self.BASE_HEADERS[email],
            "Authorization": f"Bearer {session_token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        
        for attempt in range(retries):
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, data=data, proxy=proxy, proxy_auth=proxy_auth) as response:
                        if response.status == 400: return None
                        response.raise_for_status()
                        result = await response.json()
                        return result
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                else:
                    return None

    async def process_check_connection(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy if proxy else 'No Proxy'} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if is_valid: return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)
                await asyncio.sleep(1)
                continue

            return False

    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(email, use_proxy, rotate_proxy)
        if not is_valid:
            self.log_status("Process Account", "failed", error="Connection check failed")
            return

        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        request = await self.request_otp(email, proxy)
        if not request: return

        timestamp = (
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Action :{Style.RESET_ALL}"
        )
        otp_code = input(f"{timestamp}{Fore.BLUE + Style.BRIGHT} Enter OTP Code -> {Style.RESET_ALL}")

        authenticate = await self.authenticate_otp(email, otp_code, proxy)
        if not authenticate: return

        privy_token = authenticate.get("token")
        if not privy_token:
            self.log_status("Process Account", "failed", error="No token received from authentication")
            return

        auth_jwt = await self.auth_jwt(email, privy_token, proxy)
        if not auth_jwt: return

        user_id = auth_jwt.get("user", {}).get("id")
        session_token = auth_jwt.get("session_token")

        if user_id and session_token:
            await self.use_referral(email, session_token, proxy)
            account_data = [{"email": email, "userId": user_id, "sessionToken": session_token}]
            self.save_tokens(account_data)
            self.log_status("Process Account", "success", f"Account {self.mask_account(email)} processed successfully")
        else:
            self.log_status("Process Account", "failed", error="Invalid response data")
    
    async def main(self):
        try:
            with open('emails.txt', 'r') as file:
                emails = [line.strip() for line in file if line.strip()]

            proxy_choice, rotate_proxy = self.print_question()

            self.clear_terminal()
            self.welcome()

            use_proxy = True if proxy_choice == 1 else False
            if use_proxy:
                await self.load_proxies()

            separator = "=" * 27
            for idx, email in enumerate(emails, start=1):
                if "@" not in email:
                    self.log_status("Email Validation", "failed", error="Invalid email format")
                    continue

                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {len(emails)} {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                )

                user_agent = FakeUserAgent().random

                self.BASE_HEADERS[email] = {
                    "Accept": "*/*",
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "User-Agent": user_agent
                }

                self.PRIVY_HEADERS[email] = {
                    "Accept": "application/json",
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                    "Privy-App-Id": "cmfb724md0057la0bs4tg0vf1",
                    "Privy-Ca-Id": str(uuid.uuid4()),
                    "Privy-Client": "react-auth:2.24.0",
                    "Privy-Ui": "t",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-Storage-Access": "active",
                    "User-Agent": user_agent
                }

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Email  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                )

                await self.process_accounts(email, use_proxy, rotate_proxy)
                await asyncio.sleep(3)

        except FileNotFoundError:
            self.log_status("File Loading", "failed", error="File 'emails.txt' not found")
            return
        except Exception as e:
            self.log_status("Main Process", "failed", error=e)
            raise e

if __name__ == "__main__":
    try:
        bot = Dawn()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Dawn - BOT{Style.RESET_ALL}                                      ",                                       
        )