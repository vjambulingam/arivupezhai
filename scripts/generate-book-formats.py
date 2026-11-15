#!/usr/bin/env python3
"""
generate-book-formats.py

Generates EPUB and PDF files for a given book markdown (.md) file using
Pandoc and Tectonic, with embedded Tamil fonts, preserved hardline breaks,
and auto-generated Table of Contents (depth 2 or 3).

Usage:
    python3 scripts/generate-book-formats.py [options] <book.md> [book2.md ...]
    ./scripts/generate-book-formats.py [options] <book.md>

Examples:
    python3 scripts/generate-book-formats.py src/content/books/AP001-thirukkural.md
    python3 scripts/generate-book-formats.py --format pdf src/content/books/AP002-aathichudi.md
    python3 scripts/generate-book-formats.py --output-dir dist/downloads --all
"""

import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(SCRIPT_DIR, "fonts")
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")

NOTO_TAMIL_RELEASE_ZIPS = {
    "NotoSerifTamil": "https://github.com/notofonts/tamil/releases/download/NotoSerifTamil-v2.004/NotoSerifTamil-v2.004.zip",
    "NotoSansTamil": "https://github.com/notofonts/tamil/releases/download/NotoSansTamil-v2.004/NotoSansTamil-v2.004.zip",
}

REQUIRED_FONTS = [
    "NotoSerifTamil-Regular.ttf",
    "NotoSerifTamil-Bold.ttf",
    "NotoSansTamil-Regular.ttf",
    "NotoSansTamil-Bold.ttf",
]


def check_dependencies() -> None:
    """Verifies that pandoc and tectonic are installed and accessible."""
    missing = []
    if not shutil.which("pandoc"):
        missing.append("pandoc")
    if not shutil.which("tectonic"):
        missing.append("tectonic")

    if missing:
        print(f"Error: Required tool(s) not found in PATH: {', '.join(missing)}", file=sys.stderr)
        print("Please install them before running this script:", file=sys.stderr)
        print("  macOS (Homebrew): brew install pandoc tectonic", file=sys.stderr)
        print("  Ubuntu/Debian:    sudo apt install pandoc && curl --proto '=https' --tlsv1.2 -fsSL https://drop-sh.fullyjustified.net |sh", file=sys.stderr)
        sys.exit(1)


def ensure_tamil_fonts(target_fonts_dir: str = FONTS_DIR) -> Dict[str, str]:
    """
    Ensures Tamil font files are available in the fonts directory.
    If missing or subset-only, downloads the full Noto Tamil fonts with bilingual
    (Tamil + Latin/English) support from the official notofonts repository.
    """
    import zipfile
    import io

    os.makedirs(target_fonts_dir, exist_ok=True)

    # Check if all required fonts exist and are the full builds (>100KB with Latin)
    needs_serif = not (
        os.path.exists(os.path.join(target_fonts_dir, "NotoSerifTamil-Regular.ttf"))
        and os.path.getsize(os.path.join(target_fonts_dir, "NotoSerifTamil-Regular.ttf")) > 100_000
        and os.path.exists(os.path.join(target_fonts_dir, "NotoSerifTamil-Bold.ttf"))
        and os.path.getsize(os.path.join(target_fonts_dir, "NotoSerifTamil-Bold.ttf")) > 100_000
    )

    needs_sans = not (
        os.path.exists(os.path.join(target_fonts_dir, "NotoSansTamil-Regular.ttf"))
        and os.path.getsize(os.path.join(target_fonts_dir, "NotoSansTamil-Regular.ttf")) > 100_000
        and os.path.exists(os.path.join(target_fonts_dir, "NotoSansTamil-Bold.ttf"))
        and os.path.getsize(os.path.join(target_fonts_dir, "NotoSansTamil-Bold.ttf")) > 100_000
    )

    for family, needed in [("NotoSerifTamil", needs_serif), ("NotoSansTamil", needs_sans)]:
        if needed:
            zip_url = NOTO_TAMIL_RELEASE_ZIPS[family]
            print(f"Downloading full {family} package (bilingual Tamil + Latin)...")
            try:
                req = urllib.request.Request(zip_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req) as resp:
                    zip_data = resp.read()
                with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                    for member in z.namelist():
                        basename = os.path.basename(member)
                        if member.startswith(f"{family}/full/ttf/") and basename in REQUIRED_FONTS:
                            dest_path = os.path.join(target_fonts_dir, basename)
                            with z.open(member) as src_fp, open(dest_path, "wb") as dst_fp:
                                dst_fp.write(src_fp.read())
                            print(f"  ✓ Installed {basename}")
            except Exception as exc:
                print(f"Warning: Failed to download full {family}: {exc}", file=sys.stderr)

    font_paths = {
        font_name: os.path.join(target_fonts_dir, font_name)
        for font_name in REQUIRED_FONTS
        if os.path.exists(os.path.join(target_fonts_dir, font_name))
    }
    return font_paths


