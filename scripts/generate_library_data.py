import os
import re
import json

os.makedirs('src/data/books', exist_ok=True)

with open('/tmp/pmuni0001.html', 'r', encoding='utf-8', errors='ignore') as f:
    raw = f.read()

raw = raw.replace('&nbsp;', ' ')
raw = raw.replace('<font color="blue"\n', '<font color="blue">\n')
raw = raw.replace('<br>>', '<br>')
raw = raw.replace('30</tr>', '30<br>')
raw = re.sub(r'(\s+)7811\s*<br>', r'\1 781<br>', raw)
raw = re.sub(r'(\s+)12983\s*<br>', r'\1 1293<br>', raw)

parts = re.split(r'<[hH]3[^>]*>(.*?)</[hH]3>', raw, flags=re.DOTALL)

def get_paal_info(athikaram_idx):
    if athikaram_idx <= 38:
        return {
            "name_ta": "அறத்துப்பால்",
            "name_en": "Book of Virtue",
            "slug": "arathuppal",
            "color": "amber"
        }
    elif athikaram_idx <= 108:
        return {
            "name_ta": "பொருட்பால்",
            "name_en": "Book of Wealth & Polity",
            "slug": "porutpal",
            "color": "emerald"
        }
    else:
        return {
            "name_ta": "காமத்துப்பால்",
            "name_en": "Book of Love",
            "slug": "kamathuppal",
            "color": "rose"
        }

def get_iyal_name(athikaram_idx):
    if athikaram_idx <= 4:
        return "பாயிரவியல்"
    elif athikaram_idx <= 24:
        return "இல்லறவியல்"
    elif athikaram_idx <= 37:
        return "துறவறவியல்"
    elif athikaram_idx == 38:
        return "ஊழியல்"
    elif athikaram_idx <= 63:
        return "அரசியல்"
    elif athikaram_idx <= 95:
        return "அங்கவியல்"
    elif athikaram_idx <= 108:
        return "ஒழிபியல்"
    elif athikaram_idx <= 115:
        return "களவியல்"
    else:
        return "கற்பியல்"

athikarams = []
total_kurals = 0

for i in range(1, len(parts), 2):
    heading_html = parts[i]
    content_html = parts[i+1] if i+1 < len(parts) else ""
    
    clean_h = re.sub(r'<[^>]+>', ' ', heading_html)
    clean_h = re.sub(r'\s+', ' ', clean_h).strip()
    
    m = re.search(r'(\d+[\.,]+\s*\d+[\.,]+\s*\d+)\s*(.*)', clean_h)
    if not m:
        continue
    code = m.group(1)
    name = m.group(2).strip()
    name = re.sub(r'^\d+(\.\d+)*\.?\s*', '', name).strip()
    name = re.sub(r'^[A-Za-z\s]+', '', name).strip()
    name = name.split('<')[0].strip()
    
    athikaram_idx = len(athikarams) + 1
    paal = get_paal_info(athikaram_idx)
    iyal = get_iyal_name(athikaram_idx)
    
    clean_c = re.sub(r'</?(?:tr|td|table|font|p|center|div)[^>]*>', '', content_html)
    lines = [l.strip() for l in clean_c.split('\n') if l.strip()]
    
    kurals = []
    buf = []
    for line in lines:
        if line.startswith('---') or 'Project Madurai' in line or 'www.projectmadurai.org' in line:
            break
        clean_line = re.sub(r'<br\s*/?>', '', line).strip()
        num_m = re.search(r'\s+(\d{1,4})\s*$', clean_line)
        if num_m:
            l2 = clean_line[:num_m.start()].strip()
            buf.append(l2)
            
            l1 = " ".join(buf[:-1]).strip()
            l2_final = buf[-1].strip()
            k_num = (athikaram_idx - 1) * 10 + len(kurals) + 1
            kurals.append({
                "number": k_num,
                "line1": l1,
                "line2": l2_final
            })
            buf = []
        else:
            if clean_line:
                buf.append(clean_line)
                
    total_kurals += len(kurals)
    athikarams.append({
        "number": athikaram_idx,
        "name_ta": name,
        "code": code,
        "paal": paal,
        "iyal": iyal,
        "start_kural": (athikaram_idx - 1) * 10 + 1,
        "end_kural": athikaram_idx * 10,
        "kurals": kurals
    })

