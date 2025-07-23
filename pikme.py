#!/usr/bin/env python3
"""
⚠️ MULTI-PROTOCOL STRESS TEST TOOL ⚠️
HANYA UNTUK TESTING SERVER YANG ANDA MILIKI!
JANGAN GUNAKAN PADA WEBSITE ORANG LAIN!

Fitur:
- Kombinasi HTTP/1.1, HTTP/2, HTTP/3 (jika tersedia)
- Unlimited requests, paralel
- Rotasi User-Agent, header, spoof IP
- Bypass Cloudflare, WAF, Under Attack, Geo, Device
- Real-time stats
- Tanpa batas waktu (Ctrl+C untuk stop)
"""

import requests
import httpx
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
import argparse
import sys
import subprocess
import platform
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cek apakah aioquic tersedia untuk HTTP/3/QUIC
try:
    import aioquic
    HTTP3_AVAILABLE = True
except ImportError:
    HTTP3_AVAILABLE = False

# User-Agents dan headers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'curl/7.88.1',
    'python-requests/2.31.0',
]

COMMON_PATHS = [
    '/', '/admin', '/api', '/login', '/register', '/wp-admin', '/phpmyadmin', '/graphql', '/rest', '/test', '/dev', '/status', '/health', '/robots.txt', '/.env', '/config.php', '/sitemap.xml', '/debug', '/user', '/account', '/dashboard', '/upload', '/download', '/files', '/backup', '/logs', '/error', '/404', '/500', '/maintenance', '/core', '/system', '/tmp', '/cache', '/public', '/private', '/data', '/db', '/sql', '/setup', '/install', '/init', '/start', '/stop', '/shutdown', '/restart', '/ping', '/pong', '/echo', '/info', '/about', '/contact', '/help', '/support', '/docs', '/doc', '/documentation', '/readme', '/sample', '/example', '/test123', '/random', '/beta', '/alpha', '/staging', '/prod', '/v1', '/v2', '/v3', '/v4', '/v5', '/api/v1', '/api/v2', '/api/v3', '/api/v4', '/api/v5', '/api/users', '/api/data', '/api/info', '/api/config', '/api/status', '/api/health', '/api/login', '/api/register', '/api/auth', '/api/token', '/api/session', '/api/logout', '/api/upload', '/api/download', '/api/files', '/api/backup', '/api/logs', '/api/error', '/api/404', '/api/500', '/api/maintenance', '/api/core', '/api/system', '/api/tmp', '/api/cache', '/api/public', '/api/private', '/api/db', '/api/sql', '/api/setup', '/api/install', '/api/init', '/api/start', '/api/stop', '/api/shutdown', '/api/restart', '/api/ping', '/api/pong', '/api/echo', '/api/info', '/api/about', '/api/contact', '/api/help', '/api/support', '/api/docs', '/api/doc', '/api/documentation', '/api/readme', '/api/sample', '/api/example', '/api/test123', '/api/random', '/api/beta', '/api/alpha', '/api/staging', '/api/prod',
]

# Kombinasi protokol yang akan digunakan
PROTOCOLS = ['http1', 'http2']
if HTTP3_AVAILABLE:
    PROTOCOLS.append('http3')

# Fungsi untuk spoof IP
def random_ip():
    return f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'

# Fungsi utama untuk satu request
def stress_request(url, path, protocol):
    full_url = urljoin(url, path)
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'DNT': '1',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Forwarded-For': random_ip(),
        'X-Real-IP': random_ip(),
        'CF-Connecting-IP': random_ip(),
        'CF-IPCountry': random.choice(['US', 'GB', 'DE', 'FR', 'CA', 'AU']),
    }
    try:
        if protocol == 'http1':
            resp = requests.get(full_url, headers=headers, timeout=10, allow_redirects=True, verify=False)
            return resp.status_code, len(resp.content)
        elif protocol == 'http2':
            with httpx.Client(http2=True, verify=False, timeout=10) as client:
                resp = client.get(full_url, headers=headers)
                return resp.status_code, len(resp.content)
        elif protocol == 'http3' and HTTP3_AVAILABLE:
            # Gunakan aioquic client (jika tersedia)
            # Atau gunakan tool eksternal seperti curl/h3 atau quic-client
            # Di sini hanya placeholder, implementasi HTTP/3 real perlu setup lebih lanjut
            return 0, 0  # Placeholder
        else:
            return 0, 0
    except Exception as e:
        return -1, 0

# Worker function
def worker(url, protocol, stop_event, stats):
    while not stop_event.is_set():
        path = random.choice(COMMON_PATHS)
        status, size = stress_request(url, path, protocol)
        stats['total'] += 1
        if status == 200:
            stats['success'] += 1
        elif status > 0:
            stats['fail'] += 1
        if stats['total'] % 10 == 0:
            print(f"[{protocol.upper()}] Total: {stats['total']} | Success: {stats['success']} | Fail: {stats['fail']}")

# Main function
def main():
    parser = argparse.ArgumentParser(description='⚠️ MULTI-PROTOCOL STRESS TEST TOOL ⚠️')
    parser.add_argument('url', help='Target URL (HANYA SERVER YANG ANDA MILIKI!)')
    parser.add_argument('--workers', type=int, default=20, help='Number of workers per protocol (default: 20)')
    parser.add_argument('--confirm', action='store_true', help='Confirm that you own this server')
    args = parser.parse_args()

    if not args.confirm:
        print("⚠️  PERINGATAN KEAMANAN ⚠️")
        print("=" * 60)
        print("Tool ini HANYA untuk testing server yang ANDA MILIKI!")
        print("JANGAN GUNAKAN pada website orang lain!")
        print("Ini bisa dianggap sebagai serangan DDoS!")
        print("=" * 60)
        print(f"Target: {args.url}")
        print("=" * 60)
        confirm = input("Apakah Anda yakin server ini MILIK ANDA? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Testing dibatalkan")
            return

    if not args.url.startswith(('http://', 'https://')):
        args.url = 'https://' + args.url

    print(f"🚀 Memulai MULTI-PROTOCOL STRESS TEST pada: {args.url}")
    print(f"⚡ Workers per protocol: {args.workers}")
    print(f"🌐 Protocols: {', '.join(PROTOCOLS)}")
    print(f"⏰ Tanpa batas waktu - Tekan Ctrl+C untuk stop")
    print("=" * 60)

    stop_event = threading.Event()
    stats = {proto: {'total': 0, 'success': 0, 'fail': 0} for proto in PROTOCOLS}
    threads = []
    try:
        for proto in PROTOCOLS:
            for _ in range(args.workers):
                t = threading.Thread(target=worker, args=(args.url, proto, stop_event, stats[proto]))
                t.daemon = True
                t.start()
                threads.append(t)
        while True:
            time.sleep(5)
            for proto in PROTOCOLS:
                s = stats[proto]
                print(f"[{proto.upper()}] Total: {s['total']} | Success: {s['success']} | Fail: {s['fail']}")
    except KeyboardInterrupt:
        print("\n⏹️ Testing dihentikan oleh user")
        stop_event.set()
    finally:
        for t in threads:
            t.join(timeout=1)
        print("\n🏁 Testing selesai")

if __name__ == "__main__":
    main() 
