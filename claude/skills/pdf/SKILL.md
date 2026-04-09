---
name: pdf
version: 1.0.0
description: |
  Generate a polished PDF document from conversation context. Use when the user
  asks to create, export, or save findings, analysis, or reports as a PDF.
  Builds an HTML file styled for print, converts it to PDF via headless Chrome,
  and cleans up the intermediate HTML.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
user-invocable: true
argument-hint: "[output filename, e.g. report.pdf]"
---

# PDF: Generate a Print-Quality PDF Document

Create a polished, professional PDF from conversation context using HTML and headless Chrome.

## Input

The user provides:

- Content to include in the PDF (either from prior conversation context or by reference).
- Optionally, an output filename as `$ARGUMENTS`. Default to a descriptive kebab-case name with `.pdf` extension in the current working directory.

If the content or scope is unclear, ask the user what to include.

## Process

### 1. Plan the document

Before writing any HTML, outline the document structure:

- Identify the key sections and their hierarchy
- Determine which content benefits from tables, lists, or callout boxes
- Decide on a logical page-break strategy (avoid orphaned headings or split tables)

### 2. Write the HTML

Create a single self-contained HTML file (no external dependencies) at the target path with a `.html` extension. Follow these principles:

#### Page layout

- Use `@page { margin: 0.75in; size: letter; }` for print margins
- Add matching `padding: 0.75in` on `body` for screen preview
- Use `page-break-before: always` on section headings that should start a new page
- Avoid page breaks inside tables or callout boxes (`break-inside: avoid`)

#### Typography

- Use the system font stack: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`
- Use a monospace stack for code: `"SF Mono", Menlo, Consolas, monospace`
- Body text: 10.5pt, line-height 1.45
- Keep font sizes proportional: h1 ~20pt, h2 ~14pt, h3 ~11.5pt, body ~10.5pt, table cells ~9.5pt, file references ~8.5pt

#### Color and visual design

- Body text: `#1a1a1a` (near-black, not pure black)
- Headings: `#0a0a0a`
- Muted/reference text: `#555` or `#666`
- Tables: 1px `#d0d0d0` borders, `#f5f5f5` header background
- Use colored tags/badges for severity, status, or categories:
  - Resolved/success: green background (`#c3e6cb` / `#155724`)
  - Low: light green (`#d4edda` / `#155724`)
  - Medium: amber (`#fff3cd` / `#856404`)
  - High: light red (`#f8d7da` / `#721c24`)
  - Critical: dark red (`#721c24` / `#fff`)
  - Neutral/N/A: gray (`#e8e8e8` / `#666`)
- Use left-bordered callout boxes for summaries (4px left border, light background)

#### Content elements

- **Tables**: full-width, collapsed borders, compact padding (5-8px). Use for comparisons, matrices, and structured data.
- **Callout boxes**: left-bordered boxes for key takeaways, summaries, or important context. Use blue (`#0073aa`) for neutral, green (`#28a745`) for positive, amber (`#d39e00`) for warnings.
- **Code**: inline code with light gray background and monospace font. No syntax highlighting needed.
- **File references**: small muted text (`8.5pt, #666`) for source file paths.
- **Tags/badges**: inline `display: inline-block` spans with rounded corners, small font, colored backgrounds.

#### Structure conventions

- Include a title (`h1`), subtitle line with date, and a context/summary box at the top
- Add a table of contents for documents with 3+ sections
- Include a severity/status legend if using tags
- Add a footer with generation date and source references
- Keep all styles in a single `<style>` block in `<head>`

### 3. Convert to PDF

After writing the HTML, ask the user for permission to run the headless Chrome conversion command. Present the exact command you intend to run:

```
/Applications/Google Chrome.app/Contents/MacOS/Google Chrome \
  --headless --disable-gpu \
  --print-to-pdf="<output-path>.pdf" \
  --no-pdf-header-footer \
  "<input-path>.html"
```

If Chrome is not at this path, try:
- `google-chrome` (Linux)
- `chromium-browser` (Linux alternative)
- Ask the user for their Chrome path

Use a 30-second timeout for the conversion command.

### 4. Clean up

After conversion:

- Delete the intermediate `.html` file
- Verify the PDF was created and report its file size
- Report the output path to the user

## Quality checklist

Before converting, verify the HTML against these criteria:

- [ ] No external dependencies (fonts, CSS, images) -- everything is inline
- [ ] Tables have explicit column widths where needed to prevent awkward wrapping
- [ ] Page breaks are placed logically (before major sections, not mid-table)
- [ ] Content fits letter-size pages without horizontal overflow
- [ ] Tags/badges use sufficient contrast (WCAG AA)
- [ ] The document reads well as a standalone artifact (no "as discussed above" references to conversation)
- [ ] All claims include source references (file paths, PR numbers, etc.) where applicable

## Style notes

- Write in a professional, direct tone. Avoid filler language.
- Use sentence case for headings (not Title Case).
- Prefer tables over prose for structured comparisons.
- Use callout boxes sparingly -- one per section at most.
- Do not use emojis unless the user requests them.
