from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime, timezone
from colorama import *
import asyncio, json, os, pytz, uuid

wib = pytz.timezone('Asia/Jakarta')

class Dawn:
    def __init__(self) -> None:
        self.BASE_API = "https://ext-api.dawninternet.com"
        self.VERSION = "1.2.2"
        self.CAPTCHA_KEY = None
        self.HEADERS = {}
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.password = {}
        self.app_id = {}

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
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
        
    def save_tokens(self, new_accounts):
        filename = "tokens.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, 'r') as file:
                    existing_accounts = json.load(file)
            else:
                existing_accounts = []

            account_dict = {acc["Email"]: acc for acc in existing_accounts}

            for new_acc in new_accounts:
                account_dict[new_acc["Email"]] = new_acc

            updated_accounts = list(account_dict.values())

            with open(filename, 'w') as file:
                json.dump(updated_accounts, file, indent=4)

        except Exception as e:
            return []
        
    def load_2captcha_key(self):
        try:
            with open("2captcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://raw.githubusercontent.com/monosans/proxy-list/refs/heads/main/proxies/all.txt")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
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
            
    def generate_app_id(self):
        prefix = "67"
        app_id = prefix + uuid.uuid4().hex[len(prefix):]
        return app_id
    
    def generate_login_payload(self, email: str, puzzle_id: str, answer: str):
        try:
            current_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace("+00:00", "Z")

            payload = {
                "username":email,
                "password":self.password[email],
                "logindata":{
                    "_v":{ "version":self.VERSION },
                    "datetime":current_time
                },
                "puzzle_id":puzzle_id,
                "ans":answer,
                "appid":self.app_id[email]
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()
                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        url = "https://api.ipify.org?format=json"
        proxies = {"http":proxy, "https":proxy} if proxy else None
        try:
            response = await asyncio.to_thread(requests.get, url=url, proxies=proxies, timeout=30, impersonate="chrome110", verify=False)
            response.raise_for_status()
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN + Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.RED + Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
                f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW + Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
    
    async def solve_recaptcha(self, puzzle_image: str, retries=5):
        for attempt in range(retries):
            try:
                if self.CAPTCHA_KEY is None:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT} Status  : {Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT}Image to Text Captcha Not Solved{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}2Captcha Key Is None{Style.RESET_ALL}"
                    )
                    return None
                
                response = await asyncio.to_thread(requests.post, "https://2captcha.com/in.php", json={
                    "key": self.CAPTCHA_KEY,
                    "method": "base64",
                    "body": puzzle_image,
                    "json": 1
                })

                response.raise_for_status()
                result = response.json()

                if result.get("status") != 1:
                    err_text = result.get("error_text", "Unknown Error")

                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT} Message : {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}{err_text}{Style.RESET_ALL}"
                    )
                    await asyncio.sleep(5)
                    continue

                request_id = result.get("request")
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Req Id  : {Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT}{request_id}{Style.RESET_ALL}"
                )

                for _ in range(30):
                    res_response = await asyncio.to_thread(requests.get, "https://2captcha.com/res.php", params={
                        "key": self.CAPTCHA_KEY,
                        "action": "get",
                        "id": request_id,
                        "json": 1
                    })

                    res_response.raise_for_status()
                    res_result = res_response.json()

                    if res_result.get("status") == 1:
                        answer = res_result["request"]

                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Status  : {Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT}Image to Text Captcha Solved Successfully{Style.RESET_ALL}"
                        )
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Answer  : {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{answer}{Style.RESET_ALL}"
                        )
                        return answer
                    elif res_result.get("request") == "CAPCHA_NOT_READY":
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} Message : {Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT}Captcha Not Ready{Style.RESET_ALL}"
                        )
                        await asyncio.sleep(5)
                        continue
                    else:
                        break

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Image to Text Captcha Not Solved{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                return None

    async def get_puzzle_id(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/chromeapi/dawn/v1/puzzle/get-puzzle?appid={self.app_id[email]}"
        headers = self.HEADERS[email].copy()
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch PuzzleId Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                return None

    async def get_puzzle_image(self, email: str, puzzle_id: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/chromeapi/dawn/v1/puzzle/get-puzzle-image?puzzle_id={puzzle_id}&appid={self.app_id[email]}"
        headers = self.HEADERS[email].copy()
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.get, url=url, headers=headers, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Message : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Fetch ImageB64 Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                return None

    async def user_login(self, email: str, puzzle_id: str, answer: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/chromeapi/dawn/v1/user/login/v2?appid={self.app_id[email]}"
        data = json.dumps(self.generate_login_payload(email, puzzle_id, answer))
        headers = self.HEADERS[email].copy()
        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] ="application/json"
        for attempt in range(retries):
            proxies = {"http":proxy, "https":proxy} if proxy else None
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxies=proxies, timeout=60, impersonate="chrome110", verify=False)
                if response.status_code == 400:
                    msg = response.json().get("message", "Unknown error (400)")
                    raise Exception(f"HTTP 400 Bad Request: {msg}")

                response.raise_for_status()
                return response.json()
            except Exception as e:
                if isinstance(e, Exception) and 'HTTP 400 Bad Request' in str(e):
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT} Status  : {Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT}Login Failed{Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                    )
                    return None
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT} Status  : {Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT}Login Failed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )
                return None
            
    async def process_check_connection(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if is_valid:
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)
                continue

            return False

    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(email, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            while True:
                self.log(f"{Fore.CYAN+Style.BRIGHT}Puzzle :{Style.RESET_ALL}")

                get_puzzle = await self.get_puzzle_id(email, proxy)
                if isinstance(get_puzzle, dict) and get_puzzle.get("success"):
                    puzzle_id = get_puzzle["puzzle_id"]

                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT} PuzzleId: {Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT}{puzzle_id}{Style.RESET_ALL}"
                    )

                    get_image = await self.get_puzzle_image(email, puzzle_id, proxy)
                    if isinstance(get_image, dict) and get_image.get("success"):
                        puzzle_image = get_image["imgBase64"]

                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.CYAN+Style.BRIGHT} ImageB64: {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{puzzle_image[:32]}...{Style.RESET_ALL}"
                        )

                        self.log(f"{Fore.CYAN+Style.BRIGHT}Captcha:{Style.RESET_ALL}")
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} Solving Image to Text Captcha... {Style.RESET_ALL}"
                        )

                        answer = await self.solve_recaptcha(puzzle_image)
                        if not answer:
                            continue

                        login = await self.user_login(email, puzzle_id, answer, proxy)
                        if isinstance(login, dict) and login.get("success"):
                            token = login["data"]["token"]

                            self.save_tokens([{"Email":email, "Token":token}])

                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT}   >{Style.RESET_ALL}"
                                f"{Fore.CYAN+Style.BRIGHT} Status  : {Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT}Token Have Been Saved Successfully{Style.RESET_ALL}"
                            )
                            break
                    
                await asyncio.sleep(5)
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            captcha_key = self.load_2captcha_key()
            if captcha_key:
                self.CAPTCHA_KEY = captcha_key
            
            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            separator = "=" * 27
            for idx, account in enumerate(accounts, start=1):
                if account:
                    self.log(
                        f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                    )

                    email = account["Email"]
                    password = account["Password"]

                    if not "@" in email or not password:
                        self.log(
                            f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                        )
                        continue

                    self.HEADERS[email] = {
                        "Accept": "*/*",
                        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "cross-site",
                        "User-Agent": FakeUserAgent().random
                    }

                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Email  :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {self.mask_account(email)} {Style.RESET_ALL}"
                    )

                    self.password[email] = password
                    self.app_id[email] = self.generate_app_id()

                    await self.process_accounts(email, use_proxy, rotate_proxy)
                    await asyncio.sleep(3)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
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