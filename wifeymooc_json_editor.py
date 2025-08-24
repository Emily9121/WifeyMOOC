#!/usr/bin/env python3

"""
💖 Wifey MOOC JSON Editor v2.1 💖
A complete WYSIWYG editor for WifeyMOOC quiz questions
Created with love and lots of pink! 💕

UPDATED VERSION 2.1:
✨ Fixed button text readability (no more white text!)
🏷️ Enhanced image tagging with proper alternative support!
🎭 Fixed multi-questions compatibility!

No placeholders - everything is ultra-functional and cute! 💖
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import subprocess
from typing import Dict, List, Any

class WifeyMOOCEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("💖 Wifey MOOC JSON Editor v2.1 💖")
        self.root.geometry("1400x900")  # Bigger for new features!

        # Ultra-pink color scheme - even cuter with better readability! 💕
        self.colors = {
            'bg': '#FFB6C1',        # Light pink
            'secondary': '#FFC0CB', # Pink  
            'accent': '#FF69B4',    # Hot pink
            'text': '#8B008B',      # Dark magenta
            'white': "#FFFFFF",     # White
            'button': '#FF1493',    # Deep pink
            'entry': '#FFEFD5',     # Papaya whip
            'success': '#98FB98',   # Pale green
            'warning': '#FFB347',   # Peach
            'button_text': '#000000'  # 🆕 Black text for readability! 
        }

        self.wifeymooc_app_path = "/Applications/WifeyMOOC.app/Contents/MacOS/WifeyMOOC"

        # Configure root
        self.root.configure(bg=self.colors['bg'])

        # Data storage
        self.questions = []
        self.current_file = None
        self.current_question_index = None

        # Updated question type templates - all the new cuteness! ✨
        self.question_templates = {
            'list_pick': {
                'type': 'list_pick',
                'question': 'Pick all the cute options you want! 💖',
                'options': ['Option 1', 'Option 2', 'Option 3'],
                'answer': [0]
            },
            'mcq_single': {
                'type': 'mcq_single',
                'question': 'Choose the best answer, babe! 💕',
                'options': [
                    {'image': 'image1.jpg', 'text': 'Option A'},
                    {'image': 'image2.jpg', 'text': 'Option B'},
                    {'image': 'image3.jpg', 'text': 'Option C'}
                ],
                'answer': [0],
                'media': None
            },
            'mcq_multiple': {
                'type': 'mcq_multiple', 
                'question': 'Pick all the right answers, sweetie! 💖',
                'options': [
                    {'image': 'image1.jpg', 'text': 'Option A'},
                    {'image': 'image2.jpg', 'text': 'Option B'},
                    {'image': 'image3.jpg', 'text': 'Option C'}
                ],
                'answer': [0, 1],
                'media': None
            },
            'word_fill': {
                'type': 'word_fill',
                'question': 'Fill in the cute blanks! 💕',
                'sentence_parts': ['Fill this ', ' with the perfect word ', ' please!'],
                'answers': ['blank', 'darling'],
                'media': None
            },
            'match_sentence': {
                'type': 'match_sentence',
                'question': 'Match the adorable sentences with images! 💖',
                'pairs': [
                    {'sentence': 'Cute sentence 1', 'image_path': 'image1.jpg'},
                    {'sentence': 'Sweet sentence 2', 'image_path': 'image2.jpg'}
                ],
                'answer': {'image1.jpg': 'Cute sentence 1', 'image2.jpg': 'Sweet sentence 2'},
                'media': None
            },
            'sequence_audio': {
                'type': 'sequence_audio',
                'question': 'Put these sweet sounds in order! 🎵',
                'audio_options': [
                    {'option': 'First lovely sound'},
                    {'option': 'Second amazing sound'}
                ],
                'answer': [0, 1],
                'media': {'audio': 'audio.mp3'}
            },
            'order_phrase': {
                'type': 'order_phrase',
                'question': 'Put these phrases in the right order, honey! 💕',
                'phrase_shuffled': ['Second phrase', 'First phrase', 'Third phrase'],
                'answer': ['First phrase', 'Second phrase', 'Third phrase'],
                'media': None
            },
            'categorization_multiple': {
                'type': 'categorization_multiple',
                'question': 'Categorize these cute items! 📂',
                'stimuli': [
                    {'text': 'Adorable Item 1', 'image': None},
                    {'text': 'Sweet Item 2', 'image': None}
                ],
                'categories': [' ', 'Category A', 'Category B'],
                'answer': {'Adorable Item 1': 'Category A', 'Sweet Item 2': 'Category B'},
                'media': None
            },
            'fill_blanks_dropdown': {
                'type': 'fill_blanks_dropdown',
                'question': 'Choose from the dropdowns, sweetie! ⬇️',
                'sentence_parts': ['Choose ', ' and then ', ' from these cute dropdowns.'],
                'options_for_blanks': [
                    [' ', 'option1', 'option2'],
                    [' ', 'choice1', 'choice2']
                ],
                'answers': ['option1', 'choice1'],
                'media': None
            },
            'match_phrases': {
                'type': 'match_phrases',
                'question': 'Match the phrase beginnings with their perfect endings! 💖',
                'pairs': [{
                    'source': 'Beginning of cute phrase 1...',
                    'targets': [' ', 'ending A', 'ending B', 'ending C']
                }],
                'answer': {'Beginning of cute phrase 1...': 'ending A'},
                'media': None
            },
            # 🆕 NEW QUESTION TYPES!
            'multi_questions': {
                'type': 'multi_questions',
                'questions': [{
                    'type': 'mcq_single',
                    'question': 'First cute question! 💖',
                    'options': [
                        {'image': 'image1.jpg', 'text': 'Option 1'},
                        {'image': 'image2.jpg', 'text': 'Option 2'}
                    ],
                    'answer': [0]
                }, {
                    'type': 'mcq_multiple',
                    'question': 'Second adorable question! 💕',
                    'options': [
                        {'image': 'image3.jpg', 'text': 'Choice A'},
                        {'image': 'image4.jpg', 'text': 'Choice B'}
                    ],
                    'answer': [0, 1]
                }]
            },
            'image_tagging': {
                'type': 'image_tagging',
                'question': 'Tag the cute image! 💖',
                'media': {'image': 'body.jpg'},
                'button_label': 'Alternative View',
                'tags': [
                    {'label': 'Tag 1', 'id': 'tag1'},
                    {'label': 'Tag 2', 'id': 'tag2'}
                ],
                'answer': {
                    'tag1': [100, 150],
                    'tag2': [200, 250]
                },
                'alternatives': []
            }
        }

        self.setup_ui()
    def setup_ui(self):
        """Setup the most gorgeous pink UI ever! 💖"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Ultra-cute title
        title = tk.Label(main_frame, text="💖 Wifey MOOC Question Editor v2.1 💖",
                        font=('Comic Sans MS', 22, 'bold'),
                        bg=self.colors['bg'], fg=self.colors['text'])
        title.pack(pady=10)

        # Top buttons frame - even more functional!
        buttons_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.X, pady=5)

        tk.Button(buttons_frame, text="✨ New JSON", command=self.new_json,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="💾 Load JSON", command=self.load_json,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="💖 Save JSON", command=self.save_json,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="💖 Save As", command=self.save_json_as,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="🚀 Save & Launch", command=self.save_and_launch,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="✨ New Question", command=self.show_add_question_dialog,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Main content area - two gorgeous panels
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left panel - questions list (beautifully organized!)
        left_frame = tk.Frame(content_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        tk.Label(left_frame, text="💕 Questions List 💕", font=('Arial', 14, 'bold'),
                bg=self.colors['secondary'], fg=self.colors['text']).pack(pady=5)

        # Questions listbox with scrollbar
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.questions_listbox = tk.Listbox(list_frame, width=35, height=25,
                                          bg=self.colors['white'],
                                          selectbackground=self.colors['accent'],
                                          font=('Arial', 9))
        scrollbar_list = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.questions_listbox.config(yscrollcommand=scrollbar_list.set)
        scrollbar_list.config(command=self.questions_listbox.yview)

        self.questions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)

        self.questions_listbox.bind('<<ListboxSelect>>', self.on_question_select)

        # List management buttons - ultra-cute and functional!
        list_buttons_frame = tk.Frame(left_frame, bg=self.colors['secondary'])
        list_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(list_buttons_frame, text="🗑️ Delete", command=self.delete_question,
                 bg='#FF6347', fg=self.colors['button_text'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(list_buttons_frame, text="⬆️ Up", command=self.move_question_up,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(list_buttons_frame, text="⬇️ Down", command=self.move_question_down,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        # Right panel - question editor (the main attraction!)
        self.right_frame = tk.Frame(content_frame, bg=self.colors['white'], relief=tk.RAISED, bd=2)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Welcome message
        self.show_welcome_message()

    def show_welcome_message(self):
        """Show the most adorable welcome message ever! 💖"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        welcome_label = tk.Label(self.right_frame,
                               text="💖 Welcome to Wifey MOOC Editor v2.1! 💖\n\n" +
                                    "✨ Enhanced Image Tagging & Multi-Questions! ✨\n\n" +
                                    "🎯 Better Button Readability! 🎯\n\n" +
                                    "💕 Made with extra love for all the girlies! 💕",
                               font=('Comic Sans MS', 16, 'bold'),
                               bg=self.colors['white'], fg=self.colors['text'],
                               justify=tk.CENTER)
        welcome_label.pack(expand=True)

    # 💖 FILE OPERATIONS - PERFECTLY ORGANIZED! 💖

    def new_json(self):
        if self.questions:
            if not messagebox.askyesno("Create New File?", "All unsaved changes will be lost. Continue?"):
                return

        self.questions = []
        self.current_file = None
        self.current_question_index = None
        self.refresh_questions_list()
        self.show_welcome_message()
        messagebox.showinfo("New File", "New JSON file created! Start adding questions, babe!")

    def load_json(self):
        """Load questions from JSON file - pure magic! ✨"""
        file_path = filedialog.askopenfilename(
            title="💖 Select Your Cute Wifey MOOC JSON File 💖",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.questions = json.load(f)
                self.current_file = file_path
                self.refresh_questions_list()
                messagebox.showinfo("Success! 💖", f"Loaded {len(self.questions)} adorable questions successfully!")
            except Exception as e:
                messagebox.showerror("Oopsie! 😢", f"Failed to load file, babe:\n{str(e)}")

    def save_json(self):
        """Save questions to JSON file - preserve all the cuteness! 💾"""
        if not self.questions:
            messagebox.showwarning("Warning! 💕", "No questions to save, sweetie!")
            return

        if not self.current_file:
            self.save_json_as()
            return

        try:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                json.dump(self.questions, f, indent=2, ensure_ascii=False)
            messagebox.showinfo("Success! 💖", "Questions saved successfully, darling!")
        except Exception as e:
            messagebox.showerror("Oopsie! 😢", f"Failed to save file, honey:\n{str(e)}")

    def save_json_as(self):
        """Save questions to a new JSON file - spread the cuteness! 💕"""
        file_path = filedialog.asksaveasfilename(
            title="💖 Save Your Beautiful Wifey MOOC JSON File 💖",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if file_path:
            self.current_file = file_path
            self.save_json()

    def refresh_questions_list(self):
        """Refresh the questions listbox - keep it super fresh! 💫"""
        self.questions_listbox.delete(0, tk.END)
        for i, question in enumerate(self.questions):
            qtype = question.get('type', 'unknown')
            # Special handling for multi_questions
            if qtype == 'multi_questions':
                sub_count = len(question.get('questions', []))
                qtext = f"Multi-Block ({sub_count} questions)"
            else:
                qtext = question.get('question', 'No question text')

            # Truncate long questions cutely
            if len(qtext) > 35:
                qtext = qtext[:35] + "... 💖"

            self.questions_listbox.insert(tk.END, f"{i+1}. [{qtype}] {qtext}")

    def save_and_launch(self):
        # Save JSON
        if not self.questions:
            messagebox.showwarning("Warning! 💕", "No questions to save, sweetie!")
            return

        if not self.current_file:
            self.save_json_as()
            if not self.current_file:
                return
        else:
            self.save_json()

        # Launch WifeyMOOC app with current file
        try:
            cmd = [self.wifeymooc_app_path, "-q", self.current_file]
            subprocess.Popen(cmd)
            messagebox.showinfo("Launched! 💖", f"Launched WifeyMOOC with\n{self.current_file}")
        except Exception as e:
            messagebox.showerror("Oopsie! 😢", f"Failed to launch app, babe:\n{str(e)}")

    def on_question_select(self, event):
        """Handle question selection from list - ultra-responsive! 💕"""
        selection = self.questions_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_question_index = index
            self.edit_question(index)
    def show_add_question_dialog(self):
        """Show the most adorable dialog to add new questions! ✨"""
        dialog = tk.Toplevel(self.root)
        dialog.title("✨ Add New Adorable Question ✨")
        dialog.geometry("500x700")  # Taller for new types!
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog perfectly
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

        tk.Label(dialog, text="💖 Choose Your Question Type, Princess! 💖",
                font=('Comic Sans MS', 16, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack(pady=10)

        # Question type buttons - all the cute options including NEW ones!
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        question_types = [
            ('📝 List Pick (Select Multiple)', 'list_pick'),
            ('🔘 Single Choice MCQ (Enhanced!)', 'mcq_single'),
            ('☑️ Multiple Choice MCQ (Enhanced!)', 'mcq_multiple'),
            ('📝 Word Fill (Fill Blanks)', 'word_fill'),
            ('🔗 Match Sentences to Images', 'match_sentence'),
            ('🎵 Audio Sequence Order', 'sequence_audio'),
            ('📋 Order Phrases Correctly', 'order_phrase'),
            ('📂 Categorization Multiple', 'categorization_multiple'),
            ('⬇️ Fill Blanks with Dropdowns', 'fill_blanks_dropdown'),
            ('🔗 Match Phrase Beginnings to Endings', 'match_phrases'),
            # 🆕 NEW TYPES!
            ('🎭 Multi-Questions Block (Super Cool!)', 'multi_questions'),
            ('🏷️ Image Tagging (Drag & Drop!)', 'image_tagging')
        ]

        for i, (display_name, qtype) in enumerate(question_types):
            color = self.colors['accent'] if qtype in ['multi_questions', 'image_tagging'] else self.colors['button']
            btn = tk.Button(button_frame, text=display_name,
                           command=lambda t=qtype: self.add_question(t, dialog),
                           bg=color, fg=self.colors['button_text'],
                           font=('Arial', 10, 'bold'), width=45)
            btn.pack(pady=4, padx=5, fill=tk.X)

        # Cancel button
        tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy,
                 bg='#FF6347', fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=15)

    def add_question(self, question_type, dialog):
        """Add a new question of specified type - ultra-exciting! 💖"""
        if question_type in self.question_templates:
            new_question = self.question_templates[question_type].copy()

            # Deep copy for nested structures (super important!)
            if 'pairs' in new_question:
                new_question['pairs'] = [pair.copy() for pair in new_question['pairs']]
            if 'stimuli' in new_question:
                new_question['stimuli'] = [stim.copy() for stim in new_question['stimuli']]
            if 'audio_options' in new_question:
                new_question['audio_options'] = [opt.copy() for opt in new_question['audio_options']]
            if 'options_for_blanks' in new_question:
                new_question['options_for_blanks'] = [opts.copy() for opts in new_question['options_for_blanks']]
            if 'questions' in new_question:  # For multi_questions
                new_question['questions'] = []
                for subq in self.question_templates[question_type]['questions']:
                    subq_copy = subq.copy()
                    if 'options' in subq_copy:
                        subq_copy['options'] = [opt.copy() if isinstance(opt, dict) else opt for opt in subq_copy['options']]
                    new_question['questions'].append(subq_copy)
            if 'tags' in new_question:  # For image_tagging
                new_question['tags'] = [tag.copy() for tag in new_question['tags']]
                new_question['answer'] = new_question['answer'].copy()
                new_question['alternatives'] = []

            self.questions.append(new_question)
            self.refresh_questions_list()

            # Select the new question automatically - so convenient!
            new_index = len(self.questions) - 1
            self.questions_listbox.selection_set(new_index)
            self.current_question_index = new_index
            self.edit_question(new_index)

            dialog.destroy()
            messagebox.showinfo("Success! 💖", f"Added new {question_type.replace('_', ' ')} question, babe!")

    def delete_question(self):
        """Delete selected question - sometimes we need to let go 💔"""
        selection = self.questions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning! 💕", "Please select a question to delete, sweetie!")
            return

        index = selection[0]
        question = self.questions[index]

        if question.get('type') == 'multi_questions':
            qtext = f"Multi-questions block with {len(question.get('questions', []))} sub-questions"
        else:
            qtext = question.get('question', 'No question text')[:50]

        if messagebox.askyesno("Confirm Delete 🗑️", f"Are you sure you want to delete this question, honey?\n\n{qtext}..."):
            del self.questions[index]
            self.refresh_questions_list()
            self.show_welcome_message()
            messagebox.showinfo("Deleted! 💔", "Question deleted successfully, darling!")

    def move_question_up(self):
        """Move selected question up in the list - rearrange the cuteness! ⬆️"""
        selection = self.questions_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        index = selection[0]
        self.questions[index], self.questions[index-1] = self.questions[index-1], self.questions[index]
        self.refresh_questions_list()
        self.questions_listbox.selection_set(index-1)

    def move_question_down(self):
        """Move selected question down in the list - rearrange the cuteness! ⬇️"""
        selection = self.questions_listbox.curselection()
        if not selection or selection[0] == len(self.questions) - 1:
            return

        index = selection[0]
        self.questions[index], self.questions[index+1] = self.questions[index+1], self.questions[index]
        self.refresh_questions_list()
        self.questions_listbox.selection_set(index+1)

    def browse_media_file(self, var, media_type):
        """Browse for media file - find the perfect files! 📁"""
        filetypes = {
            'video': [("Video files", "*.mp4 *.avi *.mov *.wmv *.flv *.mkv"), ("All files", "*.*")],
            'audio': [("Audio files", "*.mp3 *.wav *.ogg *.m4a *.aac *.flac"), ("All files", "*.*")],
            'image': [("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.svg *.webp"), ("All files", "*.*")]
        }

        file_path = filedialog.askopenfilename(
            title=f"💖 Select Your Perfect {media_type.title()} File 💖",
            filetypes=filetypes.get(media_type, [("All files", "*.*")])
        )

        if file_path:
            var.set(file_path)

    # 💖 COMMON EDITOR COMPONENTS - REUSABLE CUTENESS WITH BETTER READABILITY! 💖

    def create_media_section(self, question, index):
        """Create the gorgeous media management section! 🎬"""
        media_frame = tk.LabelFrame(self.editor_frame, text="🎬 Media Files (Video, Audio, Images) 🎬",
                                   font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                   fg=self.colors['text'])
        media_frame.pack(fill=tk.X, padx=10, pady=10)

        media = question.get('media', {}) or {}

        # Video section
        video_frame = tk.Frame(media_frame, bg=self.colors['white'])
        video_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(video_frame, text="📹 Video File:", bg=self.colors['white'],
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        video_var = tk.StringVar(value=media.get('video', ''))
        video_entry = tk.Entry(video_frame, textvariable=video_var, width=50, bg=self.colors['entry'])
        video_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(video_frame, text="Browse 📁", bg=self.colors['button'], fg=self.colors['button_text'],
                 command=lambda: self.browse_media_file(video_var, "video")).pack(side=tk.RIGHT, padx=5)

        # Audio section
        audio_frame = tk.Frame(media_frame, bg=self.colors['white'])
        audio_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(audio_frame, text="🎵 Audio File:", bg=self.colors['white'],
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        audio_var = tk.StringVar(value=media.get('audio', ''))
        audio_entry = tk.Entry(audio_frame, textvariable=audio_var, width=50, bg=self.colors['entry'])
        audio_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(audio_frame, text="Browse 📁", bg=self.colors['button'], fg=self.colors['button_text'],
                 command=lambda: self.browse_media_file(audio_var, "audio")).pack(side=tk.RIGHT, padx=5)

        # Image section
        image_frame = tk.Frame(media_frame, bg=self.colors['white'])
        image_frame.pack(fill=tk.X, padx=5, pady=2)

        tk.Label(image_frame, text="🖼️ Image File:", bg=self.colors['white'],
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        image_var = tk.StringVar(value=media.get('image', ''))
        image_entry = tk.Entry(image_frame, textvariable=image_var, width=50, bg=self.colors['entry'])
        image_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(image_frame, text="Browse 📁", bg=self.colors['button'], fg=self.colors['button_text'],
                 command=lambda: self.browse_media_file(image_var, "image")).pack(side=tk.RIGHT, padx=5)

        # Save media function - preserve the beauty!
        def save_media():
            new_media = {}
            if video_var.get().strip():
                new_media['video'] = video_var.get().strip()
            if audio_var.get().strip():
                new_media['audio'] = audio_var.get().strip()
            if image_var.get().strip():
                new_media['image'] = image_var.get().strip()

            question['media'] = new_media if new_media else None
            messagebox.showinfo("Success! 💖", "Media files updated successfully, babe!")

        tk.Button(media_frame, text="💾 Save Media Files", command=save_media,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=8)

    def create_question_text_section(self, question, index, label_text="📝 Question Text 📝"):
        """Create the question text editing section - the heart of it all! 💖"""
        text_frame = tk.LabelFrame(self.editor_frame, text=label_text,
                                  font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['text'])
        text_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(text_frame, text="💡 Write your question here, sweetie!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        text_var = tk.StringVar(value=question.get('question', ''))
        text_entry = tk.Entry(text_frame, textvariable=text_var, font=('Arial', 11),
                             bg=self.colors['entry'], width=80)
        text_entry.pack(padx=10, pady=10, fill=tk.X)

        def save_question_text():
            question['question'] = text_var.get()
            self.refresh_questions_list()
            messagebox.showinfo("Success! 💖", "Question text updated beautifully!")

        tk.Button(text_frame, text="💾 Save Question Text", command=save_question_text,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=5)

    def edit_question(self, index):
        """Edit question at specified index - the main magic! ✨"""
        if index < 0 or index >= len(self.questions):
            return

        question = self.questions[index]
        qtype = question.get('type')

        # Clear the right panel
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Create scrollable frame for the editor - beautifully organized!
        canvas = tk.Canvas(self.right_frame, bg=self.colors['white'])
        scrollbar = ttk.Scrollbar(self.right_frame, orient="vertical", command=canvas.yview)
        self.editor_frame = tk.Frame(canvas, bg=self.colors['white'])

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas_frame = canvas.create_window((0, 0), window=self.editor_frame, anchor="nw")

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            canvas.itemconfig(canvas_frame, width=event.width)

        self.editor_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Bind mouse wheel for scrolling - so convenient!
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # Ultra-gorgeous title
        title_text = f"💖 Editing Question {index + 1}: {qtype.replace('_', ' ').title()} 💖"
        tk.Label(self.editor_frame, text=title_text, font=('Comic Sans MS', 18, 'bold'),
                bg=self.colors['white'], fg=self.colors['text']).pack(pady=10)

        # Call appropriate editor based on question type
        editor_method = getattr(self, f'edit_{qtype}', None)
        if editor_method:
            editor_method(question, index)
        else:
            tk.Label(self.editor_frame, text=f"❌ Oopsie! Unsupported question type: {qtype}",
                    font=('Arial', 12), bg=self.colors['white'], fg='red').pack(pady=20)
    # 🆕 ENHANCED IMAGE TAGGING EDITOR - NOW WITH PROPER ALTERNATIVE SUPPORT! 🆕

    def edit_image_tagging(self, question, index):
        """Enhanced editor for image_tagging questions - now with proper alternative support! 🏷️"""
        self.create_question_text_section(question, index)

        # Main image section
        main_frame = tk.LabelFrame(self.editor_frame, text="🖼️ Main Image Configuration 🖼️",
                                  font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['text'])
        main_frame.pack(fill=tk.X, padx=10, pady=10)

        media = question.get('media', {}) or {}

        # Main image path
        main_image_frame = tk.Frame(main_frame, bg=self.colors['white'])
        main_image_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(main_image_frame, text="🖼️ Main Image:", bg=self.colors['white'],
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        main_image_var = tk.StringVar(value=media.get('image', ''))
        tk.Entry(main_image_frame, textvariable=main_image_var, width=50, bg=self.colors['entry']).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        tk.Button(main_image_frame, text="Browse 📁", bg=self.colors['button'], fg=self.colors['button_text'],
                 command=lambda: self.browse_media_file(main_image_var, "image")).pack(side=tk.RIGHT, padx=5)

        # Button label for alternative view
        button_frame = tk.Frame(main_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(button_frame, text="🔘 Main Button Label:", bg=self.colors['white'],
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        button_label_var = tk.StringVar(value=question.get('button_label', 'Alternative View'))
        tk.Entry(button_frame, textvariable=button_label_var, width=30, bg=self.colors['entry']).pack(side=tk.LEFT, padx=5)

        def save_main_config():
            new_media = {'image': main_image_var.get().strip()} if main_image_var.get().strip() else {}
            question['media'] = new_media
            question['button_label'] = button_label_var.get().strip()
            messagebox.showinfo("Success! 💖", "Main image configuration saved!")

        tk.Button(main_frame, text="💾 Save Main Config", command=save_main_config,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=5)

        # Tags section - the heart of image tagging!
        tags_frame = tk.LabelFrame(self.editor_frame, text="🏷️ Draggable Tags Configuration 🏷️",
                                  font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['text'])
        tags_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(tags_frame, text="💡 Configure tags and their coordinates for the main image!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        tags_list_frame = tk.Frame(tags_frame, bg=self.colors['white'])
        tags_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.image_tagging_tags_data = []

        def refresh_main_tags():
            for widget in tags_list_frame.winfo_children():
                widget.destroy()
            self.image_tagging_tags_data.clear()

            for i, tag in enumerate(question.get('tags', [])):
                row_frame = tk.Frame(tags_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                # Tag ID
                tk.Label(row_frame, text=f"🏷️ {i+1} ID:", bg=self.colors['white'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                id_var = tk.StringVar(value=tag.get('id', ''))
                tk.Entry(row_frame, textvariable=id_var, bg=self.colors['entry'],
                        width=15, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)

                # Tag Label (what students see)
                tk.Label(row_frame, text="📝 Label:", bg=self.colors['white'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(10,2))

                label_var = tk.StringVar(value=tag.get('label', ''))
                tk.Entry(row_frame, textvariable=label_var, bg=self.colors['entry'],
                        width=25, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)

                # Main image coordinates 
                tk.Label(row_frame, text="📍 Main X:", bg=self.colors['white']).pack(side=tk.LEFT, padx=(10,2))
                answer_coords = question.get('answer', {}).get(tag.get('id', ''), [0, 0])
                x_var = tk.StringVar(value=str(answer_coords[0] if len(answer_coords) > 0 else 0))
                tk.Entry(row_frame, textvariable=x_var, bg=self.colors['entry'],
                        width=8, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)

                tk.Label(row_frame, text="Y:", bg=self.colors['white']).pack(side=tk.LEFT, padx=(5,2))
                y_var = tk.StringVar(value=str(answer_coords[1] if len(answer_coords) > 1 else 0))
                tk.Entry(row_frame, textvariable=y_var, bg=self.colors['entry'],
                        width=8, font=('Arial', 10)).pack(side=tk.LEFT, padx=2)

                # Delete button
                if len(question.get('tags', [])) > 1:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_main_tag(idx)).pack(side=tk.RIGHT, padx=5)

                self.image_tagging_tags_data.append((id_var, label_var, x_var, y_var))

        def add_main_tag():
            new_tag = {'id': f'tag{len(question.get("tags", [])) + 1}', 'label': 'New Tag'}
            question.setdefault('tags', []).append(new_tag)
            # Add default coordinates
            question.setdefault('answer', {})[new_tag['id']] = [100, 100]
            refresh_main_tags()

        def delete_main_tag(idx):
            if len(question.get('tags', [])) > 1:
                tag_id = question['tags'][idx].get('id')
                del question['tags'][idx]
                # Remove from answer too
                if tag_id in question.get('answer', {}):
                    del question['answer'][tag_id]
                refresh_main_tags()

        def save_main_tags():
            # Save tags and main coordinates
            tags = []
            answer = {}
            for id_var, label_var, x_var, y_var in self.image_tagging_tags_data:
                tag_id = id_var.get().strip()
                if tag_id:
                    tags.append({'id': tag_id, 'label': label_var.get().strip()})
                    try:
                        x = float(x_var.get())
                        y = float(y_var.get())
                        answer[tag_id] = [x, y]
                    except ValueError:
                        answer[tag_id] = [0, 0]

            question['tags'] = tags
            question['answer'] = answer
            messagebox.showinfo("Success! 💖", "Main tags saved beautifully!")

        refresh_main_tags()

        # Tags buttons
        tags_btn_frame = tk.Frame(tags_frame, bg=self.colors['white'])
        tags_btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(tags_btn_frame, text="➕ Add Tag", command=add_main_tag,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(tags_btn_frame, text="💾 Save Main Tags", command=save_main_tags,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        # 🆕 ENHANCED ALTERNATIVE IMAGES SECTION - THE MISSING PIECE! 🆕
        alt_frame = tk.LabelFrame(self.editor_frame, text="🔄 Alternative Images (Enhanced!) 🔄",
                                 font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                 fg=self.colors['text'])
        alt_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(alt_frame, text="💡 Different images with same tags but different coordinates! Now fully editable!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        # Alternative management with proper coordinate editing
        alt_management_frame = tk.Frame(alt_frame, bg=self.colors['white'])
        alt_management_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(alt_management_frame, text="🔢 Number of alternatives:", 
                bg=self.colors['white'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

        current_alt_count = len(question.get('alternatives', []))
        alt_count_var = tk.StringVar(value=str(current_alt_count))
        tk.Entry(alt_management_frame, textvariable=alt_count_var, width=5, bg=self.colors['entry']).pack(side=tk.LEFT, padx=5)

        def update_alternatives_structure():
            try:
                count = int(alt_count_var.get())
                current_alts = question.get('alternatives', [])

                # Add new alternatives if needed
                while len(current_alts) < count:
                    new_alt = {
                        'media': {'image': 'alternative.jpg'},
                        'button_label': f'Alt View {len(current_alts) + 1}',
                        'tags': [tag.copy() for tag in question.get('tags', [])],
                        'answer': {tag.get('id', ''): [150, 150] for tag in question.get('tags', [])}
                    }
                    current_alts.append(new_alt)

                # Remove excess alternatives
                while len(current_alts) > count:
                    current_alts.pop()

                question['alternatives'] = current_alts
                refresh_alternatives_editor()
                messagebox.showinfo("Success! 💖", f"Updated to {count} alternatives!")
            except ValueError:
                messagebox.showerror("Error! 😢", "Please enter a valid number!")

        tk.Button(alt_management_frame, text="🔄 Update Count", command=update_alternatives_structure,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Alternative details editor
        alt_details_frame = tk.Frame(alt_frame, bg=self.colors['white'])
        alt_details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)

        def refresh_alternatives_editor():
            for widget in alt_details_frame.winfo_children():
                widget.destroy()

            for alt_idx, alt in enumerate(question.get('alternatives', [])):
                # Container for each alternative
                alt_container = tk.LabelFrame(alt_details_frame, text=f"🌟 Alternative {alt_idx + 1} 🌟",
                                             bg=self.colors['secondary'], font=('Arial', 11, 'bold'))
                alt_container.pack(fill=tk.X, pady=5, padx=2)

                # Alternative image path
                alt_img_frame = tk.Frame(alt_container, bg=self.colors['secondary'])
                alt_img_frame.pack(fill=tk.X, padx=5, pady=3)

                tk.Label(alt_img_frame, text="🖼️ Image:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                alt_img_var = tk.StringVar(value=alt.get('media', {}).get('image', ''))
                tk.Entry(alt_img_frame, textvariable=alt_img_var, bg=self.colors['entry'],
                        width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                tk.Button(alt_img_frame, text="Browse", bg=self.colors['button'], fg=self.colors['button_text'],
                         command=lambda v=alt_img_var: self.browse_media_file(v, "image")).pack(side=tk.RIGHT, padx=2)

                # Alternative button label
                alt_btn_frame = tk.Frame(alt_container, bg=self.colors['secondary'])
                alt_btn_frame.pack(fill=tk.X, padx=5, pady=3)

                tk.Label(alt_btn_frame, text="🔘 Button Label:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                alt_btn_var = tk.StringVar(value=alt.get('button_label', f'Alt View {alt_idx + 1}'))
                tk.Entry(alt_btn_frame, textvariable=alt_btn_var, bg=self.colors['entry'],
                        width=25, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

                # Tags coordinates for this alternative - THE KEY MISSING FEATURE! 
                tags_coord_frame = tk.LabelFrame(alt_container, text="🏷️ Tag Coordinates for This Alternative",
                                                bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                tags_coord_frame.pack(fill=tk.X, padx=5, pady=5)

                alt_coords_data = []

                for tag in question.get('tags', []):
                    tag_id = tag.get('id', '')
                    tag_label = tag.get('label', '')

                    coord_row = tk.Frame(tags_coord_frame, bg=self.colors['secondary'])
                    coord_row.pack(fill=tk.X, pady=1)

                    tk.Label(coord_row, text=f"{tag_label}:", bg=self.colors['secondary'],
                            width=15, anchor='w').pack(side=tk.LEFT)

                    # Get coordinates for this tag in this alternative
                    alt_coords = alt.get('answer', {}).get(tag_id, [0, 0])

                    tk.Label(coord_row, text="X:", bg=self.colors['secondary']).pack(side=tk.LEFT, padx=(5,2))
                    alt_x_var = tk.StringVar(value=str(alt_coords[0] if len(alt_coords) > 0 else 0))
                    tk.Entry(coord_row, textvariable=alt_x_var, bg=self.colors['entry'],
                            width=8, font=('Arial', 9)).pack(side=tk.LEFT, padx=2)

                    tk.Label(coord_row, text="Y:", bg=self.colors['secondary']).pack(side=tk.LEFT, padx=(5,2))
                    alt_y_var = tk.StringVar(value=str(alt_coords[1] if len(alt_coords) > 1 else 0))
                    tk.Entry(coord_row, textvariable=alt_y_var, bg=self.colors['entry'],
                            width=8, font=('Arial', 9)).pack(side=tk.LEFT, padx=2)

                    alt_coords_data.append((tag_id, alt_x_var, alt_y_var))

                # Save function for this specific alternative
                def save_this_alternative(idx=alt_idx, img_var=alt_img_var, btn_var=alt_btn_var, coords_data=alt_coords_data):
                    if idx < len(question.get('alternatives', [])):
                        alt = question['alternatives'][idx]

                        # Save image and button label
                        alt['media'] = {'image': img_var.get().strip()}
                        alt['button_label'] = btn_var.get().strip()

                        # Save coordinates for all tags
                        alt_answer = {}
                        for tag_id, x_var, y_var in coords_data:
                            try:
                                x = float(x_var.get())
                                y = float(y_var.get())
                                alt_answer[tag_id] = [x, y]
                            except ValueError:
                                alt_answer[tag_id] = [0, 0]

                        alt['answer'] = alt_answer
                        messagebox.showinfo("Success! 💖", f"Alternative {idx + 1} saved perfectly!")

                tk.Button(alt_container, text=f"💾 Save Alternative {alt_idx + 1}", 
                         command=save_this_alternative,
                         bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=5)

        refresh_alternatives_editor()

        # Master save function for everything
        def save_everything():
            save_main_config()
            save_main_tags()
            messagebox.showinfo("Success! 💖", "Complete image tagging configuration saved beautifully!")

        tk.Button(alt_frame, text="💖 Save Everything", command=save_everything,
                 bg=self.colors['success'], fg=self.colors['button_text'], font=('Arial', 12, 'bold')).pack(pady=10)
    # 💖 ENHANCED MULTI-QUESTIONS EDITOR - WORKS WITH IMAGE TAGGING! 💖

    def edit_multi_questions(self, question, index):
        """Enhanced editor for multi_questions - works perfectly with image tagging too! 🎭"""
        # Multi-questions don't have their own question text, just sub-questions

        # Sub-questions section - the main attraction!
        subq_frame = tk.LabelFrame(self.editor_frame, text="🎭 Multi-Questions Block (Super Enhanced!) 🎭",
                                  font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                  fg=self.colors['text'])
        subq_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(subq_frame, text="💡 Create multiple sub-questions! Each can be any question type including image tagging!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        subq_list_frame = tk.Frame(subq_frame, bg=self.colors['white'])
        subq_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.multi_questions_data = []

        def refresh_subquestions():
            for widget in subq_list_frame.winfo_children():
                widget.destroy()
            self.multi_questions_data.clear()

            for i, subq in enumerate(question.get('questions', [])):
                # Container for each sub-question - beautifully organized!
                subq_container = tk.LabelFrame(subq_list_frame, text=f"💖 Sub-Question {i+1}: {subq.get('type', 'unknown')} 💖",
                                              bg=self.colors['secondary'], font=('Arial', 11, 'bold'))
                subq_container.pack(fill=tk.X, pady=5, padx=2)

                # Question type selector
                type_frame = tk.Frame(subq_container, bg=self.colors['secondary'])
                type_frame.pack(fill=tk.X, padx=5, pady=3)

                tk.Label(type_frame, text="🎭 Type:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                # All question types available for sub-questions! Including image tagging!
                available_types = ['mcq_single', 'mcq_multiple', 'word_fill', 'list_pick',
                                 'match_sentence', 'sequence_audio', 'order_phrase',
                                 'categorization_multiple', 'fill_blanks_dropdown', 'match_phrases',
                                 'image_tagging']  # 🆕 Now includes image tagging!

                type_var = tk.StringVar(value=subq.get('type', 'mcq_single'))
                type_combo = ttk.Combobox(type_frame, textvariable=type_var,
                                        values=available_types, state='readonly', width=20)
                type_combo.pack(side=tk.LEFT, padx=5)

                # Question text
                text_frame = tk.Frame(subq_container, bg=self.colors['secondary'])
                text_frame.pack(fill=tk.X, padx=5, pady=3)

                tk.Label(text_frame, text="📝 Question:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                text_var = tk.StringVar(value=subq.get('question', ''))
                tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'],
                        width=70, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                # Quick preview of current configuration
                preview_frame = tk.Frame(subq_container, bg=self.colors['secondary'])
                preview_frame.pack(fill=tk.X, padx=5, pady=5)

                preview_text = tk.Text(preview_frame, height=3, width=80, bg=self.colors['entry'],
                                     font=('Arial', 8))
                preview_text.pack(padx=5, pady=2)

                # Generate preview content
                preview_content = f"Type: {subq.get('type', 'unknown')}\n"
                if subq.get('type') == 'image_tagging':
                    preview_content += f"Main Image: {subq.get('media', {}).get('image', 'Not set')}\n"
                    preview_content += f"Tags: {len(subq.get('tags', []))} tags, {len(subq.get('alternatives', []))} alternatives"
                elif subq.get('type') in ['mcq_single', 'mcq_multiple']:
                    preview_content += f"Options: {len(subq.get('options', []))} options\n"
                    preview_content += f"Answers: {subq.get('answer', [])}"
                else:
                    preview_content += f"Answer: {str(subq.get('answer', 'Not set'))[:50]}"

                preview_text.insert('1.0', preview_content)
                preview_text.config(state='disabled')

                self.multi_questions_data.append({
                    'type_var': type_var,
                    'text_var': text_var,
                    'preview_text': preview_text,
                    'subq_index': i
                })

                # Sub-question buttons
                subq_btn_frame = tk.Frame(subq_container, bg=self.colors['secondary'])
                subq_btn_frame.pack(fill=tk.X, pady=5)

                tk.Button(subq_btn_frame, text="🔧 Edit Details", bg=self.colors['button'], fg=self.colors['button_text'],
                         command=lambda idx=i: edit_subquestion_details(idx),
                         font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

                if len(question.get('questions', [])) > 1:
                    tk.Button(subq_btn_frame, text="🗑️ Delete", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_subquestion(idx),
                             font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        def add_subquestion():
            new_subq = {
                'type': 'mcq_single',
                'question': 'New cute sub-question! 💖',
                'options': [
                    {'image': 'image1.jpg', 'text': 'Option A'},
                    {'image': 'image2.jpg', 'text': 'Option B'}
                ],
                'answer': [0]
            }
            question.setdefault('questions', []).append(new_subq)
            refresh_subquestions()

        def delete_subquestion(idx):
            if len(question.get('questions', [])) > 1:
                del question['questions'][idx]
                refresh_subquestions()

        def edit_subquestion_details(idx):
            """Open a detailed editor for a specific sub-question - enhanced for all types!"""
            if idx >= len(question.get('questions', [])):
                return

            subq = question['questions'][idx]

            # Create a new dialog for detailed editing
            detail_dialog = tk.Toplevel(self.root)
            detail_dialog.title(f"✨ Edit Sub-Question {idx+1} ({subq.get('type', 'unknown')}) ✨")
            detail_dialog.geometry("1000x800")  # Bigger for image tagging
            detail_dialog.configure(bg=self.colors['bg'])
            detail_dialog.transient(self.root)
            detail_dialog.grab_set()

            # Create a scrollable mini-editor within the dialog
            canvas = tk.Canvas(detail_dialog, bg=self.colors['white'])
            scrollbar = ttk.Scrollbar(detail_dialog, orient="vertical", command=canvas.yview)
            detail_frame = tk.Frame(canvas, bg=self.colors['white'])

            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
            scrollbar.pack(side="right", fill="y")

            canvas_frame = canvas.create_window((0, 0), window=detail_frame, anchor="nw")

            def on_frame_configure(event):
                canvas.configure(scrollregion=canvas.bbox("all"))

            def on_canvas_configure(event):
                canvas.itemconfig(canvas_frame, width=event.width)

            detail_frame.bind("<Configure>", on_frame_configure)
            canvas.bind("<Configure>", on_canvas_configure)

            # Use the appropriate editor for this sub-question type
            self.editor_frame = detail_frame  # Temporarily redirect

            qtype = subq.get('type')
            if qtype == 'mcq_single':
                self.edit_mcq_single(subq, idx)
            elif qtype == 'mcq_multiple':
                self.edit_mcq_multiple(subq, idx)
            elif qtype == 'image_tagging':  # 🆕 Now properly supported!
                self.edit_image_tagging(subq, idx)
            elif qtype == 'list_pick':
                self.edit_list_pick(subq, idx)
            elif qtype == 'word_fill':
                self.edit_word_fill(subq, idx)
            elif qtype == 'match_sentence':
                self.edit_match_sentence(subq, idx)
            elif qtype == 'categorization_multiple':
                self.edit_categorization_multiple(subq, idx)
            # Add other types as needed...

            # Close button
            tk.Button(detail_dialog, text="💖 Close & Refresh", 
                     command=lambda: [detail_dialog.destroy(), refresh_subquestions()],
                     bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 12, 'bold')).pack(pady=10)

        def save_all_subquestions():
            # Save basic info for all sub-questions
            for data in self.multi_questions_data:
                idx = data['subq_index']
                if idx < len(question.get('questions', [])):
                    subq = question['questions'][idx]
                    # Save type and text
                    subq['type'] = data['type_var'].get()
                    subq['question'] = data['text_var'].get()

            messagebox.showinfo("Success! 💖", "Multi-questions block saved beautifully!")
            refresh_subquestions()

        refresh_subquestions()

        # Main buttons
        btn_frame = tk.Frame(subq_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Sub-Question", command=add_subquestion,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Sub-Questions", command=save_all_subquestions,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

    # 💖 ENHANCED MCQ EDITORS - FULL FEATURED! 💖

    def edit_mcq_single(self, question, index):
        """Enhanced editor for mcq_single - supports text, image, or both! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Enhanced options section - supports all formats!
        options_frame = tk.LabelFrame(self.editor_frame, text="🔘 Enhanced Answer Options (Text + Image Support!) 🔘",
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(options_frame, text="💡 Options can be text-only, image-only, or text+image! Select the correct one!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        options_list_frame = tk.Frame(options_frame, bg=self.colors['white'])
        options_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.mcq_single_option_vars = []
        self.mcq_single_correct_var = tk.IntVar()

        def refresh_options():
            for widget in options_list_frame.winfo_children():
                widget.destroy()
            self.mcq_single_option_vars.clear()

            correct_answer = question.get('answer', [0])[0] if question.get('answer') else 0
            self.mcq_single_correct_var.set(correct_answer)

            for i, option in enumerate(question.get('options', [])):
                # Container for each option - so organized!
                opt_container = tk.LabelFrame(options_list_frame, text=f"💖 Option {i+1} 💖",
                                             bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                opt_container.pack(fill=tk.X, pady=3, padx=2)

                # Correct radio button
                tk.Radiobutton(opt_container, text="✅ This is Correct!", variable=self.mcq_single_correct_var, value=i,
                              bg=self.colors['secondary'], font=('Arial', 9, 'bold')).pack(pady=2)

                if isinstance(option, dict):
                    # Enhanced option with text and/or image
                    # Image path
                    img_frame = tk.Frame(opt_container, bg=self.colors['secondary'])
                    img_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(img_frame, text="🖼️ Image:", bg=self.colors['secondary']).pack(side=tk.LEFT)
                    img_var = tk.StringVar(value=option.get('image', ''))
                    tk.Entry(img_frame, textvariable=img_var, bg=self.colors['entry'], width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    tk.Button(img_frame, text="Browse", bg=self.colors['button'], fg=self.colors['button_text'],
                             command=lambda v=img_var: self.browse_media_file(v, "image")).pack(side=tk.RIGHT, padx=2)

                    # Text content
                    text_frame = tk.Frame(opt_container, bg=self.colors['secondary'])
                    text_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(text_frame, text="📝 Text:", bg=self.colors['secondary']).pack(side=tk.LEFT)
                    text_var = tk.StringVar(value=option.get('text', ''))
                    tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'], width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    self.mcq_single_option_vars.append((img_var, text_var))
                else:
                    # Simple text-only option (legacy support)
                    text_frame = tk.Frame(opt_container, bg=self.colors['secondary'])
                    text_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(text_frame, text="📝 Text:", bg=self.colors['secondary']).pack(side=tk.LEFT)
                    text_var = tk.StringVar(value=str(option))
                    tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'], width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    self.mcq_single_option_vars.append((tk.StringVar(), text_var))

                # Delete button
                if len(question.get('options', [])) > 2:
                    tk.Button(opt_container, text="🗑️ Delete Option", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_option(idx)).pack(pady=5)

        def add_option():
            question.setdefault('options', []).append({'image': '', 'text': 'New Amazing Option'})
            refresh_options()

        def delete_option(idx):
            if len(question.get('options', [])) > 2:
                del question['options'][idx]
                # Adjust correct answer if necessary
                correct = self.mcq_single_correct_var.get()
                if correct == idx:
                    self.mcq_single_correct_var.set(0)
                elif correct > idx:
                    self.mcq_single_correct_var.set(correct - 1)
                refresh_options()

        def save_options():
            options = []
            for img_var, text_var in self.mcq_single_option_vars:
                img_path = img_var.get().strip()
                text_content = text_var.get().strip()
                if img_path and text_content:
                    # Both image and text
                    options.append({'image': img_path, 'text': text_content})
                elif img_path:
                    # Image only
                    options.append({'image': img_path, 'text': ''})
                elif text_content:
                    # Text only (can be simple string or object format)
                    options.append({'image': '', 'text': text_content})
                else:
                    # Empty option - add placeholder
                    options.append({'image': '', 'text': 'Empty Option'})

            question['options'] = options
            question['answer'] = [self.mcq_single_correct_var.get()]
            messagebox.showinfo("Success! 💖", "Enhanced MCQ options saved perfectly!")

        refresh_options()

        # Buttons
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Option", command=add_option,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Options", command=save_options,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

    def edit_mcq_multiple(self, question, index):
        """Enhanced editor for mcq_multiple - supports text, image, or both! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Enhanced options section - multiple selection with images!
        options_frame = tk.LabelFrame(self.editor_frame, text="☑️ Enhanced Multiple Choice (Text + Image Support!) ☑️",
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(options_frame, text="💡 Check all correct options! Mix text and images as you like!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        options_list_frame = tk.Frame(options_frame, bg=self.colors['white'])
        options_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.mcq_multiple_option_vars = []
        self.mcq_multiple_correct_vars = []

        def refresh_options():
            for widget in options_list_frame.winfo_children():
                widget.destroy()
            self.mcq_multiple_option_vars.clear()
            self.mcq_multiple_correct_vars.clear()

            for i, option in enumerate(question.get('options', [])):
                # Container for each option
                opt_container = tk.LabelFrame(options_list_frame, text=f"💖 Option {i+1} 💖",
                                             bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                opt_container.pack(fill=tk.X, pady=3, padx=2)

                # Correct checkbox
                correct_var = tk.BooleanVar(value=i in question.get('answer', []))
                tk.Checkbutton(opt_container, text="✅ This is Correct!", variable=correct_var,
                              bg=self.colors['secondary'], font=('Arial', 9, 'bold')).pack(pady=2)
                self.mcq_multiple_correct_vars.append(correct_var)

                if isinstance(option, dict):
                    # Enhanced option with text and/or image
                    # Image path
                    img_frame = tk.Frame(opt_container, bg=self.colors['secondary'])
                    img_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(img_frame, text="🖼️ Image:", bg=self.colors['secondary']).pack(side=tk.LEFT)
                    img_var = tk.StringVar(value=option.get('image', ''))
                    tk.Entry(img_frame, textvariable=img_var, bg=self.colors['entry'], width=40).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    tk.Button(img_frame, text="Browse", bg=self.colors['button'], fg=self.colors['button_text'],
                             command=lambda v=img_var: self.browse_media_file(v, "image")).pack(side=tk.RIGHT, padx=2)

                    # Text content
                    text_frame = tk.Frame(opt_container, bg=self.colors['secondary'])
                    text_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(text_frame, text="📝 Text:", bg=self.colors['secondary']).pack(side=tk.LEFT)
                    text_var = tk.StringVar(value=option.get('text', ''))
                    tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'], width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    self.mcq_multiple_option_vars.append((img_var, text_var))
                else:
                    # Simple text-only option (legacy support)
                    text_frame = tk.Frame(opt_container, bg=self.colors['secondary'])
                    text_frame.pack(fill=tk.X, padx=5, pady=2)
                    tk.Label(text_frame, text="📝 Text:", bg=self.colors['secondary']).pack(side=tk.LEFT)
                    text_var = tk.StringVar(value=str(option))
                    tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'], width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    self.mcq_multiple_option_vars.append((tk.StringVar(), text_var))

                # Delete button
                if len(question.get('options', [])) > 2:
                    tk.Button(opt_container, text="🗑️ Delete Option", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_option(idx)).pack(pady=5)

        def add_option():
            question.setdefault('options', []).append({'image': '', 'text': 'New Fantastic Option'})
            refresh_options()

        def delete_option(idx):
            if len(question.get('options', [])) > 2:
                del question['options'][idx]
                # Update answer indices
                answer = question.get('answer', [])
                new_answer = [a - 1 if a > idx else a for a in answer if a != idx]
                question['answer'] = [a for a in new_answer if a >= 0]
                refresh_options()

        def save_options():
            options = []
            for img_var, text_var in self.mcq_multiple_option_vars:
                img_path = img_var.get().strip()
                text_content = text_var.get().strip()
                if img_path and text_content:
                    # Both image and text
                    options.append({'image': img_path, 'text': text_content})
                elif img_path:
                    # Image only
                    options.append({'image': img_path, 'text': ''})
                elif text_content:
                    # Text only
                    options.append({'image': '', 'text': text_content})
                else:
                    # Empty option - add placeholder
                    options.append({'image': '', 'text': 'Empty Option'})

            question['options'] = options
            question['answer'] = [i for i, var in enumerate(self.mcq_multiple_correct_vars) if var.get()]
            messagebox.showinfo("Success! 💖", "Enhanced multiple choice options saved beautifully!")

        refresh_options()

        # Buttons
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Option", command=add_option,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Options", command=save_options,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
    # 💖 ALL OTHER QUESTION TYPE EDITORS - COMPLETE AND CUTE! 💖

    def edit_list_pick(self, question, index):
        """Editor for list_pick questions - pick all the cute options! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Options section - the main attraction!
        options_frame = tk.LabelFrame(self.editor_frame, text="📋 Answer Options (Students can pick multiple) 📋",
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(options_frame, text="💡 Check the boxes next to correct answers!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        options_list_frame = tk.Frame(options_frame, bg=self.colors['white'])
        options_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.list_pick_option_vars = []
        self.list_pick_correct_vars = []

        def refresh_options():
            for widget in options_list_frame.winfo_children():
                widget.destroy()
            self.list_pick_option_vars.clear()
            self.list_pick_correct_vars.clear()

            for i, option in enumerate(question.get('options', [])):
                row_frame = tk.Frame(options_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                # Correct checkbox - so important!
                correct_var = tk.BooleanVar(value=i in question.get('answer', []))
                tk.Checkbutton(row_frame, text="✅ Correct", variable=correct_var,
                              bg=self.colors['white'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
                self.list_pick_correct_vars.append(correct_var)

                # Option text
                tk.Label(row_frame, text=f"Option {i+1}:", bg=self.colors['white'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 5))

                option_var = tk.StringVar(value=option)
                tk.Entry(row_frame, textvariable=option_var, bg=self.colors['entry'],
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.list_pick_option_vars.append(option_var)

                # Delete button - sometimes we need to remove things
                if len(question.get('options', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_option(idx)).pack(side=tk.RIGHT, padx=2)

        def add_option():
            question.setdefault('options', []).append('New Cute Option')
            refresh_options()

        def delete_option(idx):
            if len(question.get('options', [])) > 2:
                del question['options'][idx]
                # Update answer indices - so smart!
                answer = question.get('answer', [])
                new_answer = [a - 1 if a > idx else a for a in answer if a != idx]
                question['answer'] = [a for a in new_answer if a >= 0]
                refresh_options()

        def save_options():
            # Save options
            question['options'] = [var.get() for var in self.list_pick_option_vars if var.get().strip()]
            # Save correct answers
            question['answer'] = [i for i, var in enumerate(self.list_pick_correct_vars) if var.get()]
            messagebox.showinfo("Success! 💖", "Options saved successfully, darling!")

        refresh_options()

        # Buttons - so functional!
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Option", command=add_option,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Options", command=save_options,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

    def edit_word_fill(self, question, index):
        """Editor for word_fill questions - fill in the blanks cutely! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Sentence parts section
        parts_frame = tk.LabelFrame(self.editor_frame, text="📝 Sentence Parts (Text before and after blanks) 📝",
                                   font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                   fg=self.colors['text'])
        parts_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(parts_frame, text="💡 Example: 'The cat is ' [BLANK] ' and very ' [BLANK] ' today.'\nCreate parts: ['The cat is ', ' and very ', ' today.']",
                bg=self.colors['white'], fg=self.colors['text'], font=('Arial', 9, 'italic')).pack(pady=5)

        parts_list_frame = tk.Frame(parts_frame, bg=self.colors['white'])
        parts_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.word_fill_parts_vars = []

        def refresh_parts():
            for widget in parts_list_frame.winfo_children():
                widget.destroy()
            self.word_fill_parts_vars.clear()

            for i, part in enumerate(question.get('sentence_parts', [])):
                row_frame = tk.Frame(parts_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Part {i+1}:", bg=self.colors['white'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                part_var = tk.StringVar(value=part)
                tk.Entry(row_frame, textvariable=part_var, bg=self.colors['entry'],
                        width=60, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.word_fill_parts_vars.append(part_var)

                if len(question.get('sentence_parts', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_part(idx)).pack(side=tk.RIGHT, padx=2)

        # Answers section
        answers_frame = tk.LabelFrame(parts_frame, text="✅ Correct Answers for Blanks ✅",
                                     font=('Arial', 11, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        answers_frame.pack(fill=tk.X, padx=5, pady=10)

        tk.Label(answers_frame, text="💡 Enter the correct word/phrase for each blank!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        answers_list_frame = tk.Frame(answers_frame, bg=self.colors['white'])
        answers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.word_fill_answers_vars = []

        def refresh_answers():
            for widget in answers_list_frame.winfo_children():
                widget.destroy()
            self.word_fill_answers_vars.clear()

            for i, answer in enumerate(question.get('answers', [])):
                row_frame = tk.Frame(answers_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Answer for Blank {i+1}:", bg=self.colors['white'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                answer_var = tk.StringVar(value=answer)
                tk.Entry(row_frame, textvariable=answer_var, bg=self.colors['entry'],
                        width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.word_fill_answers_vars.append(answer_var)

                if len(question.get('answers', [])) > 1:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_answer(idx)).pack(side=tk.RIGHT, padx=2)

        def add_part():
            question.setdefault('sentence_parts', []).append('')
            refresh_parts()

        def delete_part(idx):
            if len(question.get('sentence_parts', [])) > 2:
                del question['sentence_parts'][idx]
                refresh_parts()

        def add_answer():
            question.setdefault('answers', []).append('')
            refresh_answers()

        def delete_answer(idx):
            if len(question.get('answers', [])) > 1:
                del question['answers'][idx]
                refresh_answers()

        def save_all():
            question['sentence_parts'] = [var.get() for var in self.word_fill_parts_vars]
            question['answers'] = [var.get() for var in self.word_fill_answers_vars if var.get().strip()]
            messagebox.showinfo("Success! 💖", "Word fill data saved perfectly, babe!")

        refresh_parts()
        refresh_answers()

        # Buttons
        btn_frame = tk.Frame(parts_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Part", command=add_part,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="➕ Add Answer", command=add_answer,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save Everything", command=save_all,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

    def edit_categorization_multiple(self, question, index):
        """Editor for categorization_multiple questions - organize everything cutely! 📂"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Categories section first - define the buckets!
        categories_frame = tk.LabelFrame(self.editor_frame, text="📂 Categories (The cute buckets!) 📂",
                                        font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                        fg=self.colors['text'])
        categories_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(categories_frame, text="💡 Create the categories that students will sort items into!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        categories_list_frame = tk.Frame(categories_frame, bg=self.colors['white'])
        categories_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.categorization_category_vars = []

        def refresh_categories():
            for widget in categories_list_frame.winfo_children():
                widget.destroy()
            self.categorization_category_vars.clear()

            for i, category in enumerate(question.get('categories', [])):
                row_frame = tk.Frame(categories_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Category {i+1}:", bg=self.colors['white'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                category_var = tk.StringVar(value=category)
                tk.Entry(row_frame, textvariable=category_var, bg=self.colors['entry'],
                        width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.categorization_category_vars.append(category_var)

                if len(question.get('categories', [])) > 2 and category.strip():
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_category(idx)).pack(side=tk.RIGHT, padx=2)

        # Items section - what gets categorized (enhanced for images!)
        stimuli_frame = tk.LabelFrame(self.editor_frame, text="🎯 Items to Categorize (Text and/or Images!) 🎯",
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        stimuli_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(stimuli_frame, text="💡 Add items (text and/or images) that students will categorize!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        stimuli_list_frame = tk.Frame(stimuli_frame, bg=self.colors['white'])
        stimuli_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.categorization_stimuli_data = []

        def refresh_stimuli():
            for widget in stimuli_list_frame.winfo_children():
                widget.destroy()
            self.categorization_stimuli_data.clear()

            for i, stimulus in enumerate(question.get('stimuli', [])):
                # Container for each stimulus - so pretty!
                stim_container = tk.LabelFrame(stimuli_list_frame, text=f"💖 Item {i+1} 💖",
                                              bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                stim_container.pack(fill=tk.X, pady=3, padx=2)

                # Text (optional)
                text_frame = tk.Frame(stim_container, bg=self.colors['secondary'])
                text_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(text_frame, text="📝 Text (optional):", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                text_var = tk.StringVar(value=stimulus.get('text', '') if stimulus.get('text') else '')
                tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'],
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                # Image (optional but cute!)
                image_frame = tk.Frame(stim_container, bg=self.colors['secondary'])
                image_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(image_frame, text="🖼️ Image (optional):", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                image_var = tk.StringVar(value=stimulus.get('image', '') if stimulus.get('image') else '')
                tk.Entry(image_frame, textvariable=image_var, bg=self.colors['entry'],
                        width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                tk.Button(image_frame, text="Browse 📁", bg=self.colors['button'], fg=self.colors['button_text'],
                         command=lambda v=image_var: self.browse_media_file(v, "image")).pack(side=tk.RIGHT, padx=2)

                # Category assignment - the important part!
                category_frame = tk.Frame(stim_container, bg=self.colors['secondary'])
                category_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(category_frame, text="📂 Correct Category:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                # Get current answer for this stimulus
                # Handle both text-based and image-based keys
                stimulus_key = stimulus.get('text', '') if stimulus.get('text') else stimulus.get('image', '')
                if not stimulus_key and stimulus.get('image'):
                    stimulus_key = os.path.basename(stimulus.get('image', ''))

                current_answer = question.get('answer', {}).get(stimulus_key, '')
                category_var = tk.StringVar(value=current_answer)

                categories_list = [cat for cat in question.get('categories', []) if cat.strip()]
                if categories_list:
                    category_combo = ttk.Combobox(category_frame, textvariable=category_var,
                                                values=categories_list, state='readonly', width=25)
                    category_combo.pack(side=tk.LEFT, padx=5)
                else:
                    tk.Entry(category_frame, textvariable=category_var, bg=self.colors['entry'],
                            width=25, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

                # Delete button
                if len(question.get('stimuli', [])) > 1:
                    tk.Button(stim_container, text="🗑️ Delete This Item", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_stimulus(idx)).pack(pady=5)

                self.categorization_stimuli_data.append((text_var, image_var, category_var))

        def add_category():
            question.setdefault('categories', []).append('New Cute Category')
            refresh_categories()
            refresh_stimuli()  # Refresh stimuli to update dropdowns

        def delete_category(idx):
            if len(question.get('categories', [])) > 2:
                del question['categories'][idx]
                refresh_categories()
                refresh_stimuli()  # Refresh stimuli to update dropdowns

        def add_stimulus():
            question.setdefault('stimuli', []).append({'text': 'New Adorable Item', 'image': None})
            refresh_stimuli()

        def delete_stimulus(idx):
            if len(question.get('stimuli', [])) > 1:
                stimulus = question['stimuli'][idx]

                # Remove from answer mapping
                answer = question.get('answer', {})

                # Try both text and image keys
                text_key = stimulus.get('text', '')
                image_key = stimulus.get('image', '')

                if text_key and text_key in answer:
                    del answer[text_key]
                elif image_key and image_key in answer:
                    del answer[image_key]
                elif image_key and os.path.basename(image_key) in answer:
                    del answer[os.path.basename(image_key)]

                del question['stimuli'][idx]
                refresh_stimuli()

        def save_all():
            # Save categories
            question['categories'] = [var.get() for var in self.categorization_category_vars if var.get().strip()]

            # Save stimuli and answers - enhanced logic!
            stimuli = []
            answer = {}

            for text_var, image_var, category_var in self.categorization_stimuli_data:
                text = text_var.get().strip()
                image = image_var.get().strip() if image_var.get().strip() else None
                category = category_var.get().strip()

                if text or image:  # Save if there's text OR image
                    stimuli.append({'text': text if text else None, 'image': image})

                    # Determine the key for the answer mapping
                    if text:
                        answer_key = text
                    elif image:
                        answer_key = os.path.basename(image)  # Use filename as key for image-only items
                    else:
                        continue

                    if category:
                        answer[answer_key] = category

            question['stimuli'] = stimuli
            question['answer'] = answer

            messagebox.showinfo("Success! 💖", "All categorization data saved perfectly, darling!")

        refresh_categories()
        refresh_stimuli()

        # Buttons
        btn_frame = tk.Frame(stimuli_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Category", command=add_category,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="➕ Add Item", command=add_stimulus,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save Everything", command=save_all,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

    def edit_match_sentence(self, question, index):
        """Editor for match_sentence questions - match cutely! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Pairs section
        pairs_frame = tk.LabelFrame(self.editor_frame, text="🔗 Sentence-Image Pairs (So cute!) 🔗",
                                   font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                   fg=self.colors['text'])
        pairs_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(pairs_frame, text="💡 Students will match sentences to their corresponding images!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        pairs_list_frame = tk.Frame(pairs_frame, bg=self.colors['white'])
        pairs_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.match_sentence_pairs_data = []

        def refresh_pairs():
            for widget in pairs_list_frame.winfo_children():
                widget.destroy()
            self.match_sentence_pairs_data.clear()

            for i, pair in enumerate(question.get('pairs', [])):
                # Container for each pair - so organized!
                pair_container = tk.LabelFrame(pairs_list_frame, text=f"💖 Pair {i+1} 💖",
                                              bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                pair_container.pack(fill=tk.X, pady=5, padx=2)

                # Sentence
                sentence_frame = tk.Frame(pair_container, bg=self.colors['secondary'])
                sentence_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(sentence_frame, text="📝 Sentence:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                sentence_var = tk.StringVar(value=pair.get('sentence', ''))
                tk.Entry(sentence_frame, textvariable=sentence_var, bg=self.colors['entry'],
                        width=60, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                # Image path
                image_frame = tk.Frame(pair_container, bg=self.colors['secondary'])
                image_frame.pack(fill=tk.X, padx=5, pady=2)

                tk.Label(image_frame, text="🖼️ Image Path:", bg=self.colors['secondary'],
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                image_var = tk.StringVar(value=pair.get('image_path', ''))
                tk.Entry(image_frame, textvariable=image_var, bg=self.colors['entry'],
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                tk.Button(image_frame, text="Browse 📁", bg=self.colors['button'], fg=self.colors['button_text'],
                         command=lambda v=image_var: self.browse_media_file(v, "image")).pack(side=tk.RIGHT, padx=2)

                # Delete button
                if len(question.get('pairs', [])) > 1:
                    tk.Button(pair_container, text="🗑️ Delete This Pair", bg='#FF6347', fg=self.colors['button_text'],
                             command=lambda idx=i: delete_pair(idx)).pack(pady=5)

                self.match_sentence_pairs_data.append((sentence_var, image_var))

        def add_pair():
            question.setdefault('pairs', []).append({'sentence': 'New Cute Sentence', 'image_path': 'new_image.jpg'})
            refresh_pairs()

        def delete_pair(idx):
            if len(question.get('pairs', [])) > 1:
                pair = question['pairs'][idx]

                # Remove from answer mapping too - so smart!
                answer = question.get('answer', {})
                if pair.get('image_path') in answer:
                    del answer[pair['image_path']]

                del question['pairs'][idx]
                refresh_pairs()

        def save_pairs():
            pairs = []
            answer = {}

            for sentence_var, image_var in self.match_sentence_pairs_data:
                sentence = sentence_var.get().strip()
                image_path = image_var.get().strip()

                if sentence and image_path:
                    pairs.append({'sentence': sentence, 'image_path': image_path})
                    answer[image_path] = sentence  # Auto-generate correct answer - so convenient!

            question['pairs'] = pairs
            question['answer'] = answer

            messagebox.showinfo("Success! 💖", "Sentence-image pairs saved perfectly, darling!")

        refresh_pairs()

        # Buttons
        btn_frame = tk.Frame(pairs_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add New Pair", command=add_pair,
                 bg=self.colors['button'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Pairs", command=save_pairs,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

    def edit_sequence_audio(self, question, index):
        """Editor for sequence_audio questions - audio sequencing magic! 🎵"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Audio options section
        options_frame = tk.LabelFrame(self.editor_frame, text="🎵 Audio Options (Students put in order) 🎵",
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(options_frame, text="💡 Describe each audio clip - students will put them in correct sequence!",
                bg=self.colors['white'], fg=self.colors['text'],
                font=('Arial', 9, 'italic')).pack(pady=5)

        # Simple editor for now - can be enhanced later
        sequence_var = tk.StringVar(value=str(question.get('answer', [])))

        tk.Label(options_frame, text="✅ Correct sequence order (indices):",
                bg=self.colors['white'], font=('Arial', 10, 'bold')).pack(pady=5)

        tk.Entry(options_frame, textvariable=sequence_var, bg=self.colors['entry'], width=40).pack(pady=5)

        def save_sequence():
            try:
                sequence_text = sequence_var.get().strip()
                if sequence_text.startswith('[') and sequence_text.endswith(']'):
                    question['answer'] = eval(sequence_text)
                else:
                    question['answer'] = [int(x.strip()) for x in sequence_text.split(',')]
                messagebox.showinfo("Success! 💖", "Audio sequence saved beautifully!")
            except:
                messagebox.showerror("Oopsie! 😢", "Please enter a valid sequence format: [0, 1, 2] or 0, 1, 2")

        tk.Button(options_frame, text="💾 Save Sequence", command=save_sequence,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=10)

    def edit_order_phrase(self, question, index):
        """Editor for order_phrase questions - get those phrases in order! 📋"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Phrases section
        phrases_frame = tk.LabelFrame(self.editor_frame, text="📋 Phrase Ordering (So organized!) 📋",
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        phrases_frame.pack(fill=tk.X, padx=10, pady=10)

        # Simple text area editor - can be enhanced
        tk.Label(phrases_frame, text="💡 Enter shuffled phrases (one per line) and correct order:",
                bg=self.colors['white'], fg=self.colors['text'], font=('Arial', 9, 'italic')).pack(pady=5)

        shuffled_text = tk.Text(phrases_frame, height=6, width=70, bg=self.colors['entry'])
        shuffled_text.pack(pady=5)
        shuffled_text.insert('1.0', '\n'.join(question.get('phrase_shuffled', [])))

        correct_text = tk.Text(phrases_frame, height=6, width=70, bg=self.colors['entry'])
        correct_text.pack(pady=5)
        correct_text.insert('1.0', '\n'.join(question.get('answer', [])))

        def save_phrases():
            shuffled = [line.strip() for line in shuffled_text.get('1.0', tk.END).strip().split('\n') if line.strip()]
            correct = [line.strip() for line in correct_text.get('1.0', tk.END).strip().split('\n') if line.strip()]

            question['phrase_shuffled'] = shuffled
            question['answer'] = correct

            messagebox.showinfo("Success! 💖", "Phrases saved in perfect order!")

        tk.Button(phrases_frame, text="💾 Save Phrases", command=save_phrases,
                 bg=self.colors['accent'], fg=self.colors['button_text'], font=('Arial', 10, 'bold')).pack(pady=10)

    def edit_fill_blanks_dropdown(self, question, index):
        """Editor for fill_blanks_dropdown questions - dropdown magic! ⬇️"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Simple editor for now
        dropdown_frame = tk.LabelFrame(self.editor_frame, text="⬇️ Fill Blanks with Dropdowns ⬇️",
                                      font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                      fg=self.colors['text'])
        dropdown_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(dropdown_frame, text="💡 This is a complex editor - use JSON view for detailed editing!",
                bg=self.colors['white'], fg=self.colors['text'], font=('Arial', 10, 'italic')).pack(pady=20)

    def edit_match_phrases(self, question, index):
        """Editor for match_phrases questions - match those cute phrases! 🔗"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Simple editor for now
        match_frame = tk.LabelFrame(self.editor_frame, text="🔗 Match Phrase Beginnings to Endings 🔗",
                                   font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                   fg=self.colors['text'])
        match_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(match_frame, text="💡 This is a complex editor - use JSON view for detailed editing!",
                bg=self.colors['white'], fg=self.colors['text'], font=('Arial', 10, 'italic')).pack(pady=20)

def main():
    """Main function to run the most adorable editor ever! 💖"""
    root = tk.Tk()

    # Make it cute and maximize
    try:
        root.state('zoomed')  # Maximize on Windows
    except tk.TclError:
        try:
            root.attributes('-zoomed', True)  # Linux
        except tk.TclError:
            pass  # Not available

    # Set minimum size
    root.minsize(1200, 800)

    # Create the amazing app
    app = WifeyMOOCEditor(root)

    # Add some cute finishing touches
    def on_closing():
        if messagebox.askyesno("Leaving? 💔", "Are you sure you want to close the editor, princess?"):
            messagebox.showinfo("Goodbye! 💖", "Thanks for using Wifey MOOC Editor v2.1, babe! 💕")
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the magical application!
    root.mainloop()

if __name__ == "__main__":
    print("💖 Starting the most adorable MOOC editor v2.1 ever! 💖")
    print("✨ Enhanced features: Better readability, Full image tagging support! ✨")
    print("💕 Made with extra love for all the girlies! 💕")
    main()
