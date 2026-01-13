import requests
import datetime
import os

# 配置
URLS_FILE = 'urls.txt'
OUTPUT_FILE = 'all_live.m3u'

def get_content(url):
    try:
        # 设置超时，防止卡死
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8' # 强制utf-8，防止中文乱码
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_m3u(content):
    """简单的M3U解析，提取EXTINF行和URL"""
    lines = content.splitlines()
    playlist = []
    current_inf = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF"):
            current_inf = line
        elif not line.startswith("#") and current_inf:
            playlist.append(f"{current_inf}\n{line}")
            current_inf = None
    return playlist

def parse_txt(content):
    """解析 频道名,URL 格式的txt"""
    lines = content.splitlines()
    playlist = []
    
    for line in lines:
        if "," in line and "#genre#" not in line:
            try:
                name, url = line.split(",", 1)
                # 转换成 M3U 格式
                m3u_entry = f'#EXTINF:-1 group-title="TXT导入",{name.strip()}\n{url.strip()}'
                playlist.append(m3u_entry)
            except:
                continue
    return playlist

def main():
    if not os.path.exists(URLS_FILE):
        print("urls.txt not found!")
        return

    all_channels = []
    
    # 添加 M3U 头部
    header = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"'
    
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for url in urls:
        print(f"Processing: {url}")
        content = get_content(url)
        if not content:
            continue
            
        if "#EXTM3U" in content:
            print("Detected Format: M3U")
            all_channels.extend(parse_m3u(content))
        else:
            print("Detected Format: TXT (Assuming)")
            all_channels.extend(parse_txt(content))

    # 写入结果
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(header + '\n')
        # 加上更新时间作为注释
        f.write(f'# Updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
        f.write('\n'.join(all_channels))
    
    print(f"Done! Total channels: {len(all_channels)}")

if __name__ == '__main__':
    main()
