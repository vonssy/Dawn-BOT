from aiohttp import (
    ClientResponseError, 
    ClientSession, 
    ClientTimeout, 
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, uuid, json, pytz, re, os

wib = pytz.timezone('Asia/Jakarta')

class Dawn:
    def __init__(self) -> None:
        self.API_URL = {
            "dawn": "https://api.dawninternet.com",
            "privy": "https://auth.privy.io",
        }
        self.CAPTCHA = {
            "solver_api": "https://api.2captcha.com",
            "site_key": "0x4AAAAAAAM8ceq5KhP1uJBt",
            "page_url": "https://dashboard.dawninternet.com"
        }
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        
        self.USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36 Edg/129.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/117.0.0.0"
        ]

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
        
    def load_emails(self):
        filename = "emails.txt"
        try:
            with open(filename, 'r') as file:
                emails = [line.strip() for line in file if line.strip()]
            return emails
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Emails: {e}{Style.RESET_ALL}")
            return None
        
    def load_captcha_key(self):
        filename = "captcha_key.txt"
        try:
            with open(filename, 'r') as file:
                captcha_key = file.readline().strip()
            return captcha_key
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Captcha Key: {e}{Style.RESET_ALL}")
            return None

    def load_proxies(self):
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
    
    def display_proxy(self, proxy_url=None):
        if not proxy_url: return "No Proxy"

        proxy_url = re.sub(r"^(http|https|socks4|socks5)://", "", proxy_url)

        if "@" in proxy_url:
            proxy_url = proxy_url.split("@", 1)[1]

        return proxy_url
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def initialize_headers(self, email: str, header_type: str):
        if email not in self.HEADERS:
            self.HEADERS[email] = {}

        if "ua" not in self.HEADERS[email]:
            self.HEADERS[email]["ua"] = random.choice(self.USER_AGENTS)

        ua = self.HEADERS[email]["ua"]

        if header_type not in self.HEADERS[email]:

            base_headers = {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "User-Agent": ua
            }

            if header_type == "privy":
                headers = {
                    **base_headers,
                    "Accept": "application/json",
                    "Privy-App-Id": "cmfb724md0057la0bs4tg0vf1",
                    "Privy-Ca-Id": str(uuid.uuid4()),
                    "Privy-Client": "react-auth:3.10.0-beta-20251223041507",
                    "Sec-Fetch-Site": "none",
                }

            elif header_type == "dawn":
                headers = {
                    **base_headers,
                    "Accept": "application/json, text/plain, */*",
                    "Sec-Fetch-Site": "cross-site",
                }

            self.HEADERS[email][header_type] = headers

        return self.HEADERS[email][header_type].copy()

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
                    self.USE_PROXY = True if proxy_choice == 1 else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1  or 2.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1  or 2).{Style.RESET_ALL}")

        if self.USE_PROXY:
            while True:
                rotate_proxy = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate_proxy in ["y", "n"]:
                    self.ROTATE_PROXY = True if rotate_proxy == "y" else False
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")
    
    async def enusre_ok(self, response):
        if response.status >= 400 or response.status < 500:
            raise Exception(f"HTTP: {response.status}:{await response.text()}")
        
    async def check_connection(self, proxy_url=None):
        url = "https://api.ipify.org?format=json"
        
        try:
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=15)) as session:
                async with session.get(url=url, proxy=proxy, proxy_auth=proxy_auth) as response:
                    await self.enusre_ok(response)
                    self.log_status("Check Connection", "success", "Connection OK")
                    return True
        except (Exception, ClientResponseError) as e:
            self.log_status("Check Connection", "failed", error=e)
            return None
        
    async def solve_turnstile(self, proxy_url=None, max_attempts: int = 30):
        try:
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)

            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:

                create_url = f"{self.CAPTCHA['solver_api']}/createTask"
                create_payload = {
                    "clientKey": self.captcha_key,
                    "task": {
                        "type": "TurnstileTaskProxyless",
                        "websiteURL": self.CAPTCHA["page_url"],
                        "websiteKey": self.CAPTCHA["site_key"],
                    }
                }

                async with session.post(url=create_url, json=create_payload, proxy=proxy, proxy_auth=proxy_auth) as r1:
                    r1.raise_for_status()
                    res_text1 = await r1.text()

                    res_json1 = json.loads(res_text1)
                    if res_json1.get("errorId") != 0:
                        self.log_status("Captcha", "failed", error={res_json1.get('errorDescription')})
                        return None

                    task_id = res_json1.get("taskId")
                    self.log_status("Captcha", "success", f"Task Id: {task_id}")

                    result_url = f"{self.CAPTCHA['solver_api']}/getTaskResult"
                    result_payload = {
                        "clientKey": self.captcha_key,
                        "taskId": task_id
                    }

                    for attempt in range(max_attempts):
                        await asyncio.sleep(3)

                        async with session.post(url=result_url, json=result_payload, proxy=proxy, proxy_auth=proxy_auth) as r2:
                            r2.raise_for_status()
                            res_text2 = await r2.text()

                            res_json2 = json.loads(res_text2)
                            if res_json2.get("errorId") != 0:
                                self.log_status("Captcha", "failed", error={res_json2.get('errorDescription')})
                                return None

                            status = res_json2.get("status")
                            if status == "ready":
                                turnstile_token = res_json2.get("solution", {}).get("token")
                                self.log_status("Captcha", "success", "Turnstile token obtained")
                                return turnstile_token
                            if status == "processing":
                                self.log_status("Captcha", "retry", f"Attempt {attempt + 1}/{max_attempts}")
                                continue

                self.log_status("Captcha", "failed", "Timeout")
                return None

        except Exception as e:
            self.log_status("Captcha", "failed", error=e)
            return None
        
    async def request_otp(self, email: str, turnstile_token: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['privy']}/api/v1/passwordless/init"
        headers = self.initialize_headers(email, "privy")
        headers["Content-Type"] = "application/json"
        payload = {
            "email": email,
            "token": turnstile_token,
        }
        
        for attempt in range(retries):
            try:
                connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        self.log_status("Request OTP", "success", "OTP request sent")
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    self.log_status("Request OTP", "retry", f"Attempt {attempt + 1}/{retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    self.log_status("Request OTP", "failed", error=e)
                    return None
        
    async def authenticate_otp(self, email: str, otp_code: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['privy']}/api/v1/passwordless/authenticate"
        headers = self.initialize_headers(email, "privy")
        headers["Content-Type"] = "application/json"
        payload = {
            "email": email,
            "code": otp_code,
            "mode": "login-or-sign-up"
        }
        
        for attempt in range(retries):
            try:
                connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.post(url=url, headers=headers, json=payload, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        self.log_status("Authenticate OTP", "success", "OTP verified successfully")
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    self.log_status("Authenticate OTP", "retry", f"Attempt {attempt + 1}/{retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    self.log_status("Authenticate OTP", "failed", error=e)
                    return None
        
    async def auth_jwt(self, email: str, privy_token: str, proxy_url=None, retries=5):
        url = f"{self.API_URL['dawn']}/auth"
        headers = self.initialize_headers(email, "dawn")
        headers["X-Privy-Token"] = privy_token
        params = {
            "jwt": "true",
            "role": "extension"
        }
        
        for attempt in range(retries):
            try:
                connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, params=params, proxy=proxy, proxy_auth=proxy_auth) as response:
                        await self.enusre_ok(response)
                        response.raise_for_status()
                        self.log_status("JWT Authentication", "success", "JWT token obtained")
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    self.log_status("JWT Authentication", "retry", f"Attempt {attempt + 1}/{retries}")
                    await asyncio.sleep(5)
                    continue
                else:
                    self.log_status("JWT Authentication", "failed", error=e)
                    return None
        
    async def process_check_connection(self, email: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(email)

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {self.display_proxy(proxy_url)} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy_url)
            if is_valid: return True
            
            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(email)
                await asyncio.sleep(1)
                continue

            return False

    async def process_accounts(self, email: str, proxy_url=None):
        is_valid = await self.process_check_connection(email, proxy_url)
        if not is_valid:
            self.log_status("Process Account", "failed", error="Connection check failed")
            return
        
        if self.USE_PROXY:
            proxy_url = self.get_next_proxy_for_account(email)

        turnstile_token = await self.solve_turnstile()
        if not turnstile_token: return

        request = await self.request_otp(email, turnstile_token, proxy_url)
        if not request: return

        timestamp = (
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Action :{Style.RESET_ALL}"
        )
        otp_code = input(f"{timestamp}{Fore.BLUE + Style.BRIGHT} Enter OTP Code -> {Style.RESET_ALL}").strip()

        authenticate = await self.authenticate_otp(email, otp_code, proxy_url)
        if not authenticate: return

        privy_token = authenticate.get("token")
        if not privy_token:
            self.log_status("Process Account", "failed", error="No token received from authentication")
            return

        auth_jwt = await self.auth_jwt(email, privy_token, proxy_url)
        if not auth_jwt: return

        user_id = auth_jwt.get("user", {}).get("id")
        session_token = auth_jwt.get("session_token")

        if user_id and session_token:
            self.save_tokens([{
                "email": email, 
                "userId": user_id, 
                "privyToken": privy_token, 
                "sessionToken": session_token
            }])

            self.log_status("Process Account", "success", f"Account {self.mask_account(email)} processed successfully")
        else:
            self.log_status("Process Account", "failed", error="Invalid response data")
    
    async def main(self):
        try:
            emails = self.load_emails()
            if not emails: return

            self.captcha_key = self.load_captcha_key()
            if not self.captcha_key: return

            self.print_question()
            self.clear_terminal()
            self.welcome()

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(emails)}{Style.RESET_ALL}"
            )

            if self.USE_PROXY: self.load_proxies()

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

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Email  :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                )

                await self.process_accounts(email)
                await asyncio.sleep(random.uniform(2.0, 3.0))

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