def parse_frontmatter(content: str) -> Tuple[Dict[str, str], str]:
    """
    Extracts YAML frontmatter from markdown content.
    Returns (metadata_dict, body_content).
    """
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", content, re.DOTALL)
    if not match:
        return {}, content

    yaml_block, body = match.group(1), match.group(2)
    metadata: Dict[str, str] = {}
    current_key = None

    for line in yaml_block.splitlines():
        # Match top-level key: value
        key_match = re.match(r"^([a-zA-Z0-9_-]+)\s*:\s*(.*)$", line)
        if key_match:
            current_key = key_match.group(1).strip()
            val = key_match.group(2).strip()
            # Strip surrounding quotes if present
            if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            val = val.replace("\\n", "\n")
            metadata[current_key] = val
        elif current_key and line.startswith("  "):
            # Multi-line string continuation
            metadata[current_key] += "\n" + line.strip()

    return metadata, body


def is_verse_heading(title: str) -> bool:
    """
    Checks if an h3 heading represents a numeric verse/pasuram or line number
    rather than a distinct thematic subsection.
    """
    clean = re.sub(r"\s*\{#[^}]+\}", "", title).strip()
    if re.match(r"^\d+$", clean):
        return True
    if re.match(r"^(?:குறள்|பாசுரம்|கண்ணி|பாடல்|வரி|அடி|verse|no\.?)\s*\d+", clean, re.IGNORECASE):
        return True
    return False


def determine_toc_depth(body: str, override_depth: Optional[int] = None) -> int:
    """
    Determines whether Table of Contents depth should be 2 or 3 based on the contents.
    - If override_depth is provided, uses it.
    - If non-verse level 3 headings exist, returns 3.
    - Otherwise returns 2.
    """
    if override_depth in (2, 3):
        return override_depth

    h3s = re.findall(r"^### (?!#)(.*)", body, re.MULTILINE)
    if not h3s:
        return 2

    non_verse_h3s = [h for h in h3s if not is_verse_heading(h)]
    # If more than 50% of h3s are descriptive section names (e.g. Acts, Scenes, Subsections)
    if len(non_verse_h3s) > 0 and len(non_verse_h3s) >= len(h3s) * 0.5:
        return 3

    return 2


