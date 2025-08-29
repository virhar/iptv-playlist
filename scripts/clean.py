import os, sys, re

# Mapping simple ISO ou mots-clés -> pays
COUNTRY_MAP = {
    "fr": "FRANCE",
    "us": "USA",
    "gb": "UK",
    "cn": "CHINA",
    "de": "GERMANY",
    "es": "SPAIN",
    "it": "ITALY",
    "ru": "RUSSIA",
    "jp": "JAPAN",
    "kr": "KOREA",
    "br": "BRAZIL",
    "in": "INDIA",
}

# Catégories communes
CATEGORY_MAP = {
    "sports": "SPORT",
    "sport": "SPORT",
    "movies": "MOVIES",
    "cinema": "MOVIES",
    "news": "NEWS",
    "info": "NEWS",
    "entertainment": "ENTERTAINMENT",
    "kids": "KIDS",
    "cartoon": "KIDS",
    "music": "MUSIC",
    "series": "SERIES",
    "documentary": "DOC",
}

def detect_group(line):
    l = line.lower()
    country = "OTHER"
    category = "GENERAL"

    # Détection pays
    for key, val in COUNTRY_MAP.items():
        if f"{key}." in l or f"/{key}" in l or f"-{key}" in l:
            country = val
            break

    # Détection catégorie
    for key, val in CATEGORY_MAP.items():
        if key in l:
            category = val
            break

    return f"{country}-{category}"

def process(input_file, output_file):
    result = ["#EXTM3U\n"]
    counter = 1

    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            url = lines[i+1].strip() if i+1 < len(lines) else ""
            if not url.startswith("http"):
                i += 1
                continue
            group = detect_group(line + url)
            # Extraire nom existant ou générer
            name = "Channel_" + str(counter)
            if "," in line:
                name = line.split(",",1)[1].strip() or name
            result.append(f'#EXTINF:-1 group-title="{group}",{group}_{name}\n')
            result.append(url + "\n")
            counter += 1
            i += 2
        else:
            i += 1

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(result)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: clean.py <input_file> <output_file>")
        sys.exit(1)
    process(sys.argv[1], sys.argv[2])
