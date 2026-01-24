import requests
import datetime
import os
import sys

# === 配置部分 ===
URLS_FILE = 'urls.txt'

# 输出的三个文件名
FILE_TXT_ONLY = 'live_txt.txt'      # 纯 txt 源整合
FILE_M3U_ONLY = 'live_m3u.m3u'      # 纯 m3u 源整合
FILE_ALL_COMBINED = 'all_live.m3u'  # 所有源整合 (M3U格式)

# M3U 头部
M3U_HEADER = '#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml"'

def get_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def parse_m3u(content):
    """解析 M3U，返回 M3U 条目列表"""
    lines = content.splitlines()
    playlist = []
    current_inf = None
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.startswith("#EXTINF"):
            current_inf = line
        elif not line.startswith("#") and current_inf:
            playlist.append(f"{current_inf}\n{line}")
            current_inf = None
    return playlist

def parse_txt(content):
    """
    解析 TXT，返回两个列表：
    1. raw_list: 原始格式 ["CCTV1,http://...", ...]
    2. m3u_list: 转换后的M3U格式 ["#EXTINF... \n http...", ...]
    """
    lines = content.splitlines()
    raw_list = []
    m3u_list = []
    
    for line in lines:
        if "," in line and "#genre#" not in line:
            try:
                # 处理一下空格
                parts = line.split(",", 1)
                name = parts[0].strip()
                url = parts[1].strip()
                
                # 存入原始 TXT 列表
                raw_list.append(f"{name},{url}")
                
                # 转换为 M3U 存入列表
                m3u_entry = f'#EXTINF:-1 group-title="TXT导入",{name}\n{url}'
                m3u_list.append(m3u_entry)
            except:
                continue
    return raw_list, m3u_list

def save_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    if not os.path.exists(URLS_FILE):
        print(f"Error: {URLS_FILE} not found!")
        sys.exit(1)

    # 容器初始化
    m3u_source_entries = [] # 存放来自 m3u 源的条目
    txt_source_raw = []     # 存放来自 txt 源的原始条目
    txt_source_converted = [] # 存放来自 txt 源转化的 m3u 条目

    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    for url in urls:
        print(f"Processing: {url}")
        content = get_content(url)
        if not content: continue
            
        if "#EXTM3U" in content:
            #如果是M3U源
            entries = parse_m3u(content)
            m3u_source_entries.extend(entries)
        else:
            #如果是TXT源
            raw, converted = parse_txt(content)
            txt_source_raw.extend(raw)
            txt_source_converted.extend(converted)

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # === 1. 生成 live_txt.txt (仅TXT源) ===
    txt_content = f"更新时间,#genre#\n" + "\n".join(txt_source_raw)
    save_file(FILE_TXT_ONLY, txt_content)
    print(f"Generated {FILE_TXT_ONLY} ({len(txt_source_raw)} channels)")

    # === 2. 生成 live_m3u.m3u (仅M3U源) ===
    m3u_only_content = f"{M3U_HEADER}\n# Updated: {current_time}\n" + "\n".join(m3u_source_entries)
    save_file(FILE_M3U_ONLY, m3u_only_content)
    print(f"Generated {FILE_M3U_ONLY} ({len(m3u_source_entries)} channels)")

    # === 3. 生成 all_live.m3u (全部整合) ===
    # 合并列表：先放M3U源的，再放TXT转过来的（反之亦可）
    all_content_list = m3u_source_entries + txt_source_converted
    all_content = f"{M3U_HEADER}\n# Updated: {current_time}\n" + "\n".join(all_content_list)
    save_file(FILE_ALL_COMBINED, all_content)
    print(f"Generated {FILE_ALL_COMBINED} ({len(all_content_list)} channels)")

if __name__ == '__main__':
    main()
