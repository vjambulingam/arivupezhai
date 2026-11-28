# -*- coding: utf-8 -*-
import os
import re

files = [
    '/tmp/civaka_cintamani/pmuni0664_01.html',
    '/tmp/civaka_cintamani/pmuni0664_02.html',
    '/tmp/civaka_cintamani/pmuni0670_01.html',
    '/tmp/civaka_cintamani/pmuni0670_02.html',
    '/tmp/civaka_cintamani/pmuni0672_01.html',
    '/tmp/civaka_cintamani/pmuni0672_02.html',
    '/tmp/civaka_cintamani/pmuni0672_03.html',
]

c1 = open(files[0], encoding='utf-8', errors='ignore').read()
c2 = open(files[1], encoding='utf-8', errors='ignore').read()
c3 = open(files[2], encoding='utf-8', errors='ignore').read()
c4 = open(files[3], encoding='utf-8', errors='ignore').read()
c5 = open(files[4], encoding='utf-8', errors='ignore').read()
c6 = open(files[5], encoding='utf-8', errors='ignore').read()
c7 = open(files[6], encoding='utf-8', errors='ignore').read()

def find_pos(content, pattern, start=0):
    m = re.search(pattern, content[start:])
    if m:
        return start + m.start()
    return -1

def clean_section(html_chunk):
    chunk = html_chunk
    # remove footer notes if present
    chunk = re.sub(r'This file was last updated.*', '', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'Feel free to send any corrections.*', '', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'Project Madurai is an open.*', '', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'Details of Project Madurai.*', '', chunk, flags=re.I | re.DOTALL)
    
    # Strip redundant heading at the very beginning of the slice
    chunk = re.sub(r'^\s*<(?:center|div|p)[^>]*>\s*<h[1-4][^>]*>[^<]*(?:இலம்பகம்|பதிகம்)[^<]*</h[1-4]>\s*</(?:center|div|p)>', '', chunk, flags=re.I)
    chunk = re.sub(r'^\s*<h[1-4][^>]*>[^<]*(?:இலம்பகம்|பதிகம்)[^<]*</h[1-4]>', '', chunk, flags=re.I)
    
    # replace hr
    chunk = re.sub(r'<hr[^>]*>', '\n', chunk, flags=re.I)
    
    # replace story summary headers
    chunk = re.sub(r'<strong>\s*(?:\(கதைச் சுருக்கம்\)|கதைச் சுருக்கம்)\s*[:\s]*</strong>\s*', '**கதைச் சுருக்கம்**: ', chunk, flags=re.I)
    chunk = re.sub(r'<b>\s*(?:\(கதைச் சுருக்கம்\)|கதைச் சுருக்கம்)\s*[:\s]*</b>\s*', '**கதைச் சுருக்கம்**: ', chunk, flags=re.I)
    chunk = re.sub(r'(?:\(கதைச் சுருக்கம்\)|கதைச் சுருக்கம்)\s*:\s*', '**கதைச் சுருக்கம்**: ', chunk)
    
    # normalize porul and vilakkam
    chunk = re.sub(r'(?:\(இதன் பொருள்\)|பொருள்)\s*:\s*', '**பொருள்**: ', chunk)
    chunk = re.sub(r'(?:\(விளக்கம்\)|விளக்கம்)\s*:\s*', '**விளக்கம்**: ', chunk)
    
    # replace br
    chunk = re.sub(r'<br\s*/?>[ \t]*\n?', '\n', chunk, flags=re.I)
    
    # handle strong / b
    chunk = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', chunk, flags=re.I | re.DOTALL)
    
    # handle headings
    chunk = re.sub(r'<h[1-4][^>]*>(.*?)</h[1-4]>', r'\n\n**\1**\n\n', chunk, flags=re.I | re.DOTALL)
    
    # strip other tags
    chunk = re.sub(r'<[^>]+>', ' ', chunk)
    
    # replace entities
    chunk = chunk.replace('&nbsp;', ' ')
    chunk = chunk.replace('&#169;', '©')
    chunk = chunk.replace('&quot;', '"')
    chunk = chunk.replace('&amp;', '&')
    chunk = chunk.replace('&lt;', '<')
    chunk = chunk.replace('&gt;', '>')
    
    # remove divider lines like ----------
    chunk = re.sub(r'^[-\s]{4,}$', '', chunk, flags=re.M)
    
    # normalize spaces per line
    lines = [re.sub(r'[ \t]+', ' ', l).strip() for l in chunk.split('\n')]
    
    # clean multiple blank lines
    res = []
    for l in lines:
        if l:
            res.append(l)
        elif res and res[-1] != '':
            res.append('')
            
    text = '\n'.join(res).strip()
    return text