thirukkural_book = {
    "id": "thirukkural",
    "title_ta": "திருக்குறள்",
    "title_en": "Thirukkural",
    "author_ta": "திருவள்ளுவர்",
    "author_en": "Thiruvalluvar",
    "genre_ta": "நீதி இலக்கியம்",
    "genre_en": "Ethical Literature",
    "category_ta": "பதினெண்கீழ்க்கணக்கு",
    "category_en": "Pathinenkilkanakku",
    "period_ta": "சங்க மருவிய காலம்",
    "period_en": "Post-Sangam Classical Era",
    "description_ta": "உலகப் பொதுமறை எனப் போற்றப்படும் திருக்குறள், திருவள்ளுவரால் அருளப்பட்ட உலகளாவிய வாழ்வியல் அறநூல். அறம், பொருள், இன்பம் என்ற முப்பால்களையும் 133 அதிகாரங்களில் 1,330 குறட்பாக்களாகத் திகழ்கிறது.",
    "description_en": "Celebrated worldwide as the Universal Veda of Humanity, Thirukkural synthesizes moral virtue, ethical governance, and profound human love into 1,330 immortal couplets across 133 chapters.",
    "is_available": True,
    "stats": {
        "paals_count": 3,
        "iyals_count": 9,
        "athikarams_count": len(athikarams),
        "kurals_count": total_kurals
    },
    "paals": [
        {
            "slug": "arathuppal",
            "name_ta": "அறத்துப்பால்",
            "name_en": "Book of Virtue",
            "description_ta": "மனிதனின் தனிப்பட்ட அறநெறி, இல்லற மாண்பு, துறவற மேன்மை மற்றும் ஊழின் விதியை உரைக்கும் பால்.",
            "start_athikaram": 1,
            "end_athikaram": 38,
            "athikarams_count": 38,
            "kurals_count": 380,
            "iyals": [
                {"name": "பாயிரவியல்", "athikarams": "1 - 4"},
                {"name": "இல்லறவியல்", "athikarams": "5 - 24"},
                {"name": "துறவறவியல்", "athikarams": "25 - 37"},
                {"name": "ஊழியல்", "athikarams": "38"}
            ]
        },
        {
            "slug": "porutpal",
            "name_ta": "பொருட்பால்",
            "name_en": "Book of Wealth & Governance",
            "description_ta": "அரசியல் நெறிகள், நல்லாட்சி, படை மாண்பு, நட்பியல், மற்றும் சமூக வாழ்க்கைக்கான வழிகாட்டுதல்கள்.",
            "start_athikaram": 39,
            "end_athikaram": 108,
            "athikarams_count": 70,
            "kurals_count": 700,
            "iyals": [
                {"name": "அரசியல்", "athikarams": "39 - 63"},
                {"name": "அங்கவியல்", "athikarams": "64 - 95"},
                {"name": "ஒழிபியல்", "athikarams": "96 - 108"}
            ]
        },
        {
            "slug": "kamathuppal",
            "name_ta": "காமத்துப்பால்",
            "name_en": "Book of Love",
            "description_ta": "அகவாழ்க்கையின் களவொழுக்கம், தலைவன் தலைவியர் காதல், ஊடல், பிரிவாற்றாமை முதலான நுட்பமான உணர்வுகள்.",
            "start_athikaram": 109,
            "end_athikaram": 133,
            "athikarams_count": 25,
            "kurals_count": 250,
            "iyals": [
                {"name": "களவியல்", "athikarams": "109 - 115"},
                {"name": "கற்பியல்", "athikarams": "116 - 133"}
            ]
        }
    ],
    "athikarams": athikarams
}

with open('src/data/books/thirukkural.json', 'w', encoding='utf-8') as f:
    json.dump(thirukkural_book, f, ensure_ascii=False, indent=2)

print("Wrote src/data/books/thirukkural.json")

