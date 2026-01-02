# WifeyMOOC JSON to Paper Converter 📚

Convert your exercise JSON files into beautiful, printable HTML worksheets for paper-based learning.

## Overview

The `json_to_paper.py` script transforms your WifeyMOOC exercise JSON files into formatted HTML documents that are:

- 💷 **Print-friendly** - Optimized CSS for clean paper output
- 🎨 **Beautifully formatted** - Professional worksheet styling
- 📑 **Answer key included** - Automatic answer section at the end
- 📚 **Supports all question types** - MCQ, fill-blanks, matching, ordering, categorization, and more
- 💤 **No internet needed** - Works completely offline

## Installation

No dependencies needed! This script uses only Python 3's built-in modules.

```bash
# Make it executable (on macOS/Linux)
chmod +x json_to_paper.py
```

## Usage

### Basic Usage

```bash
python3 json_to_paper.py testfile-complete.json
```

This will generate `testfile-complete_paper.html` in the same directory.

### Custom Output Filename

```bash
python3 json_to_paper.py testfile-complete.json my_worksheet.html
```

### Print to PDF

1. Open the HTML file in your browser:
   ```bash
   open testfile-complete_paper.html  # macOS
   # or
   start testfile-complete_paper.html # Windows
   # or
   xdg-open testfile-complete_paper.html # Linux
   ```

2. Press `Ctrl+P` (or `Cmd+P` on Mac) to open the print dialog
3. Select "Save as PDF" or your printer
4. Adjust settings as needed (margins, page orientation, etc.)
5. Print or save!

## Features

### Supported Question Types

| Type | Display | Features |
|------|---------|----------|
| `mcq_single` | Multiple choice (single) | Radio buttons for selection |
| `mcq_multiple` | Multiple choice (multiple) | Checkboxes for multi-select |
| `list_pick` | List selection | Checkboxes for multiple items |
| `fill_blanks_dropdown` | Fill in blanks | Blank lines for answers |
| `match_phrases` | Match beginning/ending | Two-column matching format |
| `match_sentence` | Match sentences to images | Lists with image references |
| `order_phrase` | Ordering/sequencing | Numbered spaces for ordering |
| `categorization_multiple` | Categorization | Items with category options |
| `word_fill` | Word fill in context | Sentence with blank spaces |
| `sequence_audio` | Audio sequencing | Items to order with audio note |
| `image_tagging` | Label a diagram | Tag list with image reference |
| `multi_questions` | Multiple questions together | Sub-questions in one exercise |

### HTML Output Features

- **Visual hierarchy**: Question numbers, types, and formatting
- **Media notes**: Icons and references for videos, audio, and images
- **Answer key**: Separate section at the end (easy to remove for student copies!)
- **Print optimization**: Page breaks, spacing, and font sizing
- **Responsive design**: Works on different screen sizes before printing

## Example Workflow

### For Teachers

```bash
# Create student worksheet (no answers)
python3 json_to_paper.py unit1-exercises.json unit1-student.html
# Print or save as PDF for students

# Create answer key
python3 json_to_paper.py unit1-exercises.json unit1-answers.html
# Print for your reference
```

### For Students

```bash
# Generate worksheet for practice
python3 json_to_paper.py practice-set.json
# Open in browser, print, and complete on paper
# Check answers from the included answer key
```

## Customization

### Colors and Styling

The script uses a default color scheme optimized for printing. To customize:

1. Open the generated HTML file in a text editor
2. Find the `<style>` section
3. Modify colors, fonts, and spacing as needed

Key CSS variables you can change:
- `#3498db` - Primary blue (questions, numbering)
- `#2c3e50` - Dark text and borders
- `#27ae60` - Green (answer section)
- `#e74c3c` - Red (answer key header)

### Answer Key

To remove the answer key from student worksheets:

1. Open the HTML file in a text editor
2. Find the section with `class="answers-section"`
3. Delete everything from `<div class="answers-section">` to the closing `</div>`
4. Save and print

## Tips for Best Results

### Printing

- 💴 **Paper**: Use 80-100 gsm white paper for best results
- 📐 **Font**: Print with default font (Segoe UI or system sans-serif)
- 📷 **Margins**: Use default or 0.5" (1.27cm) margins
- 💪 **Ink**: Use economy/draft mode to save ink
- 🚵 **Pages**: Check "Shrink to page width" if needed

### Organization

```bash
# Organize by unit
mkdir -p worksheets/unit1 worksheets/unit2
python3 json_to_paper.py data/unit1.json worksheets/unit1/exercises.html
python3 json_to_paper.py data/unit2.json worksheets/unit2/exercises.html
```

## Troubleshooting

### File not found error

```
✗ Error: File 'myfile.json' not found
```

**Solution**: Make sure the JSON file is in the same directory or provide the full path:

```bash
python3 json_to_paper.py /full/path/to/myfile.json
```

### JSON parsing error

```
✗ Error: Invalid JSON
```

**Solution**: Validate your JSON file:
- Use [jsonlint.com](https://jsonlint.com) to check syntax
- Ensure all commas and quotes are correct
- Verify all bracket pairs match

### HTML doesn't look right

**Solution**: Try opening in a different browser:
- Chrome/Edge: Best compatibility
- Firefox: Good support
- Safari: Should work fine

### Questions not displaying

**Solution**: The question type might not be fully formatted yet. Check the `_exercise_to_html()` method in the script and add support or report an issue.

## Advanced Usage

### Batch Processing

Create a bash script to process multiple files:

```bash
#!/bin/bash
for file in data/*.json; do
    python3 json_to_paper.py "$file" "output/$(basename $file .json)_worksheet.html"
done
```

### Integration with Other Tools

The HTML output can be:
- Converted to PDF using tools like `wkhtmltopdf`
- Imported into Word or Google Docs
- Embedded in web pages
- Processed with other HTML manipulation tools

## Contributing

To add support for new question types:

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

For issues or feature requests, please open an issue on the repository! 🙋

---

**Happy printing! 💫🖥️**
