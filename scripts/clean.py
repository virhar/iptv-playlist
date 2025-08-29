import os, sys, requests, re
from urllib.parse import urlparse

COUNTRY_MAP = {
    "FR": "FRANCE",
    "CN": "CHINA",
    "US": "USA",
    "GB": "UK",
    "DE": "GERMANY",
    "ES": "SPAIN",
    "IT": "ITALY",
    "RU": "RUSSIA",
    "JP": "JAPAN",
    "KR": "KOREA",
    "BR": "BRAZIL",
    "IN": "INDIA",
}

def load_channels_db():
    url = "https://iptv-org.github.io/api/channels.json"
    try:
        return requests.get(url).json()
    except Exception as e:
        print(f"Erreur récupération base: {e}")
        return []

def guess_name_from_url(url):
    hostname = urlparse(url).hostname or ""
    hostname = hostname.replace("www.","")
    base = hostname.split(".")[0].upper()
    return base if base else "Channel"

def enrich(url, db, counter):
    chan = next((c for c in db if "url" in c and url in c["url"]), None)
    if chan:
        iso = chan.get("country", "")
        country = COUNTRY_MAP.get(iso, iso if iso else "OTHER")
        name = chan.get("name", f"Channel_{counter}")
        tvg_id = chan.get("id", "")
        logo = chan.get("logo", "")
        return f'#EXTINF:-1 tvg-id="{tvg_id}" group-title="{country}",{country}_{name}\n'
    else:
        # fallback: donner un nom basé sur le domaine
        country = "OTHER"
        guess = guess_name_from_url(url)
        return f'#EXTINF:-1 group-title="{country}",{country}_{guess}_{counter}\n'

def process(input_dir, output_file):
    db = load_channels_db()
    seen = set()
    result = ["#EXTM3U\n"]
    counter = 1

    for fname in os.listdir(input_dir):
        with open(os.path.join(input_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF"):
                    url = lines[i+1].strip() if i+1 < len(lines) else ""
                    # Ne pas exclure les .m3u8
                    if not url or (url.endswith(".m3u") and not url.endswith(".m3u8")):
                        continue
                    if url in seen:
                        continue
                    seen.add(url)
                    result.append(enrich(url, db, counter))
                elif line.startswith("http"):
                    if line.strip().endswith(".m3u") and not line.strip().endswith(".m3u8"):
                        continue
                    if line.strip() in seen:
                        continue
                    seen.add(line.strip())
                    result.append(line)
                    counter += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(result)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: clean.py <input_dir> <output_file>")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
