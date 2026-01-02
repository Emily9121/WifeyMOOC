# WifeyMOOC JSON to Paper Converter 📚

Convert your exercise JSON files into beautiful, printable HTML worksheets AND editable DOCX documents for paper-based learning.

## Overview

The `json_to_paper.py` script transforms your WifeyMOOC exercise JSON files into TWO formats:

### HTML Output (🖨️ For Printing)
- Professional HTML formatting
- Full control over pagination (CSS editable)
- Ready to print to PDF
- Browser print dialog for final tweaking

### DOCX Output (✏️ For Editing)
- Native Word document (A4 format)
- Fully editable before printing
- Easy to adjust layout, fonts, spacing
- Professional formatting built-in
- Share with colleagues for collaboration

## Features

✅ **Dual Output** - Both HTML and DOCX generated in one command  
✅ **A4 Formatting** - Proper page sizes and margins  
✅ **Smart Image Handling** - MCQs reference full-page images  
✅ **Randomized Match Sentences** - Images shuffled for better pedagogy  
✅ **Answer Key Included** - Automatic answer section at the end  
✅ **Embedded Images** - All images included inline (no external files)  
✅ **Media References** - Audio/video locations noted  
✅ **Professional Styling** - Color-coded, well-organized layout  

## Installation

### Step 1: Basic Setup (HTML only)
Python 3 only - no dependencies needed:
```bash
cd path/to/WifeyMOOC
python3 json_to_paper.py testfile-complete.json
```

### Step 2: Full Setup (HTML + DOCX)
For DOCX support, install `python-docx`:

```bash
pip install python-docx
```

Then run as normal:
```bash
python3 json_to_paper.py testfile-complete.json
```

## Usage

### Generate Both HTML and DOCX

```bash
python3 json_to_paper.py testfile-complete.json
```

Generates:
- `testfile-complete_paper.html` (browser/print)
- `testfile-complete_paper.docx` (Word editing)

### Custom Output Names

```bash
python3 json_to_paper.py testfile-complete.json my_worksheet
```

Generates:
- `my_worksheet_paper.html`
- `my_worksheet_paper.docx`

## Workflow: HTML vs DOCX

### 🖨️ HTML Workflow (Print-Ready)

**Best for:** Final printing, minimal editing, quick PDF generation

1. Generate: `python3 json_to_paper.py file.json`
2. Open HTML in browser: `open file_paper.html`
3. Print to PDF: Cmd+P → Save as PDF
4. Adjust if needed: Edit CSS in HTML file, reload browser

### ✏️ DOCX Workflow (Editing & Customization)

**Best for:** Heavy editing, layout tweaks, sharing with team

1. Generate: `python3 json_to_paper.py file.json`
2. Open DOCX: Double-click `file_paper.docx` (opens in Word/LibreOffice)
3. Edit freely:
   - Change fonts, sizes, colors
   - Adjust spacing and margins
   - Reorder content
   - Add/remove questions
   - Insert your school logo
4. Print or export to PDF from Word

### 🔄 Recommended Combined Workflow

**For production worksheets:**

```
1. Generate both formats
   python3 json_to_paper.py exercises.json
   ↓
2. Check HTML preview in browser
   open exercises_paper.html
   ↓
3. If pagination looks good → Print HTML to PDF ✓
   ↓
4. If you need edits → Use DOCX for customization
   open exercises_paper.docx
   → Make changes
   → Print/Export to PDF from Word
```

## Installation Troubleshooting

### Missing python-docx

```
⚠️  Warning: python-docx not installed. Install with: pip install python-docx
```

**Solution:**
```bash
pip install python-docx

# If that fails, try:
pip3 install python-docx

# On Mac with Homebrew Python:
python3 -m pip install python-docx
```

### File not found error

```
✗ Error: File 'myfile.json' not found
```

**Solution:** Provide the correct path:
```bash
python3 json_to_paper.py /full/path/to/myfile.json
python3 json_to_paper.py ./data/myfile.json
```

### Images not appearing

**In HTML:** Use browser print preview (Cmd+P or Ctrl+P) to check

**In DOCX:** 
1. Image files must exist at the paths specified in JSON
2. Check image paths are correct:
   ```
   my_project/
   ├── testfile-complete.json
   ├── images/
   │   ├── image1.jpg
   │   └── image2.png
   ```
3. In JSON, use relative paths:
   ```json
   "media": {
     "image": "images/image1.jpg"
   }
   ```

## Features by Exercise Type

| Type | HTML | DOCX | Notes |
|------|------|------|-------|
| `mcq_single` | ✓ | ✓ | References full-page images |
| `mcq_multiple` | ✓ | ✓ | References full-page images |
| `list_pick` | ✓ | ✓ | References full-page images |
| `fill_blanks_dropdown` | ✓ | ✓ | Blank lines for answers |
| `match_phrases` | ✓ | ✓ | Two-column format |
| `match_sentence` | ✓ | ✓ | **Randomized images** |
| `order_phrase` | ✓ | ✓ | Numbered ordering |
| `categorization_multiple` | ✓ | ✓ | Items with categories |
| `word_fill` | ✓ | ✓ | Sentence with blanks |
| `sequence_audio` | ✓ | ✓ | Audio sequencing |
| `image_tagging` | ✓ | ✓ | Diagram labeling |
| `multi_questions` | ✓ | ✓ | Multiple sub-questions |

