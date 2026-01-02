# WifeyMOOC JSON to Paper Converter 📚

Convert your exercise JSON files into beautiful, printable PDF worksheets (A4 format) for paper-based learning.

## Overview

The `json_to_paper.py` script transforms your WifeyMOOC exercise JSON files into professional PDF documents that are:

- 📄 **A4 PDF Format** - Ready to print directly
- 🎨 **Beautifully formatted** - Professional worksheet styling
- 📋 **Answer key included** - Automatic answer section at the end
- 🎲 **Smart randomization** - Images shuffled for match_sentence exercises
- 🖼️ **Embedded images** - All images included inline in PDF
- 🔊 **Media references** - Audio/video locations noted for reference
- 🖨️ **Print-optimized** - Perfect spacing and sizing for A4 paper
- 💾 **Fallback HTML** - Can generate HTML if PDF library not available

## Installation

### 1. Install Python Dependencies

```bash
# Install weasyprint for PDF generation
pip install weasyprint

# On macOS (if you have Homebrew issues):
brew install weasyprint
```

### 2. Make Script Executable (Optional)

```bash
# On macOS/Linux
chmod +x json_to_paper.py
```

## Usage

### Basic Usage - Generate PDF

```bash
python3 json_to_paper.py testfile-complete.json
```

This will generate `testfile-complete_paper.pdf` in the same directory.

### Custom Output Filename

```bash
python3 json_to_paper.py testfile-complete.json my_worksheet.pdf
```

### Printing

1. The PDF is ready to print directly:
   ```bash
   # On macOS
   open testfile-complete_paper.pdf
   
   # On Linux
   xdg-open testfile-complete_paper.pdf
   
   # On Windows
   start testfile-complete_paper.pdf
   ```

2. Use your PDF viewer's print function
3. Settings should default to A4 paper size

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
- Each PDF generation produces a **different random order**
- Answer key shows the correct mappings

Example layout:
```
Images:
┌─────────────────────────────────┐
│ (A)        │ (B)        │ (C)   │
│  [Image]   │  [Image]   │[Image]│
└─────────────────────────────────┘

Match sentences with images:
1. French text... _____
2. French text... _____
3. French text... _____
```

## PDF Output Details

### Page Format
- **Size**: A4 (210 × 297 mm)
- **Margins**: 1cm on all sides
- **Line height**: Optimized for readability
- **Font**: Segoe UI system fonts

### Answer Key
- Appears on separate page
- Clearly marked with red header
- Shows all answers in indexed format

## Troubleshooting

### ImportError: No module named 'weasyprint'

**Solution**: Install weasyprint
```bash
pip install weasyprint
```

If you have issues installing weasyprint:
- On macOS: Use `brew install weasyprint`
- On Linux (Ubuntu): Install system dependencies first:
  ```bash
  sudo apt-get install python3-pip python3-cffi python3-brlapi python3-dev
  pip install weasyprint
  ```

### File not found error

```
✗ Error: File 'myfile.json' not found
```

**Solution**: Make sure the JSON file is in the same directory or provide the full path:
```bash
python3 json_to_paper.py /full/path/to/myfile.json
```

### Images not appearing in PDF

**Possible causes:**
1. Image files not found - check file paths in JSON
2. Image paths are relative to JSON location
3. Supported formats: JPG, PNG, GIF, WebP, SVG

**Solution**: Place images in a subdirectory relative to your JSON:
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

```
✗ Error: Invalid JSON
```

**Solution**: Validate your JSON file:
- Use [jsonlint.com](https://jsonlint.com) to check syntax
- Ensure all commas and quotes are correct
- Verify all bracket pairs match
- Check for trailing commas in arrays/objects

### Slow PDF generation

**Solution**: This is normal for large files with many images. First generation may take 10-30 seconds.

## Workflow Examples

### For Teachers

```bash
# Create student worksheet
python3 json_to_paper.py unit1-exercises.json unit1-student.pdf

# Print for students
open unit1-student.pdf
# Ctrl+P to print, or save to cloud for digital distribution

# Create answer key
python3 json_to_paper.py unit1-exercises.json unit1-answers.pdf
```

### Batch Processing

Create a bash script `batch_convert.sh`:

```bash
#!/bin/bash
for file in data/*.json; do
    output="output/$(basename $file .json)_worksheet.pdf"
    python3 json_to_paper.py "$file" "$output"
    echo "Generated: $output"
done
```

Run with:
```bash
chmod +x batch_convert.sh
./batch_convert.sh
```

## Tips for Best Results

### Printing Settings

- 📏 **Paper**: A4 (210 × 297 mm) - default setting
- 🔤 **Font**: Use default fonts (already optimized)
- 📏 **Margins**: Default margins are perfect for binding
- 🖨️ **Color**: Use color for best visual experience with images
- 📊 **Quality**: High quality recommended for images

### File Organization

```bash
# Organize worksheets by unit
mkdir -p worksheets/{unit1,unit2,unit3}

python3 json_to_paper.py data/unit1.json worksheets/unit1/exercises.pdf
python3 json_to_paper.py data/unit2.json worksheets/unit2/exercises.pdf
```

### Creating Matched Sets

```bash
# Generate multiple versions with randomized match_sentence
python3 json_to_paper.py exercises.json version_A.pdf
python3 json_to_paper.py exercises.json version_B.pdf
python3 json_to_paper.py exercises.json version_C.pdf

# Each will have different image orders!
```

## Advanced Usage

### Editing PDF Styling

To customize colors or fonts, edit the `<style>` section in the Python script:

```python
# Find this section in generate_pdf():
css = CSS(string="""
    @page {
        size: A4;
        margin: 1cm;
    }
""")

# You can add additional CSS rules here
```

### Custom Page Setup

For different paper sizes, modify the CSS:

```python
# A3 size
size: A3;

# Letter size (US)
size: Letter;

# Custom size
size: 210mm 297mm;
```

## Known Limitations

- **Answer key format**: Shows raw JSON answer values (may need manual interpretation for complex answers)
- **Special HTML characters**: Some special characters in questions may need escaping
- **Very large files**: PDFs with 100+ questions may take several minutes
- **Memory**: Large image files may require significant memory

## Performance

- **Small files** (1-20 questions): < 2 seconds
- **Medium files** (20-50 questions): 5-10 seconds
- **Large files** (50+ questions): 10-30+ seconds

Speed depends on:
- Number of images
- Image file sizes
- Image complexity (SVG slower than JPG)
- System resources

## Updates and Contributing

To add support for new question types or improve formatting:

1. Add a new method in `ExerciseToPaper` class:
   ```python
   def _render_mytype(self, exercise: Dict) -> str:
       """Render mytype exercise"""
       # Your rendering code here
   ```

2. Add a case in `_exercise_to_html()` method:
   ```python
   elif ex_type == 'mytype':
       html += self._render_mytype(exercise)
   ```

3. Test with your JSON file

## License

Same as WifeyMOOC (WTFPL)

## Support

For issues or feature requests, please open an issue on the repository! 👋

---

**Ready to print? Happy learning! 📚✏️**
