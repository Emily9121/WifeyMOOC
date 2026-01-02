#!/usr/bin/env python3
"""
WifeyMOOC JSON to Paper Exercise Printer
Converts exercise JSON files into printable formats (HTML/PDF)
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

class ExerciseToPaper:
    def __init__(self, json_file: str):
        self.json_file = json_file
        self.exercises = []
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
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
        }
        
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .header p {
            color: #7f8c8d;
            font-size: 0.95em;
        }
        
        .exercise {
            margin-bottom: 40px;
            page-break-inside: avoid;
            border-left: 5px solid #3498db;
            padding-left: 20px;
        }
        
        .exercise-number {
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 10px;
            font-size: 0.9em;
        }
        
        .exercise-type {
            display: inline-block;
            background: #ecf0f1;
            color: #2c3e50;
            padding: 4px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            margin-left: 10px;
            font-weight: 600;
        }
        
        .question {
            font-size: 1.1em;
            margin: 15px 0;
            font-weight: 500;
            color: #2c3e50;
        }
        
        .media-note {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 10px 15px;
            margin: 15px 0;
            font-size: 0.95em;
            color: #856404;
        }
        
        .option-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .option {
            margin: 10px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 3px solid #dee2e6;
        }
        
        .option input[type="checkbox"],
        .option input[type="radio"] {
            margin-right: 10px;
            cursor: pointer;
            accent-color: #3498db;
        }
        
        .option label {
            cursor: pointer;
            user-select: none;
        }
        
        .blank-line {
            border-bottom: 1.5px solid #2c3e50;
            display: inline-block;
            min-width: 200px;
            margin: 0 5px;
        }
        
        .sentence-parts {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin: 15px 0;
            line-height: 1.8;
        }
        
        .answer-space {
            border-bottom: 1.5px solid #2c3e50;
            display: inline-block;
            min-width: 150px;
            margin: 0 5px;
            height: 20px;
        }
        
        .pairs-list {
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }
        
        .pair {
            margin: 12px 0;
            padding: 10px;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .pair-source {
            font-weight: 500;
            color: #2c3e50;
            flex: 1;
        }
        
        .pair-target {
            color: #7f8c8d;
            flex: 0 1 40%;
            text-align: right;
        }
        
        .draggable-hint {
            font-size: 0.85em;
            color: #7f8c8d;
            font-style: italic;
            margin-top: 10px;
        }
        
        .answers-section {
            margin-top: 60px;
            padding-top: 30px;
            border-top: 3px dashed #95a5a6;
        }
        
        .answers-header {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 4px;
            font-weight: bold;
            margin-bottom: 20px;
            font-size: 1.1em;
        }
        
        .answer-item {
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #27ae60;
            border-radius: 4px;
        }
        
        .answer-number {
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 5px;
        }
        
        .answer-text {
            color: #2c3e50;
            font-size: 0.95em;
        }
        
        .footer {
            text-align: center;
            color: #95a5a6;
            font-size: 0.85em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ecf0f1;
        }
        
        @media print {
            body {
                background: white;
                padding: 0;
            }
            .container {
                box-shadow: none;
                max-width: 100%;
                padding: 20px;
            }
            .exercise {
                page-break-inside: avoid;
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
                if 'image' in media:
                    html += f'<div class="media-note">🖼️ Image: {media["image"]}</div>\n'
        
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
        html += '<br><br>'
        for idx in range(len(exercise.get('options_for_blanks', []))):
            html += f'<div><strong>Blank {idx+1}:</strong> <span class="answer-space"></span></div>\n'
        html += '</div>\n'
        return html
    
    def _render_match_phrases(self, exercise: Dict) -> str:
        """Render match phrases"""
        html = '<div class="pairs-list">\n'
        html += '<p style="margin-bottom: 15px; color: #7f8c8d; font-style: italic;">Match the phrases by drawing lines or writing corresponding letters:</p>\n'
        pairs = exercise.get('pairs', [])
        for pair in pairs:
            source = pair.get('source', '')
            html += f'<div class="pair"><div class="pair-source">{source}</div><div class="pair-target">_____</div></div>\n'
        html += '</div>\n'
        return html
    
    def _render_match_sentence(self, exercise: Dict) -> str:
        """Render match sentence"""
        html = '<div class="pairs-list">\n'
        html += '<p style="margin-bottom: 15px; color: #7f8c8d; font-style: italic;">Match sentences with images:</p>\n'
        pairs = exercise.get('pairs', [])
        for idx, pair in enumerate(pairs, 1):
            sentence = pair.get('sentence', '')
            image = pair.get('image_path', '')
            html += f'<div class="pair"><div class="pair-source">{idx}. {sentence}</div><div class="pair-target">[{image.split("/")[-1]}]</div></div>\n'
        html += '</div>\n'
        return html
    
    def _render_order_phrase(self, exercise: Dict) -> str:
        """Render order phrase"""
        html = '<div class="sentence-parts">\n'
        html += '<p style="margin-bottom: 15px; color: #7f8c8d; font-style: italic;">Number the sentences in correct order (1-5):</p>\n'
        for idx, phrase in enumerate(exercise.get('phrase_shuffled', []), 1):
            html += f'<div style="margin: 10px 0;"><span style="border: 1px solid #2c3e50; width: 30px; display: inline-block; text-align: center;">__</span> {phrase}</div>\n'
        html += '</div>\n'
        return html
    
    def _render_categorization(self, exercise: Dict) -> str:
        """Render categorization"""
        html = '<div class="pairs-list">\n'
        html += '<p style="margin-bottom: 15px; color: #7f8c8d; font-style: italic;">Categorize each item:</p>\n'
        stimuli = exercise.get('stimuli', [])
        categories = exercise.get('categories', [])
        for stimulus in stimuli:
            text = stimulus.get('text', '')
            image = stimulus.get('image', '')
            label = f'{text}' if text else f'[Image]'
            html += f'<div class="pair"><div class="pair-source">{label}</div><div class="pair-target">_____</div></div>\n'
        html += '<p style="margin-top: 15px; font-size: 0.9em; color: #7f8c8d;"><strong>Categories:</strong> ' + ', '.join([c for c in categories if c.strip()]) + '</p>\n'
        html += '</div>\n'
        return html
    
    def _render_word_fill(self, exercise: Dict) -> str:
        """Render word fill"""
        html = '<div class="sentence-parts">\n'
        parts = exercise.get('sentence_parts', [])
        for part in parts:
            html += f'{part}'
        html += '<br><br>'
        for idx in range(len(exercise.get('answers', []))):
            html += f'<div><strong>Answer {idx+1}:</strong> <span class="answer-space"></span></div>\n'
        html += '</div>\n'
        return html
    
    def _render_sequence(self, exercise: Dict) -> str:
        """Render sequence/ordering"""
        html = '<div class="sentence-parts">\n'
        html += '<p style="margin-bottom: 15px; color: #7f8c8d; font-style: italic;">Put items in correct order (1-5):</p>\n'
        options = exercise.get('audio_options', [])
        for idx, option in enumerate(options, 1):
            opt_text = option.get('option', f'Item {idx}') if isinstance(option, dict) else option
            html += f'<div style="margin: 10px 0;"><span style="border: 1px solid #2c3e50; width: 30px; display: inline-block; text-align: center;">__</span> {opt_text}</div>\n'
        html += '</div>\n'
        return html
    
    def _render_image_tagging(self, exercise: Dict) -> str:
        """Render image tagging"""
        html = '<div class="media-note">\n'
        html += f'🖼️ Image: {exercise.get("media", {}).get("image", "N/A")}<br>\n'
        html += f'<strong>Button Label:</strong> {exercise.get("button_label", "N/A")}\n'
        html += '</div>\n'
        html += '<div class="sentence-parts">\n'
        html += '<p style="margin-bottom: 15px; color: #7f8c8d; font-style: italic;">Label the diagram with the following terms:</p>\n'
        tags = exercise.get('tags', [])
        for idx, tag in enumerate(tags, 1):
            html += f'<div style="margin: 8px 0;">• {tag.get("label", "N/A")}</div>\n'
        html += '</div>\n'
        return html
    
    def _render_multi_questions(self, exercise: Dict) -> str:
        """Render multi questions"""
        html = '<div style="border: 2px dashed #3498db; padding: 15px; border-radius: 4px; margin: 10px 0;">\n'
        html += '<p style="margin-bottom: 15px; font-style: italic; color: #7f8c8d;">Multiple questions in one exercise:</p>\n'
        for q_idx, question in enumerate(exercise.get('questions', []), 1):
            html += f'<div style="margin: 15px 0; padding: 10px; background: white; border-radius: 3px;"><strong>Question {q_idx}:</strong> {question.get("question", "N/A")}</div>\n'
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
        sys.exit(1)
    
    json_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    converter = ExerciseToPaper(json_file)
    output = converter.generate_html(output_file)
    
    print(f"\n✨ Worksheet ready! Open '{output}' in your browser to view and print.")


if __name__ == "__main__":
    main()
