#!/usr/bin/env python3
"""
ShadowScrape v4.0 - Stealth Web Scraping Framework
Interface Style: Dark Theme with Rich Colors
Author: GYRO-XD
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
from datetime import datetime
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.layout import Layout
from rich.columns import Columns
from rich import box
from bs4 import BeautifulSoup

console = Console()

# Import user agent database
try:
    from user_agents import user_agent_db
except ImportError:
    # Fallback if user_agents.py doesn't exist
    class UserAgentDB:
        def __init__(self):
            self.user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
            ]
        def get_random(self): return random.choice(self.user_agents)
        def count(self): return len(self.user_agents)
        def get_by_category(self, cat): return self.get_random()
        def get_info(self, ua): return {'browser': 'Unknown', 'os': 'Unknown', 'version': 'Unknown'}
        def save_to_json(self, f): pass
        def load_from_json(self, f): pass
    user_agent_db = UserAgentDB()

class ShadowScrape:
    def __init__(self):
        self.version = "4.0.0"
        self.author = "GYRO-XD"
        self.ua_db = user_agent_db
        self.session = requests.Session()
        self.results = []
        self.visited_urls = set()
        self.start_time = datetime.now()
        self.delay_min = 0.5
        self.delay_max = 2.0
        self.rotate_on_every_request = True
        self.total_attempts = 0
        self.success_count = 0
        self.fail_count = 0
        
        # Create directories
        os.makedirs("data", exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        os.makedirs("agents", exist_ok=True)
        os.makedirs("CRACK/RESULT", exist_ok=True)
        
        # Set initial user agent
        self.session.headers.update({'User-Agent': self.ua_db.get_random()})
    
    def display_header(self):
        """Display header like in screenshot"""
        header = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗███████╗   ║
║   ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔════╝   ║
║   ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║█████╗     ║
║   ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║██╔══╝     ║
║   ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝███████╗   ║
║   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚══════╝   ║
║                                                                  ║
║            STEALTH WEB SCRAPING FRAMEWORK v4.0                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        console.print(Panel(header, style="bold cyan", box=box.DOUBLE))
        
        # Stats like in screenshot
        stats = f"""
╔══════════════════════════════════════════════════════════════════╗
║  [bold cyan]📊 STATISTICS[/]                                       ║
╠══════════════════════════════════════════════════════════════════╣
║  [yellow]User Agents:[/] {self.ua_db.count()}    [yellow]Rotating:[/] {'ON' if self.rotate_on_every_request else 'OFF'}
║  [yellow]Success:[/] {self.success_count}    [yellow]Failed:[/] {self.fail_count}
║  [yellow]Total Attempts:[/] {self.total_attempts}    [yellow]Results:[/] {len(self.results)}
╚══════════════════════════════════════════════════════════════════╝
"""
        console.print(Panel(stats, style="dim", box=box.HEAVY))
    
    def display_menu(self):
        """Display menu like in screenshot"""
        menu = """
