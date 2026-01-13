import requests
import re
import datetime

# 你的源文件列表
URL_FILE = 'url.txt'
# 输出文件名
OUTPUT_FILE = 'live.m3u'

def fetch_url(url):
    try:
        response = requests.get(url.strip(), timeout=10)
        response.encoding = response.apparent_encoding # 自动识别编码，防止乱码
        return response.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def is_m3u_content(content):
    return "#EXTM3U" in content

def convert_txt_to_m3u(content):
    """将 txt 格式 (频道名,URL) 转换为 m3u 格式"""
    m3u_lines = []
    lines = content.split('\n')
    current_group = "默认分组"
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 处理分组标记，例如 "央视频道,#genre#"
        if "#genre#" in line:
            current_group = line.split(',')[0]
            continue
            
        # 处理普通频道 "CCTV1,http://..."
        if "," in line and "#" not in line:
            parts = line.split(',')
            if len(parts) >= 2:
                name = parts[0]
                url = parts[1]
                m3u_lines.append(f'#EXTINF:-1 group-title="{current_group}",{name}')
                m3u_lines.append(url)
    
    return "\n".join(m3u_lines)

def main():
    final_content = ["#EXTM3U"]
    
    with open(URL_FILE, 'r', encoding='utf-8') as f:
        urls = f.readlines()

    for url in urls:
        url = url.strip()
        if not url or url.startswith('#'):
            continue
            
        print(f"Processing: {url}")
        content = fetch_url(url)
        
        if not content:
            continue

        if is_m3u_content(content):
            # 如果是 M3U，去掉头部 #EXTM3U，保留内容
            lines = content.split('\n')
            for line in lines:
                if line.strip() and not line.startswith("#EXTM3U"):
                    final_content.append(line.strip())
        else:
            # 如果是 TXT，转换后添加
            m3u_part = convert_txt_to_m3u(content)
            final_content.append(m3u_part)

    # 写入文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("\n".join(final_content))
    
    print(f"Done! Merged into {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