def build_epub(
    input_file: str,
    output_file: str,
    toc_depth: int,
    fonts_dir: str,
    epub_css: str,
    contributors: str = "",
    verbose: bool = False
) -> bool:
    """Generates an EPUB3 file using Pandoc with embedded Tamil fonts and contributors on title page."""
    font_files = [
        os.path.join(fonts_dir, "NotoSerifTamil-Regular.ttf"),
        os.path.join(fonts_dir, "NotoSerifTamil-Bold.ttf"),
        os.path.join(fonts_dir, "NotoSansTamil-Regular.ttf"),
        os.path.join(fonts_dir, "NotoSansTamil-Bold.ttf"),
    ]

    epub_template = os.path.join(ASSETS_DIR, "epub3.html")

    cmd = [
        "pandoc",
        input_file,
        "-f", "markdown-blank_before_header+hard_line_breaks",
        "-t", "epub3",
        "--toc",
        f"--toc-depth={toc_depth}",
        "-M", "toc-title=பொருளடக்கம்",
        "-M", "lang=ta",
        f"--css={epub_css}",
    ]

    if os.path.exists(epub_template):
        cmd.append(f"--template={epub_template}")

    meta_yaml_path = None
    try:
        meta_dict = {}
        if contributors:
            meta_dict["contributors"] = contributors

        repo_root = os.path.dirname(SCRIPT_DIR)
        logo_path = os.path.join(repo_root, "public", "arivupezhai-logo.png")
        if not os.path.exists(logo_path):
            alt_path = os.path.abspath("public/arivupezhai-logo.png")
            if os.path.exists(alt_path):
                logo_path = alt_path

        if os.path.exists(logo_path):
            import base64
            with open(logo_path, "rb") as fp:
                logo_b64 = base64.b64encode(fp.read()).decode("ascii")
            meta_dict["logo_data_uri"] = f"data:image/png;base64,{logo_b64}"

        if meta_dict:
            meta_fd, meta_yaml_path = tempfile.mkstemp(suffix=".yaml", prefix="epub_meta_")
            with os.fdopen(meta_fd, "w", encoding="utf-8") as fp:
                for k, v in meta_dict.items():
                    if "\n" in str(v):
                        indented = "\n".join(("  " + line.strip()) if line.strip() else "" for line in str(v).splitlines())
                        fp.write(f"{k}: |\n{indented}\n")
                    else:
                        fp.write(f"{k}: \"{v}\"\n")
            cmd.append(f"--metadata-file={meta_yaml_path}")

        for f in font_files:
            if os.path.exists(f):
                cmd.append(f"--epub-embed-font={f}")

        cmd.extend(["-o", output_file])

        if verbose:
            print(f"Running Pandoc (EPUB): {' '.join(cmd)}")

        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            print(f"Error building EPUB for {input_file}:", file=sys.stderr)
            print(res.stderr, file=sys.stderr)
            return False

        return True
    finally:
        if meta_yaml_path and os.path.exists(meta_yaml_path):
            try:
                os.remove(meta_yaml_path)
            except OSError:
                pass