## Formatting & Styling

### DOCX Formatting

The generated DOCX includes:
- ✓ A4 page size with 0.75" margins
- ✓ Professional color-coded headers (blue for questions, purple for images, red for answers)
- ✓ Proper spacing and typography
- ✓ Formatted lists and bullet points
- ✓ Embedded images (no broken links)

### Editing in Word/LibreOffice

**Font changes:**
1. Select all (Ctrl+A)
2. Change font in toolbar
3. Adjust size as needed

**Page breaks:**
1. Click where you want break
2. Insert → Page Break

**Add school logo:**
1. Insert → Pictures
2. Choose your logo
3. Resize and position

**Change colors:**
1. Select text
2. Home → Font Color
3. Choose your school colors

## Advanced: Batch Processing

### Generate multiple files at once:

```bash
#!/bin/bash
# process_all_units.sh

for json_file in data/*.json; do
    base=$(basename "$json_file" .json)
    echo "Processing: $base"
    python3 json_to_paper.py "$json_file" "output/$base"
done

echo "✓ All worksheets generated!"
ls output/*.docx  # Show generated DOCX files
```

Run:
```bash
chmod +x process_all_units.sh
./process_all_units.sh
```

## Printing Tips

### From HTML (via Browser)

1. Open `file_paper.html` in browser
2. **Cmd+P** (Mac) or **Ctrl+P** (Windows/Linux)
3. Settings:
   - Destination: "Save as PDF" (or your printer)
   - Paper size: **A4** (or Letter)
   - Margins: Default
   - Background graphics: **ON** (for colors)
   - Scale: **100%**
4. Click **Save** or **Print**

### From DOCX (via Word)

1. Open `file_paper.docx` in Word
2. **Cmd+P** (Mac) or **Ctrl+P** (Windows)
3. Choose:
   - Printer: Your printer (or "Save as PDF")
   - Paper: **A4**
   - Orientation: **Portrait**
   - Margins: **Normal**
4. Click **Print**

### Best Practices

- ✅ Use A4 or Letter paper size
- ✅ Print in color for best visual experience
- ✅ Check print preview before printing
- ✅ Test on one page first
- ✅ Use high-quality paper for student worksheets

## JSON Structure Requirements

### Minimal Example

```json
[
  {
    "type": "mcq_single",
    "question": "What is 2+2?",
    "options": ["3", "4", "5"],
    "answer": "4",
    "media": {
      "image": "images/math_problem.jpg"
    }
  }
]
```

### With Full Media

```json
[
  {
    "type": "match_sentence",
    "question": "Match sentences to images",
    "pairs": [
      {
        "sentence": "The cat is sleeping",
        "image_path": "images/sleeping_cat.jpg"
      }
    ],
    "answer": {"sentence_1": "image_1"},
    "media": {
      "audio": "audios/pronunciation.mp3"
    }
  }
]
```

## Comparing Outputs

| Aspect | HTML | DOCX |
|--------|------|------|
| **Edit Format** | CSS + HTML | Word document |
| **Ease of Edit** | Intermediate | Easy |
| **Special Features** | CSS control, browser print | Native Word tools |
| **Share with Team** | Copy HTML file | Share .docx directly |
| **Print Quality** | Excellent | Excellent |
| **Add Images Later** | HTML editing | Drag & drop |
| **Add Logo** | CSS modification | Insert menu |
| **Batch Export** | Via print dialog | Word "Save As" |

## File Organization

**Recommended structure:**

```
WifeyMOOC/
├── json_to_paper.py
├── PAPER_PRINTING_GUIDE.md
├── data/
│   ├── unit1.json
│   ├── unit2.json
│   └── images/
│       ├── image1.jpg
│       ├── image2.png
│       └── ...
├── worksheets/
│   ├── unit1_paper.html
│   ├── unit1_paper.docx
│   ├── unit2_paper.html
│   └── unit2_paper.docx
└── audios/
    ├── audio1.mp3
    └── ...
```

## Troubleshooting

### DOCX won't open

- Install Microsoft Word or LibreOffice
- Try opening with different app
- Check file isn't corrupted (regenerate)

### Images blurry in DOCX

- DOCX shrinks images to fit page
- Open original image in "Insert > Picture" for better quality
- Or regenerate with original high-res images

### Formatting lost when opening DOCX

- DOCX uses Word's built-in styles
- Some formatting may vary by Word version
- Regenerate if needed

### HTML pagination issues

- Open in different browser (Chrome handles CSS printing better)
- Reduce margins in print dialog
- Edit CSS in HTML file for fine control

## Examples & Templates

Check the repository for example JSON files and generated worksheets:
- `examples/mcq_unit.json` → MCQ questions with images
- `examples/mixed_types.json` → Various question types
- `examples/matching_unit.json` → Matching exercises

## Contributing

To add features or fix issues:

1. Test with your JSON files
2. Submit improvements with examples
3. Check both HTML and DOCX output

## License

Same as WifeyMOOC (WTFPL)

---

**Ready to create professional worksheets? Pick your format and start! 📚✏️**
