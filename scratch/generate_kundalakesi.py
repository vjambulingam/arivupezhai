# -*- coding: utf-8 -*-
import os
import re

c = open('/tmp/kundalakesi/pmuni0507.html', encoding='utf-8', errors='ignore').read()

def clean_html(chunk):
    # remove hr
    chunk = re.sub(r'<hr[^>]*>', '\n', chunk, flags=re.I)
    # replace br
    chunk = re.sub(r'<br\s*/?>[ \t]*\n?', '\n', chunk, flags=re.I)
    # normalize porul and vilakkam
    chunk = re.sub(r'(?:\(இதன் பொருள்\)|பொருள்)\s*:\s*', '**பொருள்**: ', chunk)
    chunk = re.sub(r'(?:\(இதன் பொருள்\)|பொருள்)\s*\.\s*', '**பொருள்**: ', chunk)
    chunk = re.sub(r'(?:\(விளக்கம்\)|விளக்கம்)\s*:\s*', '**விளக்கம்**: ', chunk)
    chunk = re.sub(r'(?:\(விளக்கம்\)|விளக்கம்)\s*\.\s*', '**விளக்கம்**: ', chunk)
    # handle strong / b
    chunk = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', chunk, flags=re.I | re.DOTALL)
    # handle headings
    chunk = re.sub(r'<h[1-4][^>]*>(.*?)</h[1-4]>', r'\n\n**\1**\n\n', chunk, flags=re.I | re.DOTALL)
    # strip other tags
    chunk = re.sub(r'<[^>]+>', ' ', chunk)
    # entities
    chunk = chunk.replace('&nbsp;', ' ').replace('&#169;', '©').replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # divider lines
    chunk = re.sub(r'^[-\s]{4,}$', '', chunk, flags=re.M)
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in chunk.split('\n')]
    res = []
    for l in lines:
        if l: res.append(l)
        elif res and res[-1] != '': res.append('')
    return '\n'.join(res).strip()

def strip_leading_title(text, marker):
    lines = text.split('\n')
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            idx += 1
            continue
        clean_line = line.replace('*', '').strip()
        if marker in clean_line:
            idx += 1
            continue
        break
    return '\n'.join(lines[idx:]).strip()

p_m = re.search(r'<center><h4>பதிப்புரை</h4></center>', c)
a_m = re.search(r'<center><h4>அணிந்துரை\s*</h4></center>', c)
v_m = re.search(r'<strong>\s*1\.\s*கடவுள் வாழ்த்து</strong>', c)
v_end = c.find('குண்டலகேசி என்னும் பெருங்காப்பியத்தின்கண்')
v_end_full = c.find('</ul>', v_end)

padhippurai = strip_leading_title(clean_html(c[p_m.start():a_m.start()]), 'பதிப்புரை')
anindhurai = strip_leading_title(clean_html(c[a_m.start():v_m.start()]), 'அணிந்துரை')
verses = clean_html(c[v_m.start():v_end_full])

frontmatter = """---
id: AP105
slug: kundalakesi
catalog_id: AP105
language: ta
title: குண்டலகேசி
title_en: Kundalakesi
author: நாதகுத்தனார் (பொ. வே. சோமசுந்தரனார் விளக்கவுரையுடன்)
author_en: Nagaguthanaar & Po. Ve. Somasundaranar
genre: ஐம்பெருங் காப்பியம்
genre_en: Epic Literature
tags: ["காப்பியங்கள்", "ஐம்பெருங் காப்பியம்", "குண்டலகேசி", "பொ. வே. சோமசுந்தரனார்", "நாதகுத்தனார்", "பௌத்தம்", "சங்க மருவிய காலம்"]
period: "கி.பி. 10-ஆம் நூற்றாண்டுக்கு முன்"
description: தமிழின் தலைசிறந்த ஐம்பெருங் காப்பியங்களில் ஐந்தாவதான குண்டலகேசி. பௌத்த சமய அறநெறிகளையும் தத்துவங்களையும் விளக்கும் இக்காப்பியத்தை நாதகுத்தனார் இயற்றினார். கால வெள்ளத்தால் முழுநூல் மறைந்துவிட்ட போதிலும், நீலகேசி உரை முதலானவற்றில் மேற்கோள்களாக எஞ்சி நின்று கிடைத்துள்ள 19 அரிய செய்யுட்களும், சைவசித்தாந்த நூற்பதிப்புக் கழகப் பதிப்புரை, விரிவான ஆராய்ச்சி அணிந்துரை மற்றும் பெருமழைப் புலவர் பொ. வே. சோமசுந்தரனார் அவர்களின் அரிய விளக்கவுரைகளும் ஒருங்கே தொகுக்கப்பெற்றுள்ளன.
featured_quote: முன்றான் பெருமைக்கண் நின்றான்முடி வெய்து காறு நன்றே நினைந்தான் குணமேமொழிந் தான்ற னக்கென் றொன்றானு முள்ளான் பிறர்க்கேயுறு திக்கு ழந்தான் அன்றே யிறைவ னவன்றாள்சர ணாங்க ளன்றே.
contributors: "Source: Project Madurai (PM0507); Tamil Virtual Academy soft copy; HTML & PDF versions: Dr. K. Kalyanasundaram (Lausanne); Commentary: Po. Ve. Somasundaranar; Project Madurai team - https://www.projectmadurai.org"
pdf: /downloads/kundalakesi.pdf
epub: /downloads/kundalakesi.epub
aliases: ["குண்டலகேசி", "Kundalakesi", "Kuntalakeci", "பொ.வே. சோமசுந்தரனார்", "பொ.வே. சோமசுந்தரனார் (விளக்கவுரை)", "நாதகுத்தனார்", "Nagaguthanaar", "Somasundaranar"]
---
"""

out_path = '/Users/venkatesh/arivupezhai/src/content/books/AP105-kundalakesi.md'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(frontmatter.strip())
    f.write('\n\n')
    
    f.write('## பதிப்புரை {#padhippurai}\n\n')
    f.write(padhippurai)
    f.write('\n\n')
    
    f.write('## அணிந்துரை {#anindhurai}\n\n')
    f.write(anindhurai)
    f.write('\n\n')
    
    f.write('## குண்டலகேசி செய்யுள்களும் உரையும் {#padalkalum-uraiyum}\n\n')
    f.write(verses)
    f.write('\n')

print(f'Successfully generated {out_path} ({os.path.getsize(out_path)} bytes)')
