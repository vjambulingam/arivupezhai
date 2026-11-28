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

def clean_section(html_chunk, title_clean):
    chunk = html_chunk
    # remove footer notes if present
    chunk = re.sub(r'This file was last updated.*', '', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'Feel free to send any corrections.*', '', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'Project Madurai is an open.*', '', chunk, flags=re.I | re.DOTALL)
    chunk = re.sub(r'Details of Project Madurai.*', '', chunk, flags=re.I | re.DOTALL)
    
    # replace hr
    chunk = re.sub(r'<hr[^>]*>', '\n', chunk, flags=re.I)
    
    # replace br
    chunk = re.sub(r'<br\s*/?>[ \t]*\n?', '\n', chunk, flags=re.I)
    
    # normalize porul, vilakkam, kadhai churukkam
    chunk = re.sub(r'(?:\(இதன் பொருள்\)|பொருள்)\s*:\s*', '**பொருள்**: ', chunk)
    chunk = re.sub(r'(?:\(விளக்கம்\)|விளக்கம்)\s*:\s*', '**விளக்கம்**: ', chunk)
    chunk = re.sub(r'(?:\(கதைச் சுருக்கம்\)|கதைச் சுருக்கம்)\s*:\s*', '**கதைச் சுருக்கம்**: ', chunk)
    
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

total_chars = 0
for title, content, start, end in sections_def:
    chunk = content[start:end]
    cleaned = clean_section(chunk, title)
    total_chars += len(cleaned)
    print(f'{title}: {len(cleaned)} chars, start: {cleaned[:60]}...')

print(f'Total cleaned chars across all sections: {total_chars}')
