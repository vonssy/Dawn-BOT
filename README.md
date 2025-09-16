# 🌅 Dawn Validator BOT

> Automated Dawn Validator management with multi-threading and proxy support

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/vonssy/Dawn-BOT.svg)](https://github.com/vonssy/Dawn-BOT/stargazers)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Setup & Usage](#setup--usage)
- [Proxy Recommendation](#proxy-recommendation)
- [Support](#support)
- [Contributing](#contributing)

## 🎯 Overview

Dawn Validator BOT is an automated tool designed to manage Dawn Validator nodes efficiently with multi-threading support. It provides seamless proxy integration and automated keep-alive functionality to ensure optimal validator performance.

**🔗 Get Started:** [Register on Dawn Validator](https://dashboard.dawninternet.com/signup)

> **Referral Code:** Use code `02lt4r` during registration for benefits!

**📥 Extension:** [Download Chrome Extension](https://chromewebstore.google.com/detail/dawn-validator-chrome-ext/fpdkjdnhkakefebpekbdhillbhonfjjp?hl=en)

## ✨ Features

- 🤖 **Automated Token Extraction** - Auto-fetch bearer tokens using 2captcha
- 🔄 **Automated Account Management** - Retrieve account information automatically
- 🌐 **Flexible Proxy Support** - Run with or without proxy configuration
- 🔀 **Smart Proxy Rotation** - Automatic rotation of invalid proxies
- 💓 **Keep-Alive System** - Automated keep-alive signals every 10 minutes
- ⚡ **Multi-Threading Support** - Handle multiple accounts simultaneously
- 🤖 **2captcha Integration** - Optional captcha solving capability

## 📋 Requirements

- **Python:** Version 3.9 or higher
- **pip:** Latest version recommended
- **2captcha Key:** Optional (for automated captcha solving)

## 🛠 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vonssy/Dawn-BOT.git
cd Dawn-BOT
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# or for Python 3 specifically
pip3 install -r requirements.txt
```

## ⚙️ Configuration

### 2captcha Key Setup (Optional)

Create or edit `2captcha_key.txt` in the project directory:

```
your_2captcha_key
```

### Account Configuration

Create or edit `accounts.json` in the project directory:

```json
[
    {
        "Email": "your_email_address_1",
        "Password": "your_password_1"
    },
    {
        "Email": "your_email_address_2",
        "Password": "your_password_2"
    }
]
```

### Automatic Token Generation

The bot can automatically fetch tokens using your 2captcha key through the setup script. This eliminates the need for manual token extraction.

### Manual Token Setup (Alternative)

If you prefer to fetch tokens manually or don't have a 2captcha key, you can extract tokens from the Dawn Validator dashboard:

<div align="center">
  <img src="example.png" alt="Dawn Token Example" width="500">
  <p><em>Example of fetching bearer tokens manually from Dawn Validator dashboard</em></p>
</div>

Create or edit `tokens.json`:

```json
[
    {
        "Email": "your_email_address_1",
        "Token": "your_bearer_token_1"
    },
    {
        "Email": "your_email_address_2",
        "Token": "your_bearer_token_2"
    }
]
```

### Proxy Configuration (Optional)

Create or edit `proxy.txt` in the project directory:

```
# Simple format (HTTP protocol by default)
192.168.1.1:8080

# With protocol specification
http://192.168.1.1:8080
https://192.168.1.1:8080

# With authentication
http://username:password@192.168.1.1:8080
```

## 🚀 Setup & Usage

### Automatic Token Setup (Recommended)

Run the setup script to automatically fetch tokens using your configured 2captcha key and account credentials:

```bash
python setup.py
# or for Python 3 specifically
python3 setup.py
```

> **💡 What does setup.py do?**
> - Automatically logs in to your Dawn Validator accounts
> - Solves captchas using your 2captcha key
> - Extracts bearer tokens automatically
> - Saves tokens to `tokens.json` for the bot to use

### Start the Bot

After running the setup, launch the Dawn Validator BOT:

```bash
python bot.py
# or for Python 3 specifically
python3 bot.py
```

### Runtime Options

When starting the bot, you'll be prompted to choose:

1. **Proxy Mode Selection:**
   - Option `1`: Run with proxy
   - Option `2`: Run without proxy

2. **Auto-Rotation:** 
   - `y`: Enable automatic invalid proxy rotation
   - `n`: Disable auto-rotation

## 🌐 Proxy Recommendation

<div align="center">
  <img src="images/banner.png" alt="NST Proxy Banner" width="300">
</div>

For reliable multi-wallet automation and geo-restriction bypass, we recommend **Nstproxy**:

### Why Nstproxy?
- 💰 **Affordable pricing** starting from $0.1/GB
- 🌍 **Global coverage** with multiple locations
- 🔄 **Advanced rotation control**
- 🛡️ **Anti-ban technology**

### Get Started with Nstproxy
- 🔗 **Website:** [Nstproxy.com](https://www.nstproxy.com/?utm_source=vonssy)
- 💬 **Telegram:** [@nstproxy](https://t.me/nstproxy)
- 🎮 **Discord:** [Join Server](https://discord.gg/5jjWCAmvng)
- 📚 **GitHub:** [Nstproxy Repository](https://github.com/Nstproxy)

> 🎁 **Special Offer:** Use code `VONSSY` for **10% OFF** your first purchase!

## 💖 Support the Project

If this project has been helpful to you, consider supporting its development:

### Cryptocurrency Donations

| Network | Address |
|---------|---------|
| **EVM** | `0xe3c9ef9a39e9eb0582e5b147026cae524338521a` |
| **TON** | `UQBEFv58DC4FUrGqinBB5PAQS7TzXSm5c1Fn6nkiet8kmehB` |
| **SOL** | `E1xkaJYmAFEj28NPHKhjbf7GcvfdjKdvXju8d8AeSunf` |
| **SUI** | `0xa03726ecbbe00b31df6a61d7a59d02a7eedc39fe269532ceab97852a04cf3347` |

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

1. ⭐ **Star this repository** if you find it useful
2. 👥 **Follow** for updates on new features
3. 🐛 **Report issues** via GitHub Issues
4. 💡 **Suggest improvements** or new features
5. 🔧 **Submit pull requests** for bug fixes or enhancements

## 📞 Contact & Support

- **Developer:** vonssy
- **Issues:** [GitHub Issues](https://github.com/vonssy/Dawn-BOT/issues)
- **Discussions:** [GitHub Discussions](https://github.com/vonssy/Dawn-BOT/discussions)

---

<div align="center">

**Made with ❤️ by [vonssy](https://github.com/vonssy)**

*Thank you for using Dawn Validator BOT! Don't forget to ⭐ star this repository.*

</div>