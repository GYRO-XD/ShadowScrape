🕷️ ShadowScrape - Short & Advanced README

```markdown
<div align="center">

# 🕷️ SHADOWSCRAPE

```

╔═══════════════════════════════════════════════════════════════╗
║  ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░  ║
║  ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░  ║
║  ░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░  ║
║                                                                 ║
║     ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗     ║
║     ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║     ║
║     ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║     ║
║     ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║     ║
║     ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝     ║
║     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝      ║
║                                                                 ║
║              STEALTH WEB SCRAPING FRAMEWORK                      ║
║                       v4.0 | 200+ AGENTS                        ║
╚═══════════════════════════════════════════════════════════════╝

```

**[![Version](https://img.shields.io/badge/version-4.0.0-blue?style=flat-square&logo=github)](https://github.com/GYRO-XD/shadowscrape)
[![Python](https://img.shields.io/badge/python-3.8+-green?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/GYRO-XD/shadowscrape?style=social)](https://github.com/GYRO-XD/shadowscrape)**

```

🔥 "Stealth is not just an option, it's a necessity."

```

</div>

---

## ⚡ Features

| Category | Features |
|----------|----------|
| **🕷️ Core** | 200+ User Agents • Random Selector • Stealth Mode • Multi-Threaded |
| **📊 Extraction** | Emails • Phones • Social Links • Metadata • Images |
| **💾 Export** | JSON • CSV • SQLite • Report Generation |
| **🎯 Categories** | Windows • Mac • Linux • Android • iOS • Chrome • Firefox • Edge • Opera |
| **🛡️ Stealth** | Auto-Rotation • Random Delays • Browser Headers • Anti-Detection |

---

## 🚀 Quick Start

```bash
# Clone & Install
git clone https://github.com/GYRO-XD/shadowscrape.git
cd shadowscrape && pip install -r requirements.txt

# Run
python shadowscrape.py
```

One-Liner Usage

```python
from shadowscrape import ShadowScrape
s = ShadowScrape()
data = s.scrape_page('https://example.com', category='chrome')
s.export_json('data.json')
```

---

🎮 Menu

```
┌─────────────────────────────────────────┐
│  [1]  Scrape Single URL                 │
│  [2]  Scrape Multiple URLs              │
│  [3]  Crawl Website                     │
│  [4]  Search Emails                     │
│  [5]  Search Social Links               │
│  [6]  Search Phones                     │
│  [7]  Export Results                    │
│  [8]  View Results                      │
│  [9]  Show User Agents                  │
│  [10] Save/Load Agent Database          │
│  [11] Toggle Agent Rotation             │
│  [12] Exit                              │
└─────────────────────────────────────────┘
```

---

📦 User Agent Categories

```
🖥️ Windows  │ Chrome 120-100, Firefox 121-106, Edge, Opera
🍎 Mac      │ Chrome 120-113, Firefox 121-115, Safari 17.2
🐧 Linux    │ Chrome 120-115, Firefox 121-120
📱 Android  │ Chrome 120-118, Firefox 121-117, Samsung
📲 iOS      │ Safari 17.2-16.4, Chrome 120-118
🤖 Bots     │ Googlebot, Bingbot, YandexBot
```

---

📊 Output Example

```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "emails": ["admin@example.com"],
  "phones": ["+1-555-555-5555"],
  "social": {"twitter": ["https://twitter.com/example"]}
}
```

---

🛠️ Advanced Usage

```python
# Crawl website
results = s.crawl_website(
    'https://example.com',
    max_pages=100,
    max_depth=3,
    threads=5,
    category='firefox'
)

# Batch scrape
urls = ['url1', 'url2', 'url3']
s.batch_scrape(urls, threads=3)

# Search data
emails = s.search_emails()
social = s.search_social()
phones = s.search_phones()
```

---

📂 File Structure

```
shadowscrape/
├── shadowscrape.py      # Main tool
├── user_agents.py       # Agent database
├── user_agents.json     # JSON version
├── requirements.txt     # Dependencies
└── README.md           # This file
```

---

🔧 Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.11.0
rich>=13.0.0
lxml>=4.9.0
```

---

🛡️ Ethical Use

```
✅ Respect robots.txt        ❌ No malicious use
✅ Get permission            ❌ No spam harvesting
✅ Educational use only      ❌ No unauthorized access
```

---

📈 Stats

<p align="center">
  <img src="https://img.shields.io/github/repo-size/GYRO-XD/shadowscrape?style=flat-square">
  <img src="https://img.shields.io/github/last-commit/GYRO-XD/shadowscrape?style=flat-square">
  <img src="https://img.shields.io/github/commit-activity/m/GYRO-XD/shadowscrape?style=flat-square">
</p>

---

👨‍💻 Author

GYRO-XD

· GitHub: @GYRO-XD
· Project: ShadowScrape

---

<div align="center">

```
 "Stay hidden, stay silent, stay dangerous."
```

Made with ❤️ by GYRO-XD

⬆ Back to Top

</div>
```

---
