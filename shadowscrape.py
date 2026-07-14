#!/usr/bin/env python3
"""
ShadowScrape v4.0 - Ultimate Stealth Web Scraping Framework
User agents loaded from separate file for easy updates
Author: GYRO-XD
GitHub: https://github.com/GYRO-XD/shadowscrape
"""

import requests
import json
import os
import sys
import time
import re
import csv
import sqlite3
import random
import threading
import queue
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from bs4 import BeautifulSoup

# Import user agent database from separate file
from user_agents import user_agent_db, UserAgentDB

console = Console()

class ShadowScrape:
    """Stealth Web Scraping Framework with Separated User Agents"""
    
    def __init__(self):
        self.version = "4.0.0"
        self.author = "GYRO-XD"
        self.ua_db = user_agent_db
        self.session = requests.Session()
        self.results = []
        self.visited_urls = set()
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.start_time = datetime.now()
        self.delay_min = 0.5
        self.delay_max = 2.0
        self.rotate_on_every_request = True
        
        # Try to load from JSON (if exists)
        self.ua_db.load_from_json("user_agents.json")
        
        # Create directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("agents", exist_ok=True)
        
        # Set initial user agent
        self.session.headers.update({'User-Agent': self.ua_db.get_random()})
        
    def banner(self):
        """Display framework banner"""
        banner_text = """
╔═══════════════════════════════════════════════╗
║                                               ║
║   ███████╗██╗  ██╗ █████╗ ██████╗ ██████╗    ║
║   ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗   ║
║   ███████╗███████║███████║██║  ██║██████╔╝   ║
║   ╚════██║██╔══██║██╔══██║██║  ██║██╔══██╗   ║
║   ███████║██║  ██║██║  ██║██████╔╝██║  ██║   ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝   ║
║                                               ║
║         Ultimate Stealth Scraper v4.0         ║
║         Author: {}                         ║
║         User Agents: {}                     ║
║         Rotating: {}                       ║
║                                               ║
╚═══════════════════════════════════════════════╝
""".format(self.author, self.ua_db.count(), 
           "ON" if self.rotate_on_every_request else "OFF")
        console.print(Panel(banner_text, style="bold cyan"))
    
    def get_random_headers(self, category=None):
        """Get random headers with user agent"""
        if category:
            ua = self.ua_db.get_by_category(category)
        else:
            ua = self.ua_db.get_random()
        
        headers = {
            'User-Agent': ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-US,en;q=0.9,fr;q=0.8']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Add platform-specific headers
        if 'Windows' in ua:
            headers['sec-ch-ua-platform'] = '"Windows"'
        elif 'Macintosh' in ua:
            headers['sec-ch-ua-platform'] = '"macOS"'
        elif 'Linux' in ua and 'Android' not in ua:
            headers['sec-ch-ua-platform'] = '"Linux"'
        elif 'Android' in ua:
            headers['sec-ch-ua-platform'] = '"Android"'
        elif 'iPhone' in ua or 'iPad' in ua:
            headers['sec-ch-ua-platform'] = '"iOS"'
        
        return headers
    
    def fetch_page(self, url, retries=3, category=None):
        """Fetch page with random user agent rotation"""
        for attempt in range(retries):
            try:
                if self.rotate_on_every_request or attempt > 0:
                    headers = self.get_random_headers(category)
                else:
                    headers = self.get_random_headers(category)
                
                delay = random.uniform(self.delay_min, self.delay_max)
                if attempt > 0:
                    delay = delay * (attempt + 1)
                time.sleep(delay)
                
                response = self.session.get(url, timeout=10, headers=headers, allow_redirects=True)
                
                if response.status_code == 200:
                    return response
                elif response.status_code in [403, 429]:
                    self.delay_min += 0.3
                    self.delay_max += 0.5
                    time.sleep(random.uniform(5, 10))
                elif response.status_code == 404:
                    return None
                    
            except Exception as e:
                if attempt == retries - 1:
                    console.print(f"[red]❌ Failed: {e}[/]")
                    return None
                time.sleep(random.uniform(2, 5))
        
        return None
    
    def extract_links(self, html, base_url):
        """Extract all links from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href:
                full_url = urljoin(base_url, href)
                if full_url.startswith(('http://', 'https://')):
                    links.append({
                        'url': full_url,
                        'text': link.get_text(strip=True),
                        'title': link.get('title', '')
                    })
        return links
    
    def extract_emails(self, html):
        """Extract email addresses"""
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        return list(set(re.findall(email_pattern, html)))
    
    def extract_phones(self, html):
        """Extract phone numbers"""
        phone_patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'
        ]
        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, html))
        return list(set(phones))
    
    def extract_social_links(self, html):
        """Extract social media links"""
        social_patterns = {
            'facebook': r'https?://(?:www\.)?facebook\.com/[a-zA-Z0-9.]+',
            'twitter': r'https?://(?:www\.)?twitter\.com/[a-zA-Z0-9_]+',
            'instagram': r'https?://(?:www\.)?instagram\.com/[a-zA-Z0-9_.]+',
            'linkedin': r'https?://(?:www\.)?linkedin\.com/(?:in|company)/[a-zA-Z0-9_-]+',
            'youtube': r'https?://(?:www\.)?youtube\.com/(?:c|channel|user)/[a-zA-Z0-9_-]+',
            'github': r'https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+',
            'reddit': r'https?://(?:www\.)?reddit\.com/(?:r|u)/[a-zA-Z0-9_-]+',
            'tiktok': r'https?://(?:www\.)?tiktok\.com/@[a-zA-Z0-9_.]+'
        }
        
        social_links = {}
        for platform, pattern in social_patterns.items():
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                social_links[platform] = list(set(matches))
        
        return social_links
    
    def extract_metadata(self, soup):
        """Extract metadata from page"""
        metadata = {
            'title': '',
            'description': '',
            'keywords': '',
            'author': '',
            'og_title': '',
            'og_description': '',
            'og_image': ''
        }
        
        if soup.title:
            metadata['title'] = soup.title.string
        
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_ = meta.get('property', '').lower()
            content = meta.get('content', '')
            
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = content
            elif name == 'author':
                metadata['author'] = content
            elif property_ == 'og:title':
                metadata['og_title'] = content
            elif property_ == 'og:description':
                metadata['og_description'] = content
            elif property_ == 'og:image':
                metadata['og_image'] = content
        
        return metadata
    
    def scrape_page(self, url, depth=0, category=None):
        """Scrape a single page"""
        console.print(f"[cyan]📄 Scraping: {url}[/]")
        
        response = self.fetch_page(url, category=category)
        if not response:
            return None
        
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        
        metadata = self.extract_metadata(soup)
        
        data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'title': metadata['title'],
            'description': metadata['description'],
            'keywords': metadata['keywords'],
            'author': metadata['author'],
            'og_title': metadata['og_title'],
            'og_description': metadata['og_description'],
            'og_image': metadata['og_image'],
            'links': self.extract_links(html, url),
            'emails': self.extract_emails(html),
            'phones': self.extract_phones(html),
            'social': self.extract_social_links(html),
            'text_preview': soup.get_text()[:500].strip(),
            'images': [img.get('src') for img in soup.find_all('img') if img.get('src')],
            'depth': depth,
            'status_code': response.status_code
        }
        
        return data
    
    def crawl_website(self, start_url, max_pages=50, max_depth=3, threads=5, category=None):
        """Crawl entire website"""
        console.print(f"[bold yellow]🌐 Starting crawl: {start_url}[/]")
        console.print(f"[cyan]📊 Max pages: {max_pages}, Max depth: {max_depth}, Threads: {threads}[/]")
        
        results = []
        visited = set()
        queue = [(start_url, 0)]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Crawling...", total=max_pages)
            
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                
                while queue and len(results) < max_pages:
                    url, depth = queue.pop(0)
                    
                    if url in visited or depth > max_depth:
                        continue
                    
                    visited.add(url)
                    
                    future = executor.submit(self.scrape_page, url, depth, category)
                    futures.append(future)
                    
                    for f in as_completed(futures):
                        if f in futures:
                            futures.remove(f)
                            data = f.result()
                            if data:
                                results.append(data)
                                progress.update(task, advance=1)
                                
                                for link in data.get('links', [])[:10]:
                                    new_url = link['url']
                                    if new_url not in visited and depth + 1 <= max_depth:
                                        queue.append((new_url, depth + 1))
        
        self.results = results
        console.print(f"[green]✅ Scraped {len(results)} pages[/]")
        return results
    
    def batch_scrape(self, urls, threads=5, category=None):
        """Scrape multiple URLs"""
        console.print(f"[bold yellow]📋 Scraping {len(urls)} URLs[/]")
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scraping URLs...", total=len(urls))
            
            with ThreadPoolExecutor(max_workers=threads) as executor:
                future_to_url = {
                    executor.submit(self.scrape_page, url, 0, category): url for url in urls
                }
                
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        data = future.result()
                        if data:
                            results.append(data)
                    except Exception as e:
                        console.print(f"[red]❌ Error scraping {url}: {e}[/]")
                    progress.update(task, advance=1)
        
        self.results = results
        console.print(f"[green]✅ Scraped {len(results)} URLs[/]")
        return results
    
    def search_emails(self):
        """Search for emails in results"""
        all_emails = []
        for data in self.results:
            all_emails.extend(data.get('emails', []))
        return list(set(all_emails))
    
    def search_phones(self):
        """Search for phones in results"""
        all_phones = []
        for data in self.results:
            all_phones.extend(data.get('phones', []))
        return list(set(all_phones))
    
    def search_social(self):
        """Search for social links in results"""
        all_social = {}
        for data in self.results:
            for platform, links in data.get('social', {}).items():
                if platform not in all_social:
                    all_social[platform] = []
                all_social[platform].extend(links)
        
        for platform in all_social:
            all_social[platform] = list(set(all_social[platform]))
        
        return all_social
    
    def export_json(self, filename=None):
        """Export results to JSON"""
        if not filename:
            filename = f"data/scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if not self.results:
            console.print("[red]❌ No results to export[/]")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_pages': len(self.results),
                'data': self.results
            }, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✅ Exported to: {filename}[/]")
        return filename
    
    def export_csv(self, filename=None):
        """Export results to CSV"""
        if not filename:
            filename = f"data/scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        if not self.results:
            console.print("[red]❌ No results to export[/]")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['URL', 'Title', 'Description', 'Emails', 'Phones', 'Social', 'Depth'])
            
            for data in self.results:
                writer.writerow([
                    data.get('url', ''),
                    data.get('title', ''),
                    data.get('description', ''),
                    ', '.join(data.get('emails', [])),
                    ', '.join(data.get('phones', [])),
                    json.dumps(data.get('social', {})),
                    data.get('depth', 0)
                ])
        
        console.print(f"[green]✅ Exported to: {filename}[/]")
        return filename
    
    def export_sqlite(self, filename=None):
        """Export results to SQLite"""
        if not filename:
            filename = f"data/scrape_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        if not self.results:
            console.print("[red]❌ No results to export[/]")
            return
        
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                description TEXT,
                content TEXT,
                depth INTEGER,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                email TEXT,
                FOREIGN KEY (page_id) REFERENCES pages(id)
            )
        ''')
        
        for data in self.results:
            cursor.execute('''
                INSERT INTO pages (url, title, description, content, depth, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data.get('url', ''),
                data.get('title', ''),
                data.get('description', ''),
                data.get('text_preview', ''),
                data.get('depth', 0),
                data.get('timestamp', '')
            ))
            page_id = cursor.lastrowid
            
            for email in data.get('emails', []):
                cursor.execute('INSERT INTO emails (page_id, email) VALUES (?, ?)',
                             (page_id, email))
        
        conn.commit()
        conn.close()
        
        console.print(f"[green]✅ Exported to: {filename}[/]")
        return filename
    
    def show_results(self):
        """Display results in table"""
        if not self.results:
            console.print("[yellow]⚠️ No results to display[/]")
            return
        
        table = Table(title=f"Scraping Results ({len(self.results)} pages)")
        table.add_column("URL", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Emails", style="yellow")
        table.add_column("Phones", style="magenta")
        
        for data in self.results[:10]:
            table.add_row(
                data.get('url', '')[:50],
                data.get('title', '')[:30],
                ', '.join(data.get('emails', [])[:3]),
                ', '.join(data.get('phones', [])[:3])
            )
        
        console.print(table)
        
        total_emails = sum(len(d.get('emails', [])) for d in self.results)
        total_phones = sum(len(d.get('phones', [])) for d in self.results)
        
        console.print(Panel(
            f"[bold]Statistics:[/]\n"
            f"📄 Pages: {len(self.results)}\n"
            f"📧 Emails: {total_emails}\n"
            f"📱 Phones: {total_phones}\n"
            f"🔗 Links: {sum(len(d.get('links', [])) for d in self.results)}",
            title="Summary"
        ))
    
    def show_agents(self, limit=30):
        """Display random user agents"""
        table = Table(title=f"User Agent Database ({self.ua_db.count()} agents)")
        table.add_column("Browser", style="cyan")
        table.add_column("OS", style="green")
        table.add_column("Agent", style="white")
        
        sample = []
        for _ in range(min(limit, self.ua_db.count())):
            agent = self.ua_db.get_random()
            info = self.ua_db.get_info(agent)
            sample.append((agent, info))
        
        for agent, info in sample[:20]:
            table.add_row(
                info['browser'],
                info['os'],
                agent[:60] + "..." if len(agent) > 60 else agent
            )
        
        console.print(table)
        
        console.print(Panel(
            f"[bold]Agent Statistics:[/]\n"
            f"📊 Total: {self.ua_db.count()}\n"
            f"🔄 Rotation: {'ON' if self.rotate_on_every_request else 'OFF'}\n"
            f"📱 Mobile: {len([a for a in self.ua_db.user_agents if 'Mobile' in a or 'Android' in a])}\n"
            f"💻 Desktop: {len([a for a in self.ua_db.user_agents if 'Mobile' not in a and 'Android' not in a])}",
            title="Statistics"
        ))
    
    def save_agent_db(self):
        """Save user agent database to JSON"""
        count = self.ua_db.save_to_json("agents/user_agents.json")
        console.print(f"[green]✅ Saved {count} user agents to agents/user_agents.json[/]")
    
    def load_agent_db(self):
        """Load user agent database from JSON"""
        count = self.ua_db.load_from_json("agents/user_agents.json")
        if count:
            console.print(f"[green]✅ Loaded {count} user agents from agents/user_agents.json[/]")
        else:
            console.print("[yellow]⚠️ No agent database found, using default[/]")
    
    def update_agents(self):
        """Update user agent database"""
        console.print("[cyan]🔄 Saving user agent database...[/]")
        self.save_agent_db()
        console.print(f"[green]✅ Database updated! Total: {self.ua_db.count()} agents[/]")
    
    def menu(self):
        """Main menu with agent controls"""
        while True:
            console.clear()
            self.banner()
            
            menu_options = {
                '1': 'Scrape Single URL',
                '2': 'Scrape Multiple URLs',
                '3': 'Crawl Website',
                '4': 'Search Emails',
                '5': 'Search Social Links',
                '6': 'Search Phones',
                '7': 'Export Results',
                '8': 'View Results',
                '9': 'Show User Agents',
                '10': 'Save Agent Database',
                '11': 'Load Agent Database',
                '12': 'Toggle Agent Rotation',
                '13': 'Clear Results',
                '14': 'Exit'
            }
            
            table = Table(title="ShadowScrape Tools", style="cyan")
            table.add_column("Option", style="bold yellow")
            table.add_column("Tool", style="green")
            
            for key, value in menu_options.items():
                table.add_row(key, value)
            
            console.print(table)
            
            # Show current agent info
            current_ua = self.session.headers.get('User-Agent', 'Unknown')
            info = self.ua_db.get_info(current_ua)
            console.print(f"[dim]Current: {info['browser']} {info['version']} on {info['os']}[/dim]")
            console.print(f"[dim]Total Agents: {self.ua_db.count()}[/dim]")
            
            choice = Prompt.ask("[bold cyan]Select an option", choices=list(menu_options.keys()))
            
            if choice == '1':
                url = Prompt.ask("[cyan]Enter URL")
                category = Prompt.ask("[cyan]Category (desktop/mobile/windows/mac/linux/android/ios/chrome/firefox/edge/opera)", default="random")
                if category == "random":
                    category = None
                data = self.scrape_page(url, category=category)
                if data:
                    self.results.append(data)
                    console.print("[green]✅ Page scraped![/]")
                    self.show_results()
            
            elif choice == '2':
                urls = []
                while True:
                    url = Prompt.ask("[cyan]Enter URL (or Enter to finish)")
                    if not url:
                        break
                    urls.append(url)
                if urls:
                    category = Prompt.ask("[cyan]Category", default="random")
                    if category == "random":
                        category = None
                    self.batch_scrape(urls, category=category)
                    self.show_results()
            
            elif choice == '3':
                url = Prompt.ask("[cyan]Enter starting URL")
                max_pages = int(Prompt.ask("[cyan]Max pages", default="50"))
                max_depth = int(Prompt.ask("[cyan]Max depth", default="3"))
                threads = int(Prompt.ask("[cyan]Threads", default="5"))
                category = Prompt.ask("[cyan]Category", default="random")
                if category == "random":
                    category = None
                self.crawl_website(url, max_pages, max_depth, threads, category)
                self.show_results()
            
            elif choice == '4':
                emails = self.search_emails()
                if emails:
                    console.print("[bold green]📧 Found emails:[/]")
                    for email in emails[:20]:
                        console.print(f"  {email}")
                    if len(emails) > 20:
                        console.print(f"  ... and {len(emails) - 20} more")
                else:
                    console.print("[yellow]⚠️ No emails found[/]")
            
            elif choice == '5':
                social = self.search_social()
                if social:
                    console.print("[bold green]🔗 Social links found:[/]")
                    for platform, links in social.items():
                        console.print(f"  [bold]{platform}:[/]")
                        for link in links[:5]:
                            console.print(f"    {link}")
                        if len(links) > 5:
                            console.print(f"    ... and {len(links) - 5} more")
                else:
                    console.print("[yellow]⚠️ No social links found[/]")
            
            elif choice == '6':
                phones = self.search_phones()
                if phones:
                    console.print("[bold green]📱 Found phones:[/]")
                    for phone in phones[:20]:
                        console.print(f"  {phone}")
                    if len(phones) > 20:
                        console.print(f"  ... and {len(phones) - 20} more")
                else:
                    console.print("[yellow]⚠️ No phones found[/]")
            
            elif choice == '7':
                if not self.results:
                    console.print("[yellow]⚠️ No results to export[/]")
                else:
                    format_choice = Prompt.ask(
                        "[cyan]Export format",
                        choices=["json", "csv", "sqlite"],
                        default="json"
                    )
                    if format_choice == "json":
                        self.export_json()
                    elif format_choice == "csv":
                        self.export_csv()
                    elif format_choice == "sqlite":
                        self.export_sqlite()
            
            elif choice == '8':
                self.show_results()
            
            elif choice == '9':
                self.show_agents()
            
            elif choice == '10':
                self.save_agent_db()
            
            elif choice == '11':
                self.load_agent_db()
            
            elif choice == '12':
                self.rotate_on_every_request = not self.rotate_on_every_request
                console.print(f"[green]✅ Agent rotation: {'ON' if self.rotate_on_every_request else 'OFF'}[/]")
            
            elif choice == '13':
                if Confirm.ask("[red]Clear all results?"):
                    self.results = []
                    console.print("[yellow]✅ Results cleared[/]")
            
            elif choice == '14':
                console.print("[bold red]Exiting ShadowScrape...[/]")
                break
            
            if choice != '14':
                Confirm.ask("\n[cyan]Press Enter to continue...", default=True)

def main():
    try:
        scraper = ShadowScrape()
        scraper.menu()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/]")
        sys.exit(1)

if __name__ == "__main__":
    main()
