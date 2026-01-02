# WifeyMOOC JSON to Paper Converter 📚

Convert your exercise JSON files into beautiful, printable HTML worksheets for paper-based learning.

## Overview

The `json_to_paper.py` script transforms your WifeyMOOC exercise JSON files into formatted HTML documents that you can fine-tune and print to PDF:

- 📋 **HTML Format** - Full control over pagination and styling
- 🎨 **Beautifully formatted** - Professional worksheet styling
- 📋 **Answer key included** - Automatic answer section at the end
- 🎲 **Smart randomization** - Images shuffled for match_sentence exercises
- 🖼️ **Embedded images** - All images included inline
- 🔊 **Media references** - Audio/video locations noted for reference
- ✏️ **Fully editable** - Edit HTML/CSS before printing to get perfect pagination
- 🚽 **No dependencies** - Just Python 3, no external libraries needed

## Installation

No special installation needed! Just Python 3.

```bash
# Make script executable (optional, on macOS/Linux)
chmod +x json_to_paper.py
```

## Usage

### Generate HTML Worksheet

```bash
python3 json_to_paper.py testfile-complete.json
```

This generates `testfile-complete_paper.html` in the same directory.

### Custom Output Filename

```bash
python3 json_to_paper.py testfile-complete.json my_worksheet.html
```

### Print to PDF

#### Method 1: Browser Print Dialog (Recommended)

1. Open the HTML file in your browser:
   ```bash
   # macOS
   open testfile-complete_paper.html
   
   # Linux
   xdg-open testfile-complete_paper.html
   
   # Windows
   start testfile-complete_paper.html
   ```

2. Press **Ctrl+P** (Windows/Linux) or **Cmd+P** (macOS)

3. Choose **Save as PDF** or your printer