def build_pdf(
    input_file: str,
    output_file: str,
    toc_depth: int,
    fonts_dir: str,
    temp_dir: str,
    contributors: str = "",
    verbose: bool = False
) -> bool:
    """Generates a PDF file using Pandoc with Tectonic engine and contributors on first page."""
    norm_fonts_dir = os.path.abspath(fonts_dir) + "/"
    header_tex_path = os.path.join(temp_dir, "tectonic_header.tex")
    latex_template = os.path.join(ASSETS_DIR, "document.tex")

    # Check if bundled fonts are available, otherwise use system fallback
    has_bundled_fonts = all(
        os.path.exists(os.path.join(fonts_dir, f))
        for f in ["NotoSerifTamil-Regular.ttf", "NotoSansTamil-Regular.ttf"]
    )

    if has_bundled_fonts:
        font_config = f"""\\setmainfont[
  Path = {norm_fonts_dir},
  BoldFont = NotoSerifTamil-Bold.ttf,
  Script = Tamil,
  Language = Tamil
]{{NotoSerifTamil-Regular.ttf}}
\\setsansfont[
  Path = {norm_fonts_dir},
  BoldFont = NotoSansTamil-Bold.ttf,
  Script = Tamil,
  Language = Tamil
]{{NotoSansTamil-Regular.ttf}}
"""
    else:
        # System font fallback
        font_config = """\\setmainfont[Script = Tamil, Language = Tamil]{Tamil Sangam MN}
\\setsansfont[Script = Tamil, Language = Tamil]{Tamil MN}
"""

    header_tex = f"""\\usepackage{{fontspec}}
{font_config}
\\usepackage{{geometry}}
\\geometry{{
  a4paper,
  top=2.5cm,
  bottom=2.5cm,
  left=2.5cm,
  right=2.5cm
}}
\\usepackage{{setspace}}
\\setstretch{{1.25}}
\\usepackage{{hyperref}}
\\hypersetup{{
  colorlinks=true,
  linkcolor=black,
  urlcolor=blue,
  citecolor=black,
  pdfborder={{0 0 0}},
  pdflang={{ta}}
}}
\\raggedbottom
\\widowpenalty=10000
\\clubpenalty=10000
"""

    with open(header_tex_path, "w", encoding="utf-8") as fp:
        fp.write(header_tex)

    cmd = [
        "pandoc",
        input_file,
        "-f", "markdown-blank_before_header+hard_line_breaks",
        "--pdf-engine=tectonic",
        "--toc",
        f"--toc-depth={toc_depth}",
        "-M", "toc-title=பொருளடக்கம்",
        "-H", header_tex_path,
    ]

    if os.path.exists(latex_template):
        cmd.append(f"--template={latex_template}")

    meta_dict = {}
    if contributors:
        meta_dict["contributors"] = contributors

    repo_root = os.path.dirname(SCRIPT_DIR)
    logo_path = os.path.join(repo_root, "public", "arivupezhai-logo.png")
    if not os.path.exists(logo_path):
        alt_path = os.path.abspath("public/arivupezhai-logo.png")
        if os.path.exists(alt_path):
            logo_path = alt_path

    if os.path.exists(logo_path):
        meta_dict["logo_path"] = logo_path

    if meta_dict:
        meta_yaml_path = os.path.join(temp_dir, "meta_pdf.yaml")
        with open(meta_yaml_path, "w", encoding="utf-8") as fp:
            for k, v in meta_dict.items():
                if "\n" in str(v):
                    indented = "\n".join(("  " + line.strip()) if line.strip() else "" for line in str(v).splitlines())
                    fp.write(f"{k}: |\n{indented}\n")
                else:
                    fp.write(f"{k}: \"{v}\"\n")
        cmd.append(f"--metadata-file={meta_yaml_path}")

    cmd.extend(["-o", output_file])

    if verbose:
        print(f"Running Pandoc (PDF via Tectonic): {' '.join(cmd)}")

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error building PDF for {input_file}:", file=sys.stderr)
        print(res.stderr, file=sys.stderr)
        return False

    return True


def format_size(num_bytes: int) -> str:
    """Formats file size into human-readable string."""
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} TB"