sections_def = [
    ('## பதிகம் {#pathigam}', c1, find_pos(c1, r'<strong>\s*1\.\s*கடவுள் வாழ்த்து'), find_pos(c1, r'<h3>\s*1\.\s*நாமகள் இலம்பகம்')),
    ('## 1. நாமகள் இலம்பகம் {#namagal-ilambagam}', c1, find_pos(c1, r'<h3>\s*1\.\s*நாமகள் இலம்பகம்'), find_pos(c1, r'நாமகள் இலம்பகம்.*?முற்றியது')),
    ('## 2. கோவிந்தையார் இலம்பகம் {#govindhaiyar-ilambagam}', c2, find_pos(c2, r'<center><h3>\s*2\.\s*கோவிந்தையார் இலம்பகம்'), find_pos(c2, r'<center><h3>\s*3\.\s*காந்தருவ\s*தத்தையார்')),
    ('## 3. காந்தருவதத்தையார் இலம்பகம் {#kandharuvadathaiyar-ilambagam}', c2, find_pos(c2, r'<center><h3>\s*3\.\s*காந்தருவ\s*தத்தையார்'), find_pos(c2, r'காந்தருவ\s*தத்தையார் இலம்பகம் முற்றிற்று')),
    ('## 4. குணமாலையார் இலம்பகம் {#gunamalaiyar-ilambagam}', c3, 3640, 312331),
    ('## 5. பதுமையார் இலம்பகம் {#padhumaiyar-ilambagam}', c3, 312331, find_pos(c3, r'பதுமையார் இலம்பகம் முற்றிற்று')),
    ('## 6. கேமசரியார் இலம்பகம் {#kemasariyar-ilambagam}', c4, 3655, 150906),
    ('## 7. கனகமாலையார் இலம்பகம் {#kanagamalaiyar-ilambagam}', c4, 150906, find_pos(c4, r'கனகமாலையார் இலம்பகம்\s*முற்றும்')),
    ('## 8. விமலையார் இலம்பகம் {#vimalaiyar-ilambagam}', c5, 3733, 103734),
    ('## 9. சுரமஞ்சரியார் இலம்பகம் {#suramanjariyar-ilambagam}', c5, 103734, 214371),
    ('## 10. மண்மகள் இலம்பகம் {#manmagal-ilambagam}', c5, 214371, find_pos(c5, r'மண்மகள் இலம்பகம் முற்றும்')),
    ('## 11. பூமகள் இலம்பகம் {#poomagal-ilambagam}', c6, 3498, 54803),
    ('## 12. இலக்கணையார் இலம்பகம் {#ilakkanaiyar-ilambagam}', c6, 54803, find_pos(c6, r'இலக்கணையார் இலம்பகம் முற்றிற்று')),
    ('## 13. முத்தி இலம்பகம் {#muththi-ilambagam}', c7, 3597, find_pos(c7, r'முத்தி இலம்பகம் முற்றிற்று')),
]

frontmatter = """---
id: AP103
slug: civaka-cintamani
catalog_id: AP103
language: ta
title: சீவக சிந்தாமணி
title_en: Civaka Cintamani
author: திருத்தக்க தேவர் (பொ. வே. சோமசுந்தரனார் உரையுடன்)
author_en: Thiruthakka Devar & Po. Ve. Somasundaranar
genre: ஐம்பெருங் காப்பியம்
genre_en: Epic Literature
tags: ["காப்பியங்கள்", "ஐம்பெருங் காப்பியம்", "சீவக சிந்தாமணி", "திருத்தக்க தேவர்", "பொ. வே. சோமசுந்தரனார்", "சமணம்", "சங்க மருவிய காலம்"]
period: "கி.பி. 10-ஆம் நூற்றாண்டு"
description: தமிழின் தலைசிறந்த ஐம்பெருங் காப்பியங்களில் மூன்றாவதான சீவக சிந்தாமணி. திருத்தக்க தேவர் இயற்றிய இந்நூல், சீவகன் என்னும் ஒப்பற்ற தலைவனின் பிறப்பு, கல்வி, வீரம், கலைத்திறன், பல்வேறு நாடுகளின் இளவரசியரை மணந்த திருமணங்கள், இழந்த நாட்டைக் கட்டியங்காரனிடமிருந்து மீட்டெடுத்தல், இறுதியில் உலக நிலையாமையை உணர்ந்து துறவு பூண்டு வீடுபேறு அடைதல் ஆகிய முழுமையான வாழ்வியலை 13 இலம்பகங்களில் 3,145 பாடல்களால் பொ. வே. சோமசுந்தரனார் அவர்களின் அரிய விளக்கவுரையுடன் அழகுற விவரிக்கிறது.
featured_quote: மூவா முதலா உலகம் ஒரு மூன்றும் ஏத்தத் தாவாத இன்பம் தலை ஆயது தன்னின் எய்தி ஓவாது நின்ற குணத்து ஒள் நிதிச் செல்வன் என்ப தேவாதி தேவன் அவன் சேவடி சேர்தும் அன்றே.
contributors: "Source: Project Madurai (PM0664, PM0670, PM0672); Tamil Virtual Academy soft copy; HTML & PDF versions: Dr. K. Kalyanasundaram, Lausanne, Switzerland; Commentary: Po. Ve. Somasundaranar; Project Madurai team - https://www.projectmadurai.org"
pdf: /downloads/civaka-cintamani.pdf
epub: /downloads/civaka-cintamani.epub
aliases: ["சீவக சிந்தாமணி", "சீவகசிந்தாமணி", "திருத்தக்க தேவர்", "பொ. வே. சோமசுந்தரனார்", "திருத்தக்க தேவர் சோமசுந்தரனார் உரையுடன்", "Civaka Cintamani", "Seevaga Sinthamani", "Jivaka Chintamani", "Thiruthakka Devar", "Somasundaranar"]
---
"""

out_path = '/Users/venkatesh/arivupezhai/src/content/books/AP103-civaka-cintamani.md'
with open(out_path, 'w', encoding='utf-8') as out:
    out.write(frontmatter.strip())
    out.write('\n\n')
    for heading, content, start, end in sections_def:
        chunk = content[start:end]
        cleaned = clean_section(chunk)
        out.write(f'{heading}\n\n')
        out.write(cleaned)
        out.write('\n\n')

print(f'Successfully generated {out_path} ({os.path.getsize(out_path)} bytes)')
