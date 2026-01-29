from aiohttp import (
    ClientResponseError, 
    ClientSession, 
    ClientTimeout, 
    BasicAuth
)
from aiohttp_socks import ProxyConnector
from datetime import datetime, timezone
from colorama import *
import asyncio, json, pytz, re, os

wib = pytz.timezone('Asia/Jakarta')

class Dawn:
    def __init__(self) -> None:
        self.BASE_API = "https://api.dawninternet.com"
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.sessions = {}
        self.ua_index = 0
        self.accounts = {}
        
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
    
    def load_accounts(self):
        filename = "tokens.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            print(f"{Fore.RED + Style.BRIGHT}Failed To Load Accounts: {e}{Style.RESET_ALL}")
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
        
    def get_next_user_agent(self):
        ua = self.USER_AGENTS[self.ua_index]
        self.ua_index = (self.ua_index + 1) % len(self.USER_AGENTS)
        return ua

    def initialize_headers(self, email: str):
        if email not in self.HEADERS:
            self.HEADERS[email] = {
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Authorization": f"Bearer {self.accounts[email]['session_token']}",
                "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                "Pragma": "no-cache",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "cross-site",
                "User-Agent": self.get_next_user_agent()
            }

        return self.HEADERS[email].copy()
    
    def get_session(self, email: str, proxy_url=None, timeout=60):
        if email not in self.sessions:
            connector, proxy, proxy_auth = self.build_proxy_config(proxy_url)
            
            session = ClientSession(
                connector=connector,
                timeout=ClientTimeout(total=timeout)
            )
            
            self.sessions[email] = {
                'session': session,
                'proxy': proxy,
                'proxy_auth': proxy_auth
            }
        
        return self.sessions[email]
    
    async def recreate_session_with_new_proxy(self, email: str, proxy_url: str):
        if email in self.sessions:
            old_session = self.sessions[email]["session"]
            if not old_session.closed:
                await old_session.close()
            del self.sessions[email]

        return self.get_session(email, proxy_url)
    
    def print_message(self, email, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

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

    async def check_connection(self, email: str, proxy_url=None):
        url = "https://api.ipify.org?format=json"
        
        try:
            session_info = self.get_session(email, proxy_url, 15)
            session = session_info["session"]
            proxy = session_info["proxy"]
            proxy_auth = session_info["proxy_auth"]

            async with session.get(
                url=url, proxy=proxy, proxy_auth=proxy_auth
            ) as response:
                response.raise_for_status()
                return True
        except (Exception, ClientResponseError) as e:
            self.print_message(
                email, 
                self.display_proxy(proxy_url), 
                Fore.RED, 
                f"Connection Not 200 OK: {Fore.YELLOW+Style.BRIGHT}{str(e)}"
            )
            return None
        
    async def user_point(self, email: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/point"
        headers = self.initialize_headers(email)
        params = {
            "user_id": self.accounts[email]["user_id"]
        }
        
        for attempt in range(retries):
            try:
                session_info = self.get_session(email, proxy_url)
                session = session_info["session"]
                proxy = session_info["proxy"]
                proxy_auth = session_info["proxy_auth"]

                async with session.get(
                    url=url, headers=headers, params=params, proxy=proxy, proxy_auth=proxy_auth
                ) as response:
                    if response.status == 401:
                        self.print_message(email, proxy, Fore.RED, f"GET Earning Failed: {Fore.YELLOW+Style.BRIGHT}Token Already Expired")
                        return None
                    response.raise_for_status()
                    return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(
                    email, 
                    self.display_proxy(proxy_url), 
                    Fore.RED, 
                    f"GET Earning Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}"
                )

        return None

    async def extension_ping(self, email: str, timestamp: str, proxy_url=None, retries=5):
        url = f"{self.BASE_API}/ping"
        headers = self.initialize_headers(email)
        headers["Content-Type"] = "application/json"
        params = {
            "role": "extension"
        }
        payload = {
            "user_id": self.accounts[email]["user_id"], 
            "extension_id": "fpdkjdnhkakefebpekbdhillbhonfjjp", 
            "timestamp": timestamp
        }
        for attempt in range(retries):
            try:
                session_info = self.get_session(email, proxy_url)
                session = session_info["session"]
                proxy = session_info["proxy"]
                proxy_auth = session_info["proxy_auth"]

                async with session.post(
                    url=url, headers=headers, params=params, json=payload, proxy=proxy, proxy_auth=proxy_auth
                ) as response:
                        
                    if response.status == 401:
                        self.print_message(email, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}Token Already Expired")
                        return None
                    elif response.status == 429:
                        self.print_message(email, proxy, Fore.RED, f"PING Failed: {Fore.YELLOW+Style.BRIGHT}Too Many Request")
                        return None
                    
                    response.raise_for_status()
                    return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(
                    email, 
                    self.display_proxy(proxy_url), 
                    Fore.RED, 
                    f"PING Failed: {Fore.YELLOW+Style.BRIGHT}{str(e)}"
                )

        return None

    async def process_check_connection(self, email: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(email)

            is_valid = await self.check_connection(email, proxy_url)
            if is_valid: return True
            
            if self.ROTATE_PROXY:
                proxy_url = self.rotate_proxy_for_account(email)
                await self.recreate_session_with_new_proxy(email, proxy_url)
                
            await asyncio.sleep(1)
            
    async def process_user_earning(self, email: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(email)

            user = await self.user_point(email, proxy_url)
            if user:
                node_points = user.get("points", 0)
                referral_points = user.get("referral_points", 0)
                total_points = node_points + referral_points
                
                self.print_message(
                    email, 
                    self.display_proxy(proxy_url), 
                    Fore.WHITE, 
                    f"Earning {total_points} PTS"
                )

            await asyncio.sleep(10 * 60) 

    async def process_send_keepalive(self, email: str, proxy_url=None):
        while True:
            if self.USE_PROXY:
                proxy_url = self.get_next_proxy_for_account(email)

            await asyncio.sleep(3)

            timestamp = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

            keepalive = await self.extension_ping(email, timestamp, proxy_url)
            if keepalive:
                message = keepalive.get("message")

                self.print_message(
                    email, 
                    self.display_proxy(proxy_url), 
                    Fore.GREEN, 
                    "PING Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Message: {Style.RESET_ALL}"
                    f"{Fore.BLUE + Style.BRIGHT}{message}{Style.RESET_ALL}"
                )

            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For 20 Minutes For Next Sent Ping...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            
            await asyncio.sleep(20 * 60)
        
    async def process_accounts(self, email: str):
        is_valid = await self.process_check_connection(email)
        if is_valid:
            tasks = [
                asyncio.create_task(self.process_user_earning(email)),
                asyncio.create_task(self.process_send_keepalive(email))
            ]
            await asyncio.gather(*tasks)
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts: return
            
            self.print_question()
            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if self.USE_PROXY: self.load_proxies()

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = []
            for idx, account in enumerate(accounts, start=1):
                email = account.get("email")
                user_id = account.get("userId")
                privy_token = account.get("privyToken")
                session_token = account.get("sessionToken")

                if not "@" in email or not user_id or not privy_token or not session_token:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}[ Account: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                        f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
                        f"{Fore.RED + Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                    )
                    continue

                self.accounts[email] = {
                    "user_id": user_id,
                    "privy_token": privy_token,
                    "session_token": session_token,
                }

                tasks.append(asyncio.create_task(self.process_accounts(email)))

            await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e
        finally:
            for s in self.sessions.values():
                if not s["session"].closed:
                    await s["session"].close()

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