# Create library catalog with Thirukkural + other classical treasures
library_catalog = [
    {
        "id": "thirukkural",
        "title_ta": "திருக்குறள்",
        "title_en": "Thirukkural",
        "author_ta": "திருவள்ளுவர்",
        "author_en": "Thiruvalluvar",
        "genre_ta": "நீதி இலக்கியம்",
        "genre_en": "Ethical Literature",
        "category_ta": "பதினெண்கீழ்க்கணக்கு",
        "period_ta": "சங்க மருவிய காலம்",
        "subsections_label": "133 அதிகாரங்கள் • 1,330 குறள்கள்",
        "featured_quote": "அகர முதல எழுத்தெல்லாம் ஆதி பகவன் முதற்றே உலகு.",
        "description_ta": "உலகப் பொதுமறை எனப் போற்றப்படும் திருக்குறள், அறம், பொருள், இன்பம் என்ற முப்பால்களையும் 133 அதிகாரங்களில் 1,330 குறட்பாக்களாகத் திகழ்கிறது.",
        "is_available": True,
        "badge_color": "terracotta",
        "stats": {
            "subsections": 133,
            "verses": 1330
        }
    },
    {
        "id": "tholkappiyam",
        "title_ta": "தொல்காப்பியம்",
        "title_en": "Tholkappiyam",
        "author_ta": "தொல்காப்பியர்",
        "author_en": "Tholkappiyar",
        "genre_ta": "இலக்கணம் & வாழ்வியல்",
        "genre_en": "Grammar & Poetics",
        "category_ta": "தொல்பழங்கால இலக்கணம்",
        "period_ta": "முச்சங்க காலம் (கி.மு. 5-ஆம் நூற்றாண்டு)",
        "subsections_label": "3 அதிகாரங்கள் • 27 இயல்கள்",
        "featured_quote": "எழுத்தெனப் படுப அகர முதல னகர இறுவாய் முப்பஃ தென்ப.",
        "description_ta": "தமிழின் மிகப் பழமையான முழுமையான இலக்கண நூல். எழுத்ததிகாரம், சொல்லதிகாரம், பொருளதிகாரம் என மொழி மற்றும் தமிழரின் அக-புற வாழ்வியலை வகுத்தளிக்கிறது.",
        "is_available": False,
        "badge_color": "sand",
        "stats": {
            "subsections": 27,
            "verses": 1610
        }
    },
    {
        "id": "silappadikaram",
        "title_ta": "சிலப்பதிகாரம்",
        "title_en": "Silappadikaram",
        "author_ta": "இளங்கோவடிகள்",
        "author_en": "Ilango Adigal",
        "genre_ta": "ஐம்பெருங் காப்பியம்",
        "genre_en": "Epic Literature",
        "category_ta": "காப்பியங்கள்",
        "period_ta": "சங்க மருவிய காலம் (கி.பி. 2-ஆம் நூற்றாண்டு)",
        "subsections_label": "3 காண்டங்கள் • 30 காதைகள்",
        "featured_quote": "அரசியல் பிழைத்தோர்க்கு அறங்கூற்றாவதூஉம் உரைசால் பத்தினியை உயர்ந்தோர் ஏத்தலும்...",
        "description_ta": "கண்ணகியின் கற்பின் மாண்பையும், பாண்டிய மன்னன் நெடுஞ்செழியனின் நீதி வழுவாமையையும் உரைக்கும் தமிழின் முதன்மைக் காப்பியம்.",
        "is_available": False,
        "badge_color": "copper",
        "stats": {
            "subsections": 30,
            "verses": 5270
        }
    },
    {
        "id": "purananuru",
        "title_ta": "புறநானூறு",
        "title_en": "Purananuru",
        "author_ta": "பல்வேறு சங்கப் புலவர்கள்",
        "author_en": "Sangam Poets",
        "genre_ta": "சங்க இலக்கியம்",
        "genre_en": "Sangam Poetry",
        "category_ta": "எட்டுத்தொகை",
        "period_ta": "சங்க காலம்",
        "subsections_label": "400 பாடல்கள் • புறத்திணை",
        "featured_quote": "யாதும் ஊரே யாவரும் கேளிர்; தீதும் நன்றும் பிறர்தர வாரா.",
        "description_ta": "பண்டைத் தமிழரின் வீரம், கொடை, நட்பு, பண்பாடு, மற்றும் மன்னர்களின் ஆட்சிச் சிறப்பை உரைக்கும் வரலாற்றுச் சுரங்கம்.",
        "is_available": False,
        "badge_color": "bronze",
        "stats": {
            "subsections": 400,
            "verses": 400
        }
    },
    {
        "id": "manimekalai",
        "title_ta": "மணிமேகலை",
        "title_en": "Manimekalai",
        "author_ta": "சீத்தலைச் சாத்தனார்",
        "author_en": "Seethalai Sathanar",
        "genre_ta": "ஐம்பெருங் காப்பியம்",
        "genre_en": "Epic Literature",
        "category_ta": "காப்பியங்கள்",
        "period_ta": "சங்க மருவிய காலம்",
        "subsections_label": "30 காதைகள் • பௌத்த அறம்",
        "featured_quote": "உண்டி கொடுத்தோர் உயிர் கொடுத்தோரே; உண்டி முதற்றே உணவின் பிண்டம்.",
        "description_ta": "சிலப்பதிகாரத்தின் தொடர்ச்சியாக, கோவலன்-மாதவியின் மகள் மணிமேகலை துறவு பூண்டு அமுதசுரபி கொண்டு பசிப்பிணி போக்கிய அறக்காப்பியம்.",
        "is_available": False,
        "badge_color": "copper",
        "stats": {
            "subsections": 30,
            "verses": 4758
        }
    },
    {
        "id": "naladiyar",
        "title_ta": "நாலடியார்",
        "title_en": "Naladiyar",
        "author_ta": "சமண முனிவர்கள்",
        "author_en": "Jain Ascetics",
        "genre_ta": "நீதி இலக்கியம்",
        "genre_en": "Ethical Literature",
        "category_ta": "பதினெண்கீழ்க்கணக்கு",
        "period_ta": "சங்க மருவிய காலம்",
        "subsections_label": "40 அதிகாரங்கள் • 400 வெண்பாக்கள்",
        "featured_quote": "கல்வி கரையில கற்பவர் நாள்சில மெல்ல நினைப்பின் பிணிபல.",
        "description_ta": "ஆலும் வேலும் பல்லுக்குறுதி, நாலும் இரண்டும் சொல்லுக்குறுதி என்ற பழமொழிக்குரிய, திருக்குறளுக்கு இணையான வாழ்வியல் அற நூல்.",
        "is_available": False,
        "badge_color": "terracotta",
        "stats": {
            "subsections": 40,
            "verses": 400
        }
    }
]

with open('src/data/library.json', 'w', encoding='utf-8') as f:
    json.dump(library_catalog, f, ensure_ascii=False, indent=2)

print("Wrote src/data/library.json")
