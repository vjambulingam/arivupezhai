# -*- coding: utf-8 -*-
import os
import re

c62 = open('/tmp/valayapathi/pmuni0062.html', encoding='utf-8', errors='ignore').read()
c549 = open('/tmp/valayapathi/pmuni0549.html', encoding='utf-8', errors='ignore').read()

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

munnurai_raw = c62[2434:9479]
padhippurai_raw = c549[2461:4435]
anindhurai_raw = c549[4435:8536]
verses_raw = c549[8629:160982]

munnurai = strip_leading_title(clean_html(munnurai_raw), 'முன்னுரை')
padhippurai = strip_leading_title(clean_html(padhippurai_raw), 'பதிப்புரை')
anindhurai = strip_leading_title(clean_html(anindhurai_raw), 'அணிந்துரை')
verses = clean_html(verses_raw)

frontmatter = """---
id: AP104
slug: valayapathi
catalog_id: AP104
language: ta
title: வளையாபதி
title_en: Valayapathi
author: ஆசிரியர் பெயர் அறியப்படவில்லை (பொ. வே. சோமசுந்தரனார் உரையுடன்)
author_en: Unknown (Commentary by Po. Ve. Somasundaranar)
genre: ஐம்பெருங் காப்பியம்
genre_en: Epic Literature
tags: ["காப்பியங்கள்", "ஐம்பெருங் காப்பியம்", "வளையாபதி", "பொ. வே. சோமசுந்தரனார்", "சமணம்", "சங்க மருவிய காலம்"]
period: "கி.பி. 9-ஆம் நூற்றாண்டு"
description: ஐம்பெருங் காப்பியங்களுள் நான்காவதான வளையாபதி. கால வெள்ளத்தில் முழுமையாகக் கிடைக்காமல் மறைந்துபோன இந்நூலில், புறத்திரட்டு முதலான உரைகளில் மேற்கோள்களாகக் கிடைத்துள்ள 72 அரிய செய்யுட்களும், பெரியண்ணன் சந்திரசேகரன் அவர்களின் ஆய்வு முன்னுரையும், சைவசித்தாந்த நூற்பதிப்புக் கழகப் பதிப்புரை, அணிந்துரை மற்றும் பெருமழைப் புலவர் பொ. வே. சோமசுந்தரனார் அவர்களின் அரிய விளக்கவுரையும் ஒருங்கே தொகுக்கப்பெற்றுள்ளன.
featured_quote: உலகம் மூன்றும் ஒருங்குடன் ஏத்துமாண் திலகம் ஆய திறல் அறி வன் அடி வழுவில் நெஞ்சொடு வாலிதின் ஆற்றவும் தொழுவல் தொல்வினை நீங்குக என்று யான்.
contributors: "Source: Project Madurai (PM0062 & PM0549); Etext Preparation: Mr. Periannan Chandrasekaran (Atlanta) & Tamil Virtual Academy; HTML & PDF versions: Dr. K. Kalyanasundaram (Lausanne); Commentary: Po. Ve. Somasundaranar; Project Madurai team - https://www.projectmadurai.org"
pdf: /downloads/valayapathi.pdf
epub: /downloads/valayapathi.epub
aliases: ["வளையாபதி", "Valayapathi", "Valaiyapathi", "Valaiyapati", "பொ. வே. சோமசுந்தரனார்"]
---
"""

out_path = '/Users/venkatesh/arivupezhai/src/content/books/AP104-valayapathi.md'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(frontmatter.strip())
    f.write('\n\n')
    
    f.write('## முன்னுரை {#munnurai}\n\n')
    f.write(munnurai)
    f.write('\n\n')
    
    f.write('## பதிப்புரை {#padhippurai}\n\n')
    f.write(padhippurai)
    f.write('\n\n')
    
    f.write('## அணிந்துரை {#anindhurai}\n\n')
    f.write(anindhurai)
    f.write('\n\n')
    
    f.write('## வளையாபதி செய்யுள்களும் உரையும் {#padalkalum-uraiyum}\n\n')
    f.write(verses)
    f.write('\n')

print(f'Successfully generated {out_path} ({os.path.getsize(out_path)} bytes)')
