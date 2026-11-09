# அறிவுப்பேழை (Arivupezhai)
### செவ்வியல் தமிழ் இணைய நூலகம் • Classical Tamil Digital Library

> செவ்வியல் தமிழ் இலக்கியங்களை கணினி மற்றும் மொபைல் திரைகளில் கண் சோர்வின்றி மணிநேரக் கணக்கில் வாசிப்பதற்கென வடிவமைக்கப்பட்ட நவீன, திறந்த டிஜிட்டல் நூலகம்.

---

## 🌟 சிறப்பம்சங்கள் (Key Highlights)

- 📜 **முழுமையான முதல் நூல் - திருக்குறள்**: 
  - திருவள்ளுவரின் **133 அதிகாரங்கள் (1,330 குறட்பாக்கள்)** முழுமையாகப் பகுக்கப்பட்டு குறியிடப்பட்டுள்ளன.
  - முப்பால்கள் (அறத்துப்பால், பொருட்பால், காமத்துப்பால்) மற்றும் 9 இயல்களின் கீழ் முறைப்படுத்தப்பட்டுள்ளது.
- 🎨 **3 கண்-நல வண்ணத் தீம்கள் (Reading Themes)**:
  - **செப்பேடு (Temple Bronze - Default)**: சோழர் காலச் செப்பேடுகள் மற்றும் கோயில் மணற்கற்களின் இதமான வண்ணம் (`#F6F2EC` / `#AD5F1D`).
  - **இரவுக் கூடம் (Midnight Slate)**: இருண்ட சூழலில் கண் கூச்சத்தைத் தவிர்க்கும் மென்மையான சிலேட்டுப் பலகை வண்ணம் (`#17181B` / `#DE7851`).
  - **குறிஞ்சிக் குளிர் (Cool Mountain Mist)**: பனிமூட்டம் போன்ற குளுமையான நீல-சாம்பல் பின்னணியும், கூர்மையான நள்ளிரவு மை எழுத்துக்களும் (`#F0F4F8` / `#27567B`).
  - *எந்தப் பக்கத்திலிருந்தும் ஒரு கிளிக்கில் தீம்களை மாற்றலாம்; வாசகர் தேர்வு `localStorage`-இல் சேமிக்கப்படும்.*
- 🖋️ **செவ்வியல் தமிழ் எழுத்துருக்கள் (Tamil Typography)**:
  - செய்யுளுக்கு: `Noto Serif Tamil` மற்றும் `Mukta Malar`
  - உரை மற்றும் இடைமுகத்திற்கு: `Noto Sans Tamil`
  - கொம்பு (`ெ`, `ே`, `ை`), சுழி (`ி`, `ீ`, `ு`, `ூ`), மற்றும் புள்ளி (`்`) எழுத்துக்கள் வெட்டுப்படாமல் இருப்பதற்கென தாராளமான **1.8 முதல் 2.0 வரியிடைவெளி (line-height)**.
- 🔍 **உலகளாவிய உடனடித் தேடல் (Global Instant Search)**:
  - நூலின் பெயர், ஆசிரியர், வகை (Genre), அதிகாரம், மற்றும் குறள் வரிகளை நொடிப் பொழுதில் தேடலாம். விசைப்பலகை குறுக்குவழி: `/` அல்லது `Esc`.
- 📱 **தொடு-நட்பு நூலட்டை (Touch-friendly Book Cards)**:
  - பெரிய தொடு பரப்பளவுடன் கூடிய அட்டைகள்.
  - அட்டை வழியாக **நூல் விவரப் பக்கத்திற்கோ (Book Landing Page)** அல்லது **நேரடி வாசிப்புப் பக்கத்திற்கோ (Reader)** ஒரு தொடுதலில் செல்லலாம்.
- 📖 **வாசிப்புக் கூடம் (Dedicated Reader View)**:
  - எழுத்து அளவு மாற்றும் வசதி (`A-`, `100%`, `A+`).
  - வரியிடைவெளி மற்றும் எழுத்துரு மாற்றிகள்.
  - குறட்பாக்களை எளிதில் பகிர (WhatsApp / Social Share) மற்றும் நகலெடுக்க (Copy) வசதி.
  - முந்தைய / அடுத்த அதிகாரங்களுக்கான விசைப்பலகை (← / →) மற்றும் தொடு பொத்தான்கள்.
- 🚀 **GitHub Pages முழு தானியங்கி (CI/CD)**:
  - எந்த பின்தள சேவையகமும் (backend) இன்றி இயங்கும் தூய Static தளம்.
  - GitHub Actions வழியாக தானாக Build செய்யப்பட்டு GitHub Pages-இல் பதிவேற்றப்படும்.

---

## 📂 பக்கங்களின் அமைப்பு (Pages Structure)

| பாதை (Route) | விளக்கம் |
| :--- | :--- |
| `/` | முதன்மை நூலக அட்டவணை மற்றும் நூல் அட்டைகள் |
| `/palettes` | 3 வண்ணத் தீம்களை ஒப்பிட்டு தேர்வு செய்யும் மாதிரிப் பக்கம் |
| `/book/thirukkural` | திருக்குறள் நூல் முகப்பு, பால்கள், மற்றும் 133 அதிகாரங்களின் அட்டவணை |
| `/book/thirukkural/read/N/` | குறிப்பிட்ட அதிகாரத்திற்கான static வாசகர் பக்கம்; `#kural-N` மூலம் ஒரு குறளுக்கு நேரடியாகச் செல்லலாம் |
| `/book/thirukkural/read?athikaram=N` | பழைய இணைப்பு; JavaScript இயக்கத்தில் புதிய பக்கத்திற்குச் செல்லும். JavaScript இன்றி அதிகாரப் பட்டியல் காட்டப்படும். |

