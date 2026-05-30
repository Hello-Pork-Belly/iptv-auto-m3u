import os
import re
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')

CHANNELS_FILE = os.path.join(CONFIG_DIR, 'channels.txt')
SOURCES_FILE = os.path.join(CONFIG_DIR, 'sources.txt')
LOCAL_M3U_FILE = os.path.join(CONFIG_DIR, 'local.m3u')
OUTPUT_M3U_FILE = os.path.join(OUTPUT_DIR, 'result.m3u')

def read_lines(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = []
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                lines.append(line)
        return lines

def parse_m3u(content):
    results = []
    lines = content.splitlines()
    current_name = ""
    for line in lines:
        line = line.strip()
        if line.startswith('#EXTINF'):
            parts = line.split(',')
            if len(parts) > 1:
                current_name = parts[-1].strip()
        elif line and not line.startswith('#'):
            if current_name:
                results.append((current_name, line))
                current_name = ""
    return results

def parse_txt(content):
    results = []
    lines = content.splitlines()
    for line in lines:
        line = line.strip()
        if line and ',' in line and not line.startswith('#'):
            parts = line.split(',', 1)
            if len(parts) == 2:
                results.append((parts[0].strip(), parts[1].strip()))
    return results

def fetch_source(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            if '#EXTM3U' in content:
                return parse_m3u(content)
            else:
                return parse_txt(content)
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        return []

def check_url(item):
    name, url = item
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        # Try HEAD
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 206, 301, 302, 403):
                return item
    except urllib.error.HTTPError as e:
        if e.code in (200, 206, 301, 302, 403):
            return item
    except Exception:
        pass
    
    try:
        # Fallback to GET stream (read small amount)
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 206, 301, 302, 403):
                response.read(10)
                return item
    except urllib.error.HTTPError as e:
        if e.code in (200, 206, 301, 302, 403):
            return item
    except Exception:
        pass
        
    return None

def main():
    print("=== IPTV Playlist Generator ===")
    
    # 1. 读取白名单
    whitelist = set(read_lines(CHANNELS_FILE))
    print(f"[Info] Loaded {len(whitelist)} channels from whitelist.")
    
    # 2. 读取本地源
    local_streams = []
    if os.path.exists(LOCAL_M3U_FILE):
        with open(LOCAL_M3U_FILE, 'r', encoding='utf-8') as f:
            local_streams = parse_m3u(f.read())
    print(f"[Info] Loaded {len(local_streams)} local streams.")
    
    # 3. 读取远程源
    sources = read_lines(SOURCES_FILE)
    remote_streams = []
    for source in sources:
        print(f"[Fetch] Fetching source: {source}")
        remote_streams.extend(fetch_source(source))
    print(f"[Info] Fetched {len(remote_streams)} remote streams.")
    
    # 4. 合并并过滤白名单
    all_streams = local_streams + remote_streams
    filtered_streams = []
    for name, url in all_streams:
        if name in whitelist:
            filtered_streams.append((name, url))
    print(f"[Info] {len(filtered_streams)} streams matched the whitelist.")
    
    # 5. 去重 (保留第一次出现的优先级，即 local 优先)
    seen = set()
    unique_streams = []
    for name, url in filtered_streams:
        if (name, url) not in seen:
            seen.add((name, url))
            unique_streams.append((name, url))
    print(f"[Info] {len(unique_streams)} unique streams to check.")
    
    # 6. 可用性检测
    print("[Check] Starting URL availability check...")
    available_streams = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        results = executor.map(check_url, unique_streams)
        for res in results:
            if res:
                available_streams.append(res)
                
    failed_count = len(unique_streams) - len(available_streams)
    print(f"[Check] Check finished. {len(available_streams)} available, {failed_count} failed.")
    
    # 7. 生成输出文件
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_M3U_FILE, 'w', encoding='utf-8') as f:
        f.write("#EXTM3U\n")
        for name, url in available_streams:
            f.write(f"#EXTINF:-1,{name}\n")
            f.write(f"{url}\n")
            
    print(f"[Success] Generated output at {OUTPUT_M3U_FILE}")

if __name__ == '__main__':
    main()
