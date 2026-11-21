# Book Format Generator (EPUB & PDF)

Script to generate high-quality **EPUB3** and **PDF** files from book markdown (`.md`) files in `src/content/books/` using **Pandoc** and **Tectonic**.

## Key Features

1. **Embedded Tamil Fonts**:
   - Bundles and embeds Google Noto Tamil OpenType/TrueType fonts (`NotoSerifTamil-Regular.ttf`, `NotoSerifTamil-Bold.ttf`, `NotoSansTamil-Regular.ttf`, `NotoSansTamil-Bold.ttf`).
   - Fonts are fully embedded into the EPUB container via `--epub-embed-font` and into the PDF via XeTeX `fontspec`.
   - Ensures consistent, authentic rendering on all devices (Kindle, Apple Books, Kobo, Android, PDF readers) without tofu (`□`) or broken conjuncts.

2. **Preserved Hardline Breaks**:
   - Uses `markdown+hard_line_breaks` to preserve all poetic verses, stanzas, and line endings as written in the source markdown.

3. **Frontmatter Contributors on First Page**:
   - Automatically extracts `contributors` (or `acknowledgement`) from the markdown YAML frontmatter.
   - Formats and displays this block prominently on the **first page** in both EPUB and PDF formats:
     - **EPUB**: Rendered on the title page (`title_page.xhtml`) directly under the author block with custom styling (`.contributors`), title `பங்களிப்பாளர்கள் / பதிப்புரை`, and dark-mode adaptation.
     - **PDF**: Formatted inside a centered block with decorative horizontal rules directly beneath `\maketitle` on page 1 before the Table of Contents.
     - Preserves all multi-line contributor credits, names, organizations, and URLs.

4. **Auto-Generated Table of Contents (TOC)**:
   - Auto-detects whether the book requires **TOC depth 2 or 3**:
     - Large verse collections (like Thirukkural, Aathichudi, Nalvazhi) with thousands of numeric verses default to depth 2 (shows parts and chapters without cluttering with thousands of verse numbers).
     - Books with descriptive sub-sections default to depth 3.
     - Can also be explicitly overridden using `--toc-depth 2` or `--toc-depth 3`.
   - Uses authentic Tamil TOC title `பொருளடக்கம்`.

5. **Engineered for Compatibility**:
   - Uses **Pandoc** for structured EPUB3 generation with clean CSS and dark-mode support.
   - Uses **Tectonic** (modern self-contained XeTeX engine) for PDF generation with perfect Tamil OpenType ligature shaping and clean A4 margins.

6. **Book-Specific Covers**:
   - Generates a cover for each book using the site logo, the book title, and the author name from frontmatter.
   - Registers the cover in EPUB metadata for e-reader library views and renders the matching composition as the first page of the PDF.

---

## Prerequisites

- **Pandoc** (>= 2.19): `brew install pandoc`
- **Tectonic** (>= 0.15): `brew install tectonic`
- **Python 3**: Pre-installed on macOS.

---

## Usage

### 1. Generate both EPUB and PDF for a single book
Files are saved by default to `public/downloads/`:
```bash
python3 scripts/generate-book-formats.py src/content/books/AP001-thirukkural.md
# or using the shell wrapper:
./scripts/generate-book-formats.sh src/content/books/AP001-thirukkural.md
```

### 2. Generate only EPUB or only PDF
```bash
# Only EPUB
python3 scripts/generate-book-formats.py --format epub src/content/books/AP002-aathichudi.md

# Only PDF
python3 scripts/generate-book-formats.py --format pdf src/content/books/AP002-aathichudi.md
```

### 3. Specify custom output directory (default: `public/downloads`)
```bash
python3 scripts/generate-book-formats.py -o custom_output src/content/books/AP001-thirukkural.md
```

### 4. Override Table of Contents Depth
```bash
# Force depth 2
python3 scripts/generate-book-formats.py --toc-depth 2 src/content/books/AP035-ponniyin-selvan.md

# Force depth 3
python3 scripts/generate-book-formats.py --toc-depth 3 src/content/books/AP034-ndp-4.md
```

### 5. Generate for multiple books or all books
```bash
# Multiple specific books
python3 scripts/generate-book-formats.py src/content/books/AP001-thirukkural.md src/content/books/AP002-aathichudi.md

# All books in src/content/books/
python3 scripts/generate-book-formats.py --all
```

---

## Directory Layout

```
scripts/
├── generate-book-formats.py    # Main generator script
├── generate-book-formats.sh    # Executable shell wrapper
├── README.md                   # Documentation
├── assets/
│   ├── document.tex            # Pandoc LaTeX template with page 1 contributors block
│   ├── epub.css                # EPUB stylesheet with font embedding & dark mode
│   ├── epub3.html              # Pandoc EPUB3 template with title page contributors block
│   └── header.tex              # LaTeX/Tectonic fontspec and geometry header
└── fonts/
    ├── NotoSansTamil-Bold.ttf
    ├── NotoSansTamil-Regular.ttf
    ├── NotoSerifTamil-Bold.ttf
    └── NotoSerifTamil-Regular.ttf
```