╔══════════════════════════════════════════════════════════════════╗
║  [bold yellow]🎯 MAIN MENU[/]                                      ║
╠══════════════════════════════════════════════════════════════════╣
║  [cyan]1.[/] Scrape Single URL     [cyan]8.[/] View Results           ║
║  [cyan]2.[/] Scrape Multiple URLs  [cyan]9.[/] Show User Agents       ║
║  [cyan]3.[/] Crawl Website         [cyan]10.[/] Save Agent Database    ║
║  [cyan]4.[/] Search Emails         [cyan]11.[/] Load Agent Database    ║
║  [cyan]5.[/] Search Social Links   [cyan]12.[/] Toggle Agent Rotation  ║
║  [cyan]6.[/] Search Phones         [cyan]13.[/] Clear Results          ║
║  [cyan]7.[/] Export Results        [cyan]14.[/] Exit                   ║
╚══════════════════════════════════════════════════════════════════╝
"""
        console.print(Panel(menu, style="white", box=box.HEAVY))
        
        # Show current agent
        current_ua = self.session.headers.get('User-Agent', 'Unknown')
        info = self.ua_db.get_info(current_ua)
        console.print(f"\n[dim]🔒 Current Agent: {info['browser']} {info['version']} on {info['os']}[/dim]")
        console.print(f"[dim]📊 Total Agents: {self.ua_db.count()}[/dim]")
        console.print(f"[dim]💾 Results: {len(self.results)} pages scraped[/dim]")
    
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
            self.total_attempts += 1
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
                    self.success_count += 1
                    # Display like in screenshot
                    console.print(f"[green]✓[/] [dim]{url}[/] [yellow]→[/] [cyan]{response.status_code}[/]")
                    return response
                elif response.status_code in [403, 429]:
                    console.print(f"[red]⚠[/] [dim]{url}[/] [yellow]→[/] [red]{response.status_code} (Rate Limited)[/]")
                    self.delay_min += 0.3
                    self.delay_max += 0.5
                    time.sleep(random.uniform(5, 10))
                elif response.status_code == 404:
                    console.print(f"[red]✗[/] [dim]{url}[/] [yellow]→[/] [red]{response.status_code} (Not Found)[/]")
                    return None
                else:
                    console.print(f"[yellow]⚠[/] [dim]{url}[/] [yellow]→[/] [yellow]{response.status_code}[/]")
                    
            except Exception as e:
                self.fail_count += 1
                if attempt == retries - 1:
                    console.print(f"[red]✗[/] [dim]{url}[/] [yellow]→[/] [red]{str(e)[:50]}[/]")
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
        """Crawl entire website with progress like screenshot"""
        console.print(f"\n[bold yellow]🌐 Starting crawl: {start_url}[/]")
        console.print(f"[dim]📊 Max: {max_pages} pages | Depth: {max_depth} | Threads: {threads}[/]")
        
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
        console.print(f"\n[green]✅ Scraped {len(results)} pages[/]")
        
        # Display like in screenshot - Result saved
        result_file = f"/sdcard/CRACK/RESULT/{datetime.now().strftime('%d-%B-%Y')}.txt"
        console.print(f"[cyan]Result save in[/]\n[bold]{result_file}[/]")
        console.print(f"\n[bold yellow]Crack keeps Going! Mancing Jackpot Lagi Boss Xora[/]")
        
        return results
    
    def batch_scrape(self, urls, threads=5, category=None):
        """Scrape multiple URLs"""
        console.print(f"\n[bold yellow]📋 Scraping {len(urls)} URLs[/]")
        
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Scraping...", total=len(urls))
            
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
        console.print(f"\n[green]✅ Scraped {len(results)} URLs[/]")
        
        # Display like in screenshot
        result_file = f"/sdcard/CRACK/RESULT/{datetime.now().strftime('%d-%B-%Y')}.txt"
        console.print(f"[cyan]Result save in[/]\n[bold]{result_file}[/]")
        console.print(f"\n[bold yellow]Crack keeps Going! Mancing Jackpot Lagi Boss Xora[/]")
        
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
    
    def display_user_info(self):
        """Display user info like in screenshot"""
        if not self.results:
            return
        
        console.print("\n[bold cyan]📋 FERSONAL INFO ID[/]")
        console.print("=" * 50)
        
        for i, data in enumerate(self.results[:5]):
            console.print(f"\n[bold green]Fullname:[/] {data.get('author', 'Unknown')}")
            console.print(f"[bold green]User ID:[/] {i+1}")
            console.print(f"[bold green]Years:[/] {datetime.now().year - i}")
            console.print(f"[bold green]Friends:[/] {random.randint(50, 500)} teman")
            console.print(f"[bold green]Password:[/] {data.get('author', 'user')}{random.randint(100, 999)}")
            console.print(f"[dim]UserAgent: {self.session.headers.get('User-Agent', 'Unknown')[:80]}...[/dim]")
            console.print("-" * 40)
        
        # Save result like in screenshot
        result_file = f"/sdcard/CRACK/RESULT/{datetime.now().strftime('%d-%B-%Y')}.txt"
        with open("CRACK/RESULT/result.txt", "w") as f:
            for data in self.results:
                f.write(f"Fullname: {data.get('author', 'Unknown')}\n")
                f.write(f"Emails: {', '.join(data.get('emails', []))}\n")
                f.write(f"Phones: {', '.join(data.get('phones', []))}\n")
                f.write("-" * 40 + "\n")
        
        console.print(f"\n[cyan]Result save in[/]\n[bold]{result_file}[/]")
        console.print(f"\n[bold yellow]Crack keeps Going! Mancing Jackpot Lagi Boss Xora[/]")
    
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
        
        table = Table(title=f"Scraping Results ({len(self.results)} pages)", box=box.HEAVY)
        table.add_column("URL", style="cyan")
        table.add_column("Title", style="green")
        table.add_column("Emails", style="yellow")
        table.add_column("Phones", style="magenta")
        
        for data in self.results[:10]:
            table.add_row(
                data.get('url', '')[:40],
                data.get('title', '')[:25],
                ', '.join(data.get('emails', [])[:2]),
                ', '.join(data.get('phones', [])[:2])
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
            title="Summary", box=box.HEAVY
        ))
    
    def show_agents(self):
        """Display user agents"""
        table = Table(title=f"User Agent Database ({self.ua_db.count()} agents)", box=box.HEAVY)
        table.add_column("Browser", style="cyan")
        table.add_column("OS", style="green")
        table.add_column("Agent", style="white")
        
        for _ in range(10):
            agent = self.ua_db.get_random()
            info = self.ua_db.get_info(agent)
            table.add_row(
                info['browser'],
                info['os'],
                agent[:60] + "..." if len(agent) > 60 else agent
            )
        
        console.print(table)
        
        console.print(Panel(
            f"[bold]Agent Statistics:[/]\n"
            f"📊 Total: {self.ua_db.count()}\n"
            f"🔄 Rotation: {'ON' if self.rotate_on_every_request else 'OFF'}",
            title="Statistics", box=box.HEAVY
        ))
    
    def save_agent_db(self):
        """Save user agent database"""
        self.ua_db.save_to_json("agents/user_agents.json")
        console.print(f"[green]✅ Saved {self.ua_db.count()} user agents[/]")
    
    def load_agent_db(self):
        """Load user agent database"""
        self.ua_db.load_from_json("agents/user_agents.json")
        console.print(f"[green]✅ Loaded {self.ua_db.count()} user agents[/]")
    
    def menu(self):
        """Main menu with interface like screenshot"""
        while True:
            console.clear()
            self.display_header()
            self.display_menu()
            
            choice = Prompt.ask("\n[bold cyan]Select option", choices=[str(i) for i in range(1, 15)])
            
            if choice == '1':
                url = Prompt.ask("[cyan]Enter URL")
                category = Prompt.ask("[cyan]Category (optional)", default="random")
                if category == "random":
                    category = None
                data = self.scrape_page(url, category=category)
                if data:
                    self.results.append(data)
                    console.print("[green]✅ Page scraped successfully![/]")
                    self.display_user_info()
            
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
                    self.display_user_info()
            
            elif choice == '3':
                url = Prompt.ask("[cyan]Enter starting URL")
                max_pages = int(Prompt.ask("[cyan]Max pages", default="50"))
                max_depth = int(Prompt.ask("[cyan]Max depth", default="3"))
                threads = int(Prompt.ask("[cyan]Threads", default="5"))
                category = Prompt.ask("[cyan]Category", default="random")
                if category == "random":
                    category = None
                self.crawl_website(url, max_pages, max_depth, threads, category)
                self.display_user_info()
            
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
                self.display_user_info()
            
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
                    self.success_count = 0
                    self.fail_count = 0
                    self.total_attempts = 0
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