def process_book(
    book_path: str,
    output_dir: str,
    target_format: str,
    toc_depth_override: Optional[int],
    fonts_dir: str,
    epub_css: str,
    verbose: bool = False
) -> Dict[str, Optional[str]]:
    """Processes a single book markdown file and produces EPUB and/or PDF."""
    if not os.path.isfile(book_path):
        print(f"Error: File not found: {book_path}", file=sys.stderr)
        return {"epub": None, "pdf": None}

    with open(book_path, "r", encoding="utf-8", errors="ignore") as fp:
        raw_content = fp.read()

    meta, body = parse_frontmatter(raw_content)
    title = meta.get("title", os.path.splitext(os.path.basename(book_path))[0])
    author = meta.get("author", "Unknown")
    slug = meta.get("slug") or meta.get("id") or os.path.splitext(os.path.basename(book_path))[0]
    contributors = meta.get("contributors") or meta.get("acknowledgement") or ""
    # Clean slug for filename
    base_name = re.sub(r"[^a-zA-Z0-9_\-\.]", "-", slug)

    toc_depth = determine_toc_depth(body, toc_depth_override)

    print(f"\n========================================================")
    print(f"Book:         {title} ({author})")
    print(f"Source:       {book_path}")
    print(f"TOC:          Depth {toc_depth} (auto-detected: {toc_depth_override is None})")
    if contributors:
        contrib_preview = contributors.replace("\n", " ").strip()
        if len(contrib_preview) > 60:
            contrib_preview = contrib_preview[:57] + "..."
        print(f"Contributors: {contrib_preview}")
    print(f"Output:       {output_dir}/")
    print(f"========================================================")

    os.makedirs(output_dir, exist_ok=True)
    epub_out = os.path.join(output_dir, f"{base_name}.epub")
    pdf_out = os.path.join(output_dir, f"{base_name}.pdf")

    results = {"epub": None, "pdf": None}

    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate EPUB
        if target_format in ("all", "epub"):
            print("→ Generating EPUB...")
            success = build_epub(
                input_file=book_path,
                output_file=epub_out,
                toc_depth=toc_depth,
                fonts_dir=fonts_dir,
                epub_css=epub_css,
                contributors=contributors,
                verbose=verbose
            )
            if success and os.path.exists(epub_out):
                size = format_size(os.path.getsize(epub_out))
                print(f"  ✓ EPUB created: {epub_out} ({size})")
                results["epub"] = epub_out

        # Generate PDF
        if target_format in ("all", "pdf"):
            print("→ Generating PDF (Tectonic)...")
            success = build_pdf(
                input_file=book_path,
                output_file=pdf_out,
                toc_depth=toc_depth,
                fonts_dir=fonts_dir,
                temp_dir=temp_dir,
                contributors=contributors,
                verbose=verbose
            )
            if success and os.path.exists(pdf_out):
                size = format_size(os.path.getsize(pdf_out))
                print(f"  ✓ PDF created:  {pdf_out} ({size})")
                results["pdf"] = pdf_out

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate EPUB and PDF files for Tamil book markdown files with embedded fonts and auto-TOC."
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Path to book markdown file(s) (e.g. src/content/books/AP001-thirukkural.md)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        default="public/downloads",
        help="Directory to save generated EPUB and PDF files (default: 'public/downloads')"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["all", "epub", "pdf"],
        default="all",
        help="Format(s) to generate (default: all)"
    )
    parser.add_argument(
        "--toc-depth",
        choices=["auto", "2", "3"],
        default="auto",
        help="Table of contents depth (default: auto, detects 2 or 3)"
    )
    parser.add_argument(
        "--fonts-dir",
        default=FONTS_DIR,
        help=f"Directory containing Tamil TTF fonts (default: {FONTS_DIR})"
    )
    parser.add_argument(
        "--css",
        default=os.path.join(ASSETS_DIR, "epub.css"),
        help="Custom CSS file for EPUB styling"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all books found in src/content/books/*.md"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output from Pandoc and Tectonic"
    )

    args = parser.parse_args()

    check_dependencies()
    ensure_tamil_fonts(args.fonts_dir)

    target_files = []
    if args.all:
        target_files = sorted(glob.glob("src/content/books/*.md"))
        if not target_files:
            print("No books found in src/content/books/*.md", file=sys.stderr)
            sys.exit(1)
    elif args.files:
        for pattern in args.files:
            matched = glob.glob(pattern)
            if matched:
                target_files.extend(matched)
            else:
                target_files.append(pattern)
    else:
        parser.print_help()
        sys.exit(0)

    toc_depth_val = None
    if args.toc_depth in ("2", "3"):
        toc_depth_val = int(args.toc_depth)

    generated_count = 0
    total_files = len(target_files)

    print(f"Starting format generation for {total_files} book(s)...")

    for idx, file_path in enumerate(target_files, 1):
        print(f"\n[{idx}/{total_files}] Processing {file_path}")
        res = process_book(
            book_path=file_path,
            output_dir=args.output_dir,
            target_format=args.format,
            toc_depth_override=toc_depth_val,
            fonts_dir=args.fonts_dir,
            epub_css=args.css,
            verbose=args.verbose
        )
        if res["epub"] or res["pdf"]:
            generated_count += 1

    print("\n========================================================")
    print(f"Finished: Successfully generated formats for {generated_count}/{total_files} book(s).")
    print(f"Output files stored in: {os.path.abspath(args.output_dir)}")
    print("========================================================")


if __name__ == "__main__":
    main()
