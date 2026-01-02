#!/usr/bin/env python3
"""
WifeyMOOC JSON to Paper Exercise Printer
Converts exercise JSON files into printable HTML format (print to PDF manually)
"""

import json
import os
import sys
import base64
import random
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple

class ExerciseToPaper:
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.exercises = []
        self.base_dir = Path(json_file).parent
        self.load_json()
        
    def load_json(self):
        """Load and parse the JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.exercises = json.load(f)
            print(f"✓ Loaded {len(self.exercises)} exercises from {self.json_file}")
        except FileNotFoundError:
            print(f"✗ Error: File '{self.json_file}' not found")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Error: Invalid JSON - {e}")
            sys.exit(1)
    
    def _load_image_as_base64(self, image_path: str) -> str:
        """Load an image file and convert to base64 data URI"""
        try:
            # Try to find the image relative to the JSON file's directory
            full_path = self.base_dir / image_path
            if not full_path.exists():
                # Try relative to current directory
                full_path = Path(image_path)
            
            if not full_path.exists():
                print(f"⚠️  Warning: Image not found - {image_path}")
                return None
            
            # Determine MIME type
            suffix = full_path.suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml'
            }
            mime_type = mime_types.get(suffix, 'image/jpeg')
            
            # Read and encode image
            with open(full_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            return f"data:{mime_type};base64,{image_data}"
        except Exception as e:
            print(f"⚠️  Warning: Could not load image {image_path} - {e}")
            return None
    
    def generate_html(self, output_file: str = None) -> str:
        """Generate HTML document for printing"""
        if output_file is None:
            output_file = Path(self.json_file).stem + "_paper.html"
        
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WifeyMOOC - Exercise Worksheet</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html {
            font-size: 14px;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.5;
            color: #333;
            background: white;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 15px;
            break-after: avoid;
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 5px;
            font-size: 2em;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        
        .exercise {
            margin-bottom: 25px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            break-inside: avoid;
        }
        
        .exercise-number {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-weight: bold;
            margin-bottom: 8px;
            font-size: 0.85em;
        }
        
        .exercise-type {
            display: inline-block;
            background: #ecf0f1;
            color: #2c3e50;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.75em;
            margin-left: 8px;
            font-weight: 600;
        }
        
        .question {
            font-size: 1.05em;
            margin: 12px 0;
            font-weight: 500;
            color: #2c3e50;
        }
        
        .media-note {
            background: #fff3cd;
            border-left: 3px solid #ffc107;
            padding: 8px 12px;
            margin: 10px 0;
            font-size: 0.85em;
            color: #856404;
        }
        
        .media-image {
            margin: 12px 0;
            text-align: center;
            border: 1px solid #dee2e6;
            padding: 10px;
            border-radius: 4px;
            background: #f8f9fa;
            break-inside: avoid;
        }
        
        .media-image img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            display: inline-block;
            max-height: 250px;
        }
        
        .media-image-caption {
            font-size: 0.8em;
            color: #7f8c8d;
            margin-top: 6px;
            font-style: italic;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
            margin: 12px 0;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 4px;
            break-inside: avoid;
        }
        
        .image-item {
            border: 1px solid #dee2e6;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
            background: white;
            break-inside: avoid;
        }
        
        .image-item img {
            max-width: 100%;
            height: auto;
            max-height: 120px;
            margin-bottom: 8px;
        }
        
        .image-label {
            font-weight: bold;
            color: #2c3e50;
            font-size: 0.9em;
        }
        
        .option-list {
            margin: 10px 0;
            padding-left: 15px;
        }
        
        .option {
            margin: 8px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 3px;
            border-left: 2px solid #dee2e6;
            font-size: 0.95em;
        }
        
        .option input[type="checkbox"],
        .option input[type="radio"] {
            margin-right: 8px;
            cursor: pointer;
            accent-color: #3498db;
        }
        
        .option label {
            cursor: pointer;
            user-select: none;
        }
        
        .sentence-parts {
            background: #f8f9fa;
            padding: 12px;
            border-radius: 4px;
            margin: 10px 0;
            line-height: 1.8;
            font-size: 0.95em;
            break-inside: avoid;
        }
        
        .answer-space {
            border-bottom: 1.5px solid #2c3e50;
            display: inline-block;
            min-width: 120px;
            margin: 0 4px;
            height: 18px;
        }
        
        .pairs-list {
            margin: 10px 0;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 4px;
            break-inside: avoid;
        }
        
        .pair {
            margin: 8px 0;
            padding: 8px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            font-size: 0.95em;
        }
        
        .pair-source {
            font-weight: 500;
            color: #2c3e50;
            flex: 1;
            min-width: 150px;
        }
        
        .pair-target {
            color: #7f8c8d;
            flex: 0 1 35%;
            text-align: right;
            margin-left: 10px;
            font-size: 0.9em;
        }
        
        .categorization-item {
            margin: 12px 0;
            padding: 12px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            break-inside: avoid;
        }
        
        .categorization-item img {
            max-width: 100%;
            max-height: 150px;
            margin: 10px 0;
            border-radius: 3px;
        }
        
        .categorization-text {
            font-size: 0.95em;
            margin-bottom: 8px;
            color: #2c3e50;
        }
        
        .categorization-input {
            border-bottom: 1.5px solid #2c3e50;
            display: inline-block;
            min-width: 100px;
            margin-top: 8px;
            height: 18px;
        }
        
        .category-list {
            margin-top: 10px;
            padding: 8px 12px;
            background: #ecf0f1;
            border-radius: 3px;
            font-size: 0.85em;
            color: #7f8c8d;
            break-inside: avoid;
        }
        
        .answers-section {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 3px dashed #95a5a6;
            break-before: page;
        }
        
        .answers-header {
            background: #e74c3c;
            color: white;
            padding: 12px;
            border-radius: 4px;
            font-weight: bold;
            margin-bottom: 20px;
            font-size: 1.1em;
        }
        
        .answer-item {
            margin-bottom: 15px;
            padding: 12px;
            background: #f8f9fa;
            border-left: 4px solid #27ae60;
            border-radius: 3px;
            break-inside: avoid;
        }
        
        .answer-number {
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 4px;
            font-size: 0.9em;
        }
        
        .answer-text {
            color: #2c3e50;
            font-size: 0.9em;
            word-break: break-word;
        }
        
        .footer {
            text-align: center;
            color: #95a5a6;
            font-size: 0.8em;
            margin-top: 40px;
            padding-top: 15px;
            border-top: 1px solid #ecf0f1;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .container {
                max-width: 100%;
                margin: 0;
            }
            .exercise {
                break-inside: avoid;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 WifeyMOOC Worksheet</h1>
            <p>Exercise Set • Generated on {date}</p>
        </div>
"""
        
        # Add exercises
        for idx, exercise in enumerate(self.exercises, 1):
            html_content += self._exercise_to_html(exercise, idx)
        
        # Add answers section
        html_content += self._generate_answers_section()
        
        # Close HTML
        html_content += """
        <div class="footer">
            <p>© WifeyMOOC - Keep Learning! 💫</p>
        </div>
    </div>
</body>
</html>"""
        
        html_content = html_content.replace("{date}", datetime.now().strftime("%B %d, %Y"))
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ HTML worksheet saved to: {output_file}")
        return output_file
    
    def _exercise_to_html(self, exercise: Dict[str, Any], number: int) -> str:
        """Convert individual exercise to HTML"""
        ex_type = exercise.get('type', 'unknown')
        html = f'''
        <div class="exercise">
            <div>
                <span class="exercise-number">Q{number}</span>
                <span class="exercise-type">{ex_type.upper()}</span>
            </div>
            <div class="question">{exercise.get('question', 'N/A')}</div>
'''
        
        # Handle media if present
        if exercise.get('media'):
            media = exercise['media']
            if isinstance(media, dict):
                if 'video' in media:
                    html += f'<div class="media-note">🎥 Video: {media["video"]}</div>\n'
                if 'audio' in media:
                    html += f'<div class="media-note">🔊 Audio: {media["audio"]}</div>\n'
                if 'image' in media and ex_type != 'match_sentence' and ex_type != 'image_tagging':
                    # Embed image inline for non-match_sentence types
                    html += self._render_inline_image(media['image'])
        
        # Type-specific rendering
        if ex_type == 'mcq_single':
            html += self._render_mcq_single(exercise)
        elif ex_type == 'mcq_multiple':
            html += self._render_mcq_multiple(exercise)
        elif ex_type == 'list_pick':
            html += self._render_list_pick(exercise)
        elif ex_type == 'fill_blanks_dropdown':
            html += self._render_fill_blanks(exercise)
        elif ex_type == 'match_phrases':
            html += self._render_match_phrases(exercise)
        elif ex_type == 'match_sentence':
            html += self._render_match_sentence(exercise)
        elif ex_type == 'order_phrase':
            html += self._render_order_phrase(exercise)
        elif ex_type == 'categorization_multiple':
            html += self._render_categorization(exercise)
        elif ex_type == 'word_fill':
            html += self._render_word_fill(exercise)
        elif ex_type == 'sequence_audio':
            html += self._render_sequence(exercise)
        elif ex_type == 'image_tagging':
            html += self._render_image_tagging(exercise)
        elif ex_type == 'multi_questions':
            html += self._render_multi_questions(exercise)
        else:
            html += '<div class="media-note">⚠️ Exercise type not yet formatted for printing</div>\n'
        
        html += '</div>\n'
        return html
    
    def _render_inline_image(self, image_path: str) -> str:
        """Render an image inline with base64 encoding"""
        data_uri = self._load_image_as_base64(image_path)
        if data_uri:
            filename = Path(image_path).name
            return f'''<div class="media-image">
    <img src="{data_uri}" alt="{filename}">
    <div class="media-image-caption">{filename}</div>
</div>\n'''
        else:
            return f'<div class="media-note">🖼️ Image: {image_path}</div>\n'
    
    def _render_mcq_single(self, exercise: Dict) -> str:
        """Render MCQ single choice"""
        html = '<div class="option-list">\n'
        for idx, option in enumerate(exercise.get('options', [])):
            html += f'<div class="option"><input type="radio" id="q_opt_{idx}" name="question"> <label for="q_opt_{idx}">{option}</label></div>\n'
        html += '</div>\n'
        return html
    
    def _render_mcq_multiple(self, exercise: Dict) -> str:
        """Render MCQ multiple choice"""
        html = '<div class="option-list">\n'
        for idx, option in enumerate(exercise.get('options', [])):
            html += f'<div class="option"><input type="checkbox" id="q_opt_{idx}" name="question"> <label for="q_opt_{idx}">{option}</label></div>\n'
        html += '</div>\n'
        return html
    
    def _render_list_pick(self, exercise: Dict) -> str:
        """Render list pick"""
        html = '<div class="option-list">\n'
        for idx, option in enumerate(exercise.get('options', [])):
            html += f'<div class="option"><input type="checkbox" id="q_opt_{idx}" name="question"> <label for="q_opt_{idx}">{option}</label></div>\n'
        html += '</div>\n'
        return html
    
    def _render_fill_blanks(self, exercise: Dict) -> str:
        """Render fill blanks dropdown"""
        html = '<div class="sentence-parts">\n'
        parts = exercise.get('sentence_parts', [])
        for part in parts:
            html += f'{part}'
        html += '<br>'
        for idx in range(len(exercise.get('options_for_blanks', []))):
            html += f'<div><strong>Blank {idx+1}:</strong> <span class="answer-space"></span></div>\n'
        html += '</div>\n'
        return html
    
    def _render_match_phrases(self, exercise: Dict) -> str:
        """Render match phrases"""
        html = '<div class="pairs-list">\n'
        html += '<p style="margin-bottom: 10px; color: #7f8c8d; font-style: italic; font-size: 0.9em;">Match the phrases by drawing lines or writing corresponding letters:</p>\n'
        pairs = exercise.get('pairs', [])
        for pair in pairs:
            source = pair.get('source', '')
            html += f'<div class="pair"><div class="pair-source">{source}</div><div class="pair-target">_____</div></div>\n'
        html += '</div>\n'
        return html
    
    def _render_match_sentence(self, exercise: Dict) -> str:
        """Render match sentence with randomized images"""
        pairs = exercise.get('pairs', [])
        
        # Create list of images with original indices for answer key
        images_with_indices = [(idx, pair.get('image_path', '')) for idx, pair in enumerate(pairs)]
        
        # Shuffle images
        random_order = list(range(len(pairs)))
        random.shuffle(random_order)
        shuffled_images = [images_with_indices[i] for i in random_order]
        
        # Create mapping from original index to random label
        index_to_label = {orig_idx: chr(65 + label_idx) for label_idx, (orig_idx, _) in enumerate(shuffled_images)}
        
        html = '<div class="pairs-list">\n'
        html += '<p style="margin-bottom: 10px; color: #2c3e50; font-weight: bold; font-size: 0.95em;">Images:</p>\n'
        
        # Display images in random order with letter labels
        html += '<div class="image-grid">\n'
        for label_idx, (orig_idx, image_path) in enumerate(shuffled_images):
            data_uri = self._load_image_as_base64(image_path)
            if data_uri:
                label = chr(65 + label_idx)  # A, B, C, D, etc.
                html += f'''<div class="image-item">
    <img src="{data_uri}" alt="option {label}">
    <div class="image-label">({label})</div>
</div>\n'''
        html += '</div>\n'
        
        # Display sentences below
        html += '<p style="margin: 15px 0 8px 0; color: #2c3e50; font-weight: bold; font-size: 0.95em;">Match sentences with images:</p>\n'
        for idx, pair in enumerate(pairs, 1):
            sentence = pair.get('sentence', '')
            html += f'<div class="pair"><div class="pair-source" style="flex: 1;">{idx}. {sentence}</div><div class="pair-target" style="flex: 0; margin-left: 10px;">____</div></div>\n'
        
        html += '</div>\n'
        return html
    
    def _render_order_phrase(self, exercise: Dict) -> str:
        """Render order phrase"""
        html = '<div class="sentence-parts">\n'
        html += '<p style="margin-bottom: 10px; color: #7f8c8d; font-style: italic; font-size: 0.9em;">Number the sentences in correct order:</p>\n'
        for idx, phrase in enumerate(exercise.get('phrase_shuffled', []), 1):
            html += f'<div style="margin: 8px 0;"><span style="border: 1px solid #2c3e50; width: 25px; display: inline-block; text-align: center; font-size: 0.9em;">__</span> {phrase}</div>\n'
        html += '</div>\n'
        return html
    
    def _render_categorization(self, exercise: Dict) -> str:
        """Render categorization - compact layout to avoid page breaks"""
        html = '<div class="pairs-list">\n'
        html += '<p style="margin-bottom: 10px; color: #2c3e50; font-weight: bold; font-size: 0.95em;">Categorize each item:</p>\n'
        stimuli = exercise.get('stimuli', [])
        categories = exercise.get('categories', [])
        
        # Show categories first
        html += '<div class="category-list"><strong>Categories:</strong> ' + ', '.join([c for c in categories if c.strip()]) + '</div>\n'
        
        # Render items in compact format
        for stimulus in stimuli:
            text = stimulus.get('text', '')
            image = stimulus.get('image', '')
            
            html += '<div class="categorization-item">\n'
            
            if text:
                html += f'<div class="categorization-text">{text}</div>\n'
            
            if image:
                data_uri = self._load_image_as_base64(image)
                if data_uri:
                    html += f'<img src="{data_uri}" alt="stimulus">\n'
            
            html += '<div>Category: <span class="categorization-input"></span></div>\n'
            html += '</div>\n'
        
        html += '</div>\n'
        return html
    
    def _render_word_fill(self, exercise: Dict) -> str:
        """Render word fill"""
        html = '<div class="sentence-parts">\n'
        parts = exercise.get('sentence_parts', [])
        for part in parts:
            html += f'{part}'
        html += '<br>'
        for idx in range(len(exercise.get('answers', []))):
            html += f'<div><strong>Answer {idx+1}:</strong> <span class="answer-space"></span></div>\n'
        html += '</div>\n'
        return html
    
    def _render_sequence(self, exercise: Dict) -> str:
        """Render sequence/ordering"""
        html = '<div class="sentence-parts">\n'
        html += '<p style="margin-bottom: 10px; color: #7f8c8d; font-style: italic; font-size: 0.9em;">Put items in correct order:</p>\n'
        options = exercise.get('audio_options', [])
        for idx, option in enumerate(options, 1):
            opt_text = option.get('option', f'Item {idx}') if isinstance(option, dict) else option
            html += f'<div style="margin: 8px 0;"><span style="border: 1px solid #2c3e50; width: 25px; display: inline-block; text-align: center; font-size: 0.9em;">__</span> {opt_text}</div>\n'
        html += '</div>\n'
        return html
    
    def _render_image_tagging(self, exercise: Dict) -> str:
        """Render image tagging with inline image"""
        html = ''
        media = exercise.get('media', {})
        image_path = media.get('image', '')
        
        if image_path:
            html += self._render_inline_image(image_path)
        
        html += f'<div class="sentence-parts">\n'
        html += f'<p style="margin-bottom: 10px; color: #2c3e50; font-weight: 500;"><strong>Button Label:</strong> {exercise.get("button_label", "N/A")}</p>\n'
        html += '<p style="margin-bottom: 10px; color: #7f8c8d; font-style: italic; font-size: 0.9em;">Label the diagram with the following terms:</p>\n'
        tags = exercise.get('tags', [])
        for idx, tag in enumerate(tags, 1):
            html += f'<div style="margin: 6px 0; font-size: 0.9em;">• {tag.get("label", "N/A")}</div>\n'
        html += '</div>\n'
        return html
    
    def _render_multi_questions(self, exercise: Dict) -> str:
        """Render multi questions"""
        html = '<div style="border: 2px dashed #3498db; padding: 10px; border-radius: 4px; margin: 10px 0;">\n'
        html += '<p style="margin-bottom: 10px; font-style: italic; color: #7f8c8d; font-size: 0.85em;">Multiple questions in one exercise:</p>\n'
        for q_idx, question in enumerate(exercise.get('questions', []), 1):
            html += f'<div style="margin: 10px 0; padding: 8px; background: white; border-radius: 3px; font-size: 0.9em;"><strong>Question {q_idx}:</strong> {question.get("question", "N/A")}</div>\n'
        html += '</div>\n'
        return html
    
    def _generate_answers_section(self) -> str:
        """Generate answers section"""
        html = '<div class="answers-section">\n'
        html += '<div class="answers-header">📋 ANSWER KEY</div>\n'
        
        for idx, exercise in enumerate(self.exercises, 1):
            answer = exercise.get('answer')
            if answer is None:
                continue
            
            html += f'<div class="answer-item">\n'
            html += f'<div class="answer-number">Question {idx}</div>\n'
            
            if isinstance(answer, list):
                answer_text = ', '.join(str(a) for a in answer) if answer else 'N/A'
            elif isinstance(answer, dict):
                answer_text = ' | '.join([f'{k}: {v}' for k, v in answer.items()])
            else:
                answer_text = str(answer)
            
            html += f'<div class="answer-text">{answer_text}</div>\n'
            html += '</div>\n'
        
        html += '</div>\n'
        return html


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python json_to_paper.py <json_file> [output_file.html]")
        print("\nExample:")
        print("  python json_to_paper.py testfile-complete.json")
        print("  python json_to_paper.py testfile-complete.json my_worksheet.html")
        print("\nThen open in browser and print to PDF (Ctrl+P or Cmd+P)")
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    converter = ExerciseToPaper(json_file)
    output = converter.generate_html(output_file)
    
    print(f"\n✨ Worksheet ready!")
    print(f"📄 Open '{output}' in your browser")
    print(f"🖨️  Print to PDF: Ctrl+P (or Cmd+P on Mac) → Save as PDF")


if __name__ == "__main__":
    main()
