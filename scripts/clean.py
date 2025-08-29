import os, sys, re

# Dictionnaire pour traduire abréviations → noms clairs
COUNTRY_MAP = {
    "fr": "FRANCE",
    "cn": "CHINA",
    "us": "USA",
    "gb": "UK",
    "de": "GERMANY",
    "es": "SPAIN",
    "it": "ITALY",
    "ru": "RUSSIA",
    "jp": "JAPAN",
    "kr": "KOREA",
    "br": "BRAZIL",
    "in": "INDIA",
}

CATEGORY_MAP = {
    "sports": "SPORT",
    "movies": "MOVIES",
    "news": "NEWS",
    "entertainment": "ENTERTAINMENT",
    "kids": "KIDS",
    "music": "MUSIC",
}

def detect_group(filename):
    fname = filename.lower()
    country = "OTHER"
    category = "GENERAL"

    for key, val in COUNTRY_MAP.items():
        if key in fname:
            country = val
            break
    for key, val in CATEGORY_MAP.items():
        if key in fname:
            category = val
            break

    return f"{country}-{category}"

def process(input_dir, output_file):
    seen = set()
    result = ["#EXTM3U\n"]
    counter = 1

    for fname in os.listdir(input_dir):
        group = detect_group(fname)
        with open(os.path.join(input_dir, fname), "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if line.startswith("#EXTINF"):
                    url = lines[i+1].strip() if i+1 < len(lines) else ""
                    if not url or url in seen:
                        continue
                    seen.add(url)
                    # Ajouter group-title et préfixe nom
                    if "," in line:
                        name = line.split(",",1)[1].strip()
                    else:
                        name = f"Channel_{counter}"
                    result.append(f'#EXTINF:-1 group-title="{group}",{group}_{name}\n')
                elif line.startswith("http"):
                    if line.strip() not in seen:
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