4. **Important print settings:**
   - Page size: **A4** (or Letter)
   - Margins: **Default** (the stylesheet handles spacing)
   - Background graphics: **ON** (for colors/images)
   - Scale: **100%** (don't shrink)

5. Click **Save** or **Print**

#### Method 2: Edit & Fine-tune Before Printing

Since you have full HTML control, you can:

1. Open `testfile-complete_paper.html` in a text editor
2. Find problematic exercises (e.g., `categorization_multiple` breaking pages)
3. Adjust the CSS styling:
   ```css
   .categorization-item {
       margin: 12px 0;
       padding: 12px;
       background: white;
       border: 1px solid #dee2e6;
       break-inside: avoid;  /* Prevents page breaks within item */
   }
   ```
4. Add `break-after: avoid;` to keep related sections together
5. Reduce margins or padding if needed
6. Save and print

## Features

### Supported Question Types

| Type | Display | Features |
|------|---------|----------|
| `mcq_single` | Multiple choice (single) | Radio buttons for selection |
| `mcq_multiple` | Multiple choice (multiple) | Checkboxes for multi-select |
| `list_pick` | List selection | Checkboxes for multiple items |
| `fill_blanks_dropdown` | Fill in blanks | Blank lines for answers |
| `match_phrases` | Match beginning/ending | Two-column matching format |
| `match_sentence` | Match sentences to images | **Randomized image grid** |
| `order_phrase` | Ordering/sequencing | Numbered spaces for ordering |
| `categorization_multiple` | Categorization | Items with category options |
| `word_fill` | Word fill in context | Sentence with blank spaces |
| `sequence_audio` | Audio sequencing | Items to order with audio note |
| `image_tagging` | Label a diagram | Tag list with image reference |
| `multi_questions` | Multiple questions together | Sub-questions in one exercise |

### Smart Match Sentence Feature 🎲

For `match_sentence` exercises:
- **Images are displayed in random order** with letter labels (A, B, C, D...)
- **Sentences appear below** without revealing which image matches which sentence
- Each time you run the script, images shuffle differently
- Answer key shows the correct mappings

Example layout:
```
Images:
┌──────────────────────────────────────┐
│ (A)         (B)         (C)    (D)   │
│[Image]    [Image]    [Image] [Image]│
└──────────────────────────────────────┘

Match sentences with images:
1. French sentence... ____
2. French sentence... ____
3. French sentence... ____
4. French sentence... ____
```

## Pagination Tips

### Preventing Page Breaks

If an exercise or section breaks across pages unexpectedly:

**In the HTML/CSS:**
```css
.exercise {
    break-inside: avoid;  /* Keeps entire exercise on one page */
}

.pairs-list {
    break-inside: avoid;  /* Keeps matching list intact */
}
```

**In browser print dialog:**
- Lower the `margin` values slightly
- Increase the `scale` from 100% to 102%
- Reduce font size by 1-2px

### Forcing Page Breaks

If you want a new page before the answer key:
```css
.answers-section {
    break-before: page;  /* Already in default stylesheet */
}
```

### Compact Layouts

The `categorization_multiple` renderer has been optimized to show all items together with a shared category list to prevent blank pages.

## Troubleshooting

### File not found error

```
✗ Error: File 'myfile.json' not found
```

**Solution**: Provide the correct path:
```bash
python3 json_to_paper.py /full/path/to/myfile.json
```

### Images not appearing in HTML

**Solution**:
1. Check that image files exist relative to JSON location
2. Images should be in a subfolder like `images/` next to your JSON
3. Check file paths in your JSON are correct

Directory structure:
```
my_project/
├── testfile-complete.json
├── images/
│   ├── image1.jpg
│   └── image2.png
└── audios/
    └── audio1.mp3
```

### JSON parsing error

**Solution**: Validate your JSON:
- Use [jsonlint.com](https://jsonlint.com)
- Check for missing commas
- Verify all brackets match
- No trailing commas in arrays

### Weird page breaks when printing

**Solutions**:
1. Open HTML in different browser (Chrome handles print better)
2. Adjust CSS margins/padding before problem exercises
3. Use print preview to identify exact break points
4. Add CSS rules for specific exercises

## Workflow Examples

### Quick Worksheet Generation

```bash
# Generate
python3 json_to_paper.py unit1.json

# Open in browser
open unit1_paper.html

# Print (Cmd+P) → Save as PDF
```

### Edit & Perfect Layout

```bash
# Generate
python3 json_to_paper.py unit1.json

# Edit HTML for pagination
open -a TextEdit unit1_paper.html  # or your editor

# Adjust CSS as needed, save

# Open updated version in browser
open unit1_paper.html

# Print to PDF
```

### Batch Processing

```bash
#!/bin/bash
for file in data/*.json; do
    output="worksheets/$(basename $file .json)_worksheet.html"
    python3 json_to_paper.py "$file" "$output"
    echo "Generated: $output"
done
```

## CSS Customization

All styling is in the `<style>` section of the HTML. Common tweaks:

### Reduce Margins
```css
body {
    padding: 10px;  /* was 20px */
}

.exercise {
    margin-bottom: 15px;  /* was 25px */
}
```

### Make Text Smaller
```css
html {
    font-size: 12px;  /* was 14px */
}
```

### Change Colors
```css
.exercise-number {
    background: #2ecc71;  /* green instead of blue */
}
```

### Adjust Image Sizes
```css
.media-image img {
    max-height: 200px;  /* was 250px */
}

.image-item img {
    max-height: 100px;  /* was 120px */
}
```

## Printing Best Practices

- 📏 **Paper**: A4 (210 × 297 mm) or Letter
- 🖨️ **Colors**: Print in color for best visual experience
- 📏 **Quality**: High quality for images
- 🞨️ **Font**: Default fonts work great, no special fonts needed
- 📋 **Margins**: Keep default or reduce slightly if needed
- 💭 **Preview**: Always use print preview to check pagination

## Tips for Teachers

### Multiple Versions
```bash
# Generate 3 different versions with shuffled match_sentence images
python3 json_to_paper.py exercises.json version_A.html
python3 json_to_paper.py exercises.json version_B.html
python3 json_to_paper.py exercises.json version_C.html
```

### Removing Answer Key from Student Version

1. Open HTML in text editor
2. Find `<div class="answers-section">`
3. Delete from there to the closing `</div>`
4. Save as `student_version.html`
5. Print to PDF

### Creating Answer Key Only

1. Open HTML in text editor
2. Delete everything from `<div class="exercise">` to just before `<div class="answers-section">`
3. Save and print

## Contributing

To add support for new question types:

1. Add a new rendering method in the `ExerciseToPaper` class
2. Add a case in the `_exercise_to_html()` method
3. Test with your JSON file
4. Submit improvements!

## License

Same as WifeyMOOC (WTFPL)

## Support

For issues or suggestions, open an issue on the repository! 👋

---

**Ready to create your worksheets? Print and learn! 📚✏️**