## Adding a book

Copy [`templates/book-template.md`](templates/book-template.md) to [`src/content/books/`](src/content/books/) and edit it. Use one UTF-8 `.md` or `.txt` file per book. Both extensions use the same Markdown format with YAML frontmatter. Each file is automatically included in the catalog, static reader, and full-text search during `npm run build`; no route or search-index code needs changing.

```markdown
---
id: example-book
title: எடுத்துக்காட்டு நூல்
title_en: Example Book
author: ஆசிரியர் பெயர்
author_en: Author Name
genre: இலக்கிய வகை
genre_en: Literature
category: தொகுப்பு
period: காலம்
description: நூல் பற்றிய சிறு விளக்கம்.
featured_quote: ஒரு சிறிய மேற்கோள்.
acknowledgement: உரையின் மூலம், பதிப்பு, நன்றி மற்றும் உரிமத் தகவல்.
pdf: null
epub: null
aliases:
  - Alternative title
---

# முதல் தொகுப்பு

## முதல் பகுதி {#first}

### முதல் பாடல் {#verse-1}

முதல் வரி
இரண்டாம் வரி

## இரண்டாம் பகுதி {#second}

இங்கு உரை அல்லது Markdown எழுதலாம்.
```

- `id`, `title`, `author`, `genre`, `description` and `acknowledgement` are required. Book IDs must be unique and use lowercase ASCII letters, numbers and hyphens.
- Each `##` heading creates a section page. Its `{#id}` is required, unique within the book and forms part of the URL; keep it stable after publication. A `#` heading groups subsequent sections. Optional `###` headings with `{#id}` create individually linkable passages; passage IDs must be unique within the book. Other Markdown headings and formatting are rendered as content. Plain text belongs under a section heading.
- `title_en`, `author_en`, `genre_en`, `category`, `period`, `featured_quote`, and `aliases` are optional. Aliases help search alternate names and transliterations.
- Leave `pdf` and `epub` as `null` until available. Later use an HTTPS URL or a site-root path such as `/downloads/book.pdf`; put local files under `public/downloads/`. Missing links are not displayed.
- If an ID matches an existing “coming soon” entry in `src/data/library.json`, the new book replaces that placeholder automatically. Keep the ID unchanged after publishing.
- [`thirukkural.md`](src/content/books/thirukkural.md) is the authoritative text for திருக்குறள். The older JSON is retained as a migration reference for regression tests; editing it does not change the site. `scripts/migrate_thirukkural.mjs` is a one-time migration tool and overwrites the Markdown file if rerun.
- Search uses Unicode NFC normalization. The index is generated at build time; its entries include every book, section and passage.

---

## 🛠️ தொழில்நுட்பக் கட்டமைப்பு (Tech Stack)

- **Framework**: [Astro](https://astro.build) (Static Site Generation)
- **Styling**: [Tailwind CSS v4](https://tailwindcss.com) (Modern CSS Variables & Utilities)
- **Fonts**: Google Fonts (`Noto Serif Tamil`, `Noto Sans Tamil`, `Mukta Malar`)
- **Analytics**: GoatCounter, loaded through the shared layout on all pages. Future book pages should use the same layout.
- **Hosting & CI/CD**: GitHub Pages (`.github/workflows/deploy.yml`)

---

## GitHub Pages deployment

The production site is configured for **https://arivupezhai.com/** at the domain root. Before the workflow can deploy:

1. In [repository Pages settings](https://github.com/vjambulingam/arivupezhai/settings/pages), enable GitHub Pages and select **GitHub Actions** as the build and deployment source.
2. In the same settings, set the custom domain to `arivupezhai.com` and save it. A `CNAME` file is not required for a custom GitHub Actions deployment; GitHub uses the repository Pages setting.
3. At the DNS provider, configure the apex (`@`) with GitHub Pages A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, and `185.199.111.153`. Remove conflicting records only after reviewing the existing DNS configuration.
4. Optionally add a `www` CNAME pointing to `vjambulingam.github.io` (without a repository path), then enable **Enforce HTTPS** in Pages settings once the certificate is ready.

See GitHub's [custom domain instructions](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) and [domain verification guidance](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/verifying-your-custom-domain-for-github-pages). DNS and certificate provisioning may take time. After pushing to `main`, check the workflow and open the domain once DNS resolves.

---

## 💻 உள்ளூர் கணினியில் இயக்குதல் (Local Development)

```bash
# 1. களஞ்சியத்தை குளோன் செய்க
git clone https://github.com/vjambulingam/arivupezhai.git
cd arivupezhai

# 2. சார்புகளை நிறுவுக
npm install

# 3. டெவலப்மென்ட் சர்வரை இயக்குக
npm run dev
# http://localhost:4321/

# 4. ஸ்டேடிக் தளத்தை Build செய்க
npm run build

# 5. Build மற்றும் static reader/search சோதனைகளை இயக்குக
npm test
```

---

## 📄 உரிமம் (License)

- அனைத்துச் செவ்வியல் தமிழ் இலக்கியப் பாடல்களும் பொதுக் களத்திற்கு (Public Domain) உட்பட்டவை.
