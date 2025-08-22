#!/usr/bin/env python3
"""
💖 Wifey MOOC JSON Editor 💖
A complete WYSIWYG editor for WifeyMOOC quiz questions
Created with love and lots of pink! 💕

This is the COMPLETE implementation with all question type editors!
No placeholders - everything is fully functional! 💖
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
import subprocess
import shutil
from typing import Dict, List, Any

class WifeyMOOCEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("💖 Wifey MOOC JSON Editor 💖")
        self.root.geometry("1200x800")

        # Pink color scheme - so cute! 💕
        self.colors = {
            'bg': '#FFB6C1',           # Light pink
            'secondary': '#FFC0CB',     # Pink
            'accent': '#FF69B4',        # Hot pink
            'text': '#8B008B',          # Dark magenta
            'white': "#FFFFFF",         # White
            'button': '#FF1493',        # Deep pink
            'entry': '#FFEFD5'          # Papaya whip
        }

        self.wifeymooc_app_path = "/Applications/WifeyMOOC.app/Contents/MacOS/WifeyMOOC"

        # Configure root
        self.root.configure(bg=self.colors['bg'])

        # Data storage
        self.questions = []
        self.current_file = None
        self.current_question_index = None

        # Question type templates - all supported types! ✨
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
                'options': ['Option A', 'Option B', 'Option C'],
                'answer': [0],
                'media': None
            },
            'mcq_multiple': {
                'type': 'mcq_multiple',
                'question': 'Pick all the right answers, sweetie! 💖',
                'options': ['Option A', 'Option B', 'Option C'],
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
                'pairs': [
                    {
                        'source': 'Beginning of cute phrase 1...',
                        'targets': [' ', 'ending A', 'ending B', 'ending C']
                    }
                ],
                'answer': {'Beginning of cute phrase 1...': 'ending A'},
                'media': None
            }
        }

        self.setup_ui()

    def setup_ui(self):
        """Setup the gorgeous pink UI! 💖"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Cute title
        title = tk.Label(main_frame, text="💖 Wifey MOOC Question Editor 💖", 
                        font=('Comic Sans MS', 20, 'bold'), 
                        bg=self.colors['bg'], fg=self.colors['text'])
        title.pack(pady=10)

        # Top buttons frame - so functional and cute!
        buttons_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        buttons_frame.pack(fill=tk.X, pady=5)

        tk.Button(buttons_frame, text="✨ New JSON", command=self.new_json,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="💾 Load JSON", command=self.load_json,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="💖 Save JSON", command=self.save_json,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="💖 Save As", command=self.save_json_as,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Button(buttons_frame, text="🚀 Save & Launch", command=self.save_and_launch,
          bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(buttons_frame, text="✨ New Question", command=self.show_add_question_dialog,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        # Main content area - two gorgeous panels
        content_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Left panel - questions list (so organized!)
        left_frame = tk.Frame(content_frame, bg=self.colors['secondary'], relief=tk.RAISED, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        tk.Label(left_frame, text="💕 Questions List 💕", font=('Arial', 12, 'bold'),
                bg=self.colors['secondary'], fg=self.colors['text']).pack(pady=5)

        # Questions listbox with scrollbar
        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.questions_listbox = tk.Listbox(list_frame, width=30, height=20,
                                          bg=self.colors['white'], 
                                          selectbackground=self.colors['accent'])
        scrollbar_list = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.questions_listbox.config(yscrollcommand=scrollbar_list.set)
        scrollbar_list.config(command=self.questions_listbox.yview)

        self.questions_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)

        self.questions_listbox.bind('<<ListboxSelect>>', self.on_question_select)

        # List management buttons - so cute and functional!
        list_buttons_frame = tk.Frame(left_frame, bg=self.colors['secondary'])
        list_buttons_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(list_buttons_frame, text="🗑️ Delete", command=self.delete_question,
                 bg='#FF6347', fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(list_buttons_frame, text="⬆️ Up", command=self.move_question_up,
                 bg=self.colors['button'], fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(list_buttons_frame, text="⬇️ Down", command=self.move_question_down,
                 bg=self.colors['button'], fg='black', font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

        # Right panel - question editor (the main attraction!)
        self.right_frame = tk.Frame(content_frame, bg=self.colors['white'], relief=tk.RAISED, bd=2)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Welcome message
        self.show_welcome_message()

    def show_welcome_message(self):
        """Show the cutest welcome message ever! 💖"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        welcome_label = tk.Label(self.right_frame, 
                                text="💖 Welcome to Wifey MOOC Editor! 💖\n\n" +
                                     "✨ Load a JSON file or create new questions to get started ✨\n\n" +
                                     "💕 Made with love for all the girlies! 💕",
                                font=('Comic Sans MS', 16, 'bold'),
                                bg=self.colors['white'], fg=self.colors['text'],
                                justify=tk.CENTER)
        welcome_label.pack(expand=True)

    # 💖 FILE OPERATIONS - SO ORGANIZED! 💖
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
        """Load questions from JSON file - magic! ✨"""
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
        """Save questions to JSON file - preserve the cuteness! 💾"""
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
        """Refresh the questions listbox - keep it fresh! 💫"""
        self.questions_listbox.delete(0, tk.END)
        for i, question in enumerate(self.questions):
            qtype = question.get('type', 'unknown')
            qtext = question.get('question', 'No question text')
            # Truncate long questions cutely
            if len(qtext) > 40:
                qtext = qtext[:40] + "... 💖"
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
        """Handle question selection from list - so responsive! 💕"""
        selection = self.questions_listbox.curselection()
        if selection:
            index = selection[0]
            self.current_question_index = index
            self.edit_question(index)

    def show_add_question_dialog(self):
        """Show the cutest dialog to add new questions! ✨"""
        dialog = tk.Toplevel(self.root)
        dialog.title("✨ Add New Adorable Question ✨")
        dialog.geometry("450x550")
        dialog.configure(bg=self.colors['bg'])
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog perfectly
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))

        tk.Label(dialog, text="💖 Choose Your Question Type, Babe! 💖", 
                font=('Comic Sans MS', 14, 'bold'),
                bg=self.colors['bg'], fg=self.colors['text']).pack(pady=10)

        # Question type buttons - all the cute options!
        button_frame = tk.Frame(dialog, bg=self.colors['bg'])
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        question_types = [
            ('📝 List Pick (Select Multiple)', 'list_pick'),
            ('🔘 Single Choice (MCQ)', 'mcq_single'),
            ('☑️ Multiple Choice (MCQ)', 'mcq_multiple'),
            ('📝 Word Fill (Fill Blanks)', 'word_fill'),
            ('🔗 Match Sentences to Images', 'match_sentence'),
            ('🎵 Audio Sequence Order', 'sequence_audio'),
            ('📋 Order Phrases Correctly', 'order_phrase'),
            ('📂 Categorization Multiple', 'categorization_multiple'),
            ('⬇️ Fill Blanks with Dropdowns', 'fill_blanks_dropdown'),
            ('🔗 Match Phrase Beginnings to Endings', 'match_phrases')
        ]

        for i, (display_name, qtype) in enumerate(question_types):
            btn = tk.Button(button_frame, text=display_name, 
                           command=lambda t=qtype: self.add_question(t, dialog),
                           bg=self.colors['accent'], fg='black', 
                           font=('Arial', 10, 'bold'), width=35)
            btn.pack(pady=3, padx=5, fill=tk.X)

        # Cancel button
        tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy,
                 bg='#FF6347', fg='black', font=('Arial', 10, 'bold')).pack(pady=15)

    def add_question(self, question_type, dialog):
        """Add a new question of specified type - so exciting! 💖"""
        if question_type in self.question_templates:
            new_question = self.question_templates[question_type].copy()

            # Deep copy for nested structures (so important!)
            if 'pairs' in new_question:
                new_question['pairs'] = [pair.copy() for pair in new_question['pairs']]
            if 'stimuli' in new_question:
                new_question['stimuli'] = [stim.copy() for stim in new_question['stimuli']]
            if 'audio_options' in new_question:
                new_question['audio_options'] = [opt.copy() for opt in new_question['audio_options']]
            if 'options_for_blanks' in new_question:
                new_question['options_for_blanks'] = [opts.copy() for opts in new_question['options_for_blanks']]

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

    # 💖 COMMON EDITOR COMPONENTS - REUSABLE CUTENESS! 💖
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
        tk.Button(video_frame, text="Browse 📁", bg=self.colors['button'], fg='black',
                 command=lambda: self.browse_media_file(video_var, "video")).pack(side=tk.RIGHT, padx=5)

        # Audio section
        audio_frame = tk.Frame(media_frame, bg=self.colors['white'])
        audio_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(audio_frame, text="🎵 Audio File:", bg=self.colors['white'], 
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        audio_var = tk.StringVar(value=media.get('audio', ''))
        audio_entry = tk.Entry(audio_frame, textvariable=audio_var, width=50, bg=self.colors['entry'])
        audio_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(audio_frame, text="Browse 📁", bg=self.colors['button'], fg='black',
                 command=lambda: self.browse_media_file(audio_var, "audio")).pack(side=tk.RIGHT, padx=5)

        # Image section
        image_frame = tk.Frame(media_frame, bg=self.colors['white'])
        image_frame.pack(fill=tk.X, padx=5, pady=2)
        tk.Label(image_frame, text="🖼️ Image File:", bg=self.colors['white'], 
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        image_var = tk.StringVar(value=media.get('image', ''))
        image_entry = tk.Entry(image_frame, textvariable=image_var, width=50, bg=self.colors['entry'])
        image_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(image_frame, text="Browse 📁", bg=self.colors['button'], fg='black',
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
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(pady=8)

    def create_question_text_section(self, question, index):
        """Create the question text editing section - the heart of it all! 💖"""
        text_frame = tk.LabelFrame(self.editor_frame, text="📝 Question Text 📝", 
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
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(pady=5)

    def edit_question(self, index):
        """Edit question at specified index - the main magic! ✨"""
        if index < 0 or index >= len(self.questions):
            return

        question = self.questions[index]
        qtype = question.get('type')

        # Clear the right panel
        for widget in self.right_frame.winfo_children():
            widget.destroy()

        # Create scrollable frame for the editor - so organized!
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

        # Gorgeous title
        title_text = f"💖 Editing Question {index + 1}: {qtype.replace('_', ' ').title()} 💖"
        tk.Label(self.editor_frame, text=title_text, font=('Comic Sans MS', 16, 'bold'),
                bg=self.colors['white'], fg=self.colors['text']).pack(pady=10)

        # Call appropriate editor based on question type
        editor_method = getattr(self, f'edit_{qtype}', None)
        if editor_method:
            editor_method(question, index)
        else:
            tk.Label(self.editor_frame, text=f"❌ Oopsie! Unsupported question type: {qtype}",
                    font=('Arial', 12), bg=self.colors['white'], fg='red').pack(pady=20)

    # 💖 SPECIFIC QUESTION TYPE EDITORS - ALL THE CUTENESS! 💖

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
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
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
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Options", command=save_options,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

    def edit_mcq_single(self, question, index):
        """Editor for mcq_single questions - pick the ONE perfect answer! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Options section
        options_frame = tk.LabelFrame(self.editor_frame, text="🔘 Answer Options (Students pick only ONE) 🔘", 
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(options_frame, text="💡 Select the radio button next to the correct answer!", 
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
                row_frame = tk.Frame(options_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                # Correct radio button - only one can be chosen!
                tk.Radiobutton(row_frame, text="✅ Correct", variable=self.mcq_single_correct_var, value=i,
                              bg=self.colors['white'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT)

                # Option text
                tk.Label(row_frame, text=f"Option {i+1}:", bg=self.colors['white'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 5))
                option_var = tk.StringVar(value=option)
                tk.Entry(row_frame, textvariable=option_var, bg=self.colors['entry'], 
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.mcq_single_option_vars.append(option_var)

                # Delete button
                if len(question.get('options', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_option(idx)).pack(side=tk.RIGHT, padx=2)

        def add_option():
            question.setdefault('options', []).append('New Amazing Option')
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
            question['options'] = [var.get() for var in self.mcq_single_option_vars if var.get().strip()]
            question['answer'] = [self.mcq_single_correct_var.get()]
            messagebox.showinfo("Success! 💖", "Single choice options saved perfectly!")

        refresh_options()

        # Buttons
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Option", command=add_option,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Options", command=save_options,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

    def edit_mcq_multiple(self, question, index):
        """Editor for mcq_multiple questions - pick multiple cute answers! 💖"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Options section - multiple choices allowed!
        options_frame = tk.LabelFrame(self.editor_frame, text="☑️ Answer Options (Students can pick MULTIPLE) ☑️", 
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(options_frame, text="💡 Check all the boxes next to correct answers!", 
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
                row_frame = tk.Frame(options_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                # Correct checkbox
                correct_var = tk.BooleanVar(value=i in question.get('answer', []))
                tk.Checkbutton(row_frame, text="✅ Correct", variable=correct_var, 
                              bg=self.colors['white'], font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
                self.mcq_multiple_correct_vars.append(correct_var)

                # Option text
                tk.Label(row_frame, text=f"Option {i+1}:", bg=self.colors['white'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 5))
                option_var = tk.StringVar(value=option)
                tk.Entry(row_frame, textvariable=option_var, bg=self.colors['entry'], 
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.mcq_multiple_option_vars.append(option_var)

                # Delete button
                if len(question.get('options', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_option(idx)).pack(side=tk.RIGHT, padx=2)

        def add_option():
            question.setdefault('options', []).append('New Fantastic Option')
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
            question['options'] = [var.get() for var in self.mcq_multiple_option_vars if var.get().strip()]
            question['answer'] = [i for i, var in enumerate(self.mcq_multiple_correct_vars) if var.get()]
            messagebox.showinfo("Success! 💖", "Multiple choice options saved beautifully!")

        refresh_options()

        # Buttons
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Option", command=add_option,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Options", command=save_options,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

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
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
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
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
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
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="➕ Add Answer", command=add_answer,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save Everything", command=save_all,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

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
                tk.Button(image_frame, text="Browse 📁", bg=self.colors['button'], fg='black',
                         command=lambda v=image_var: self.browse_media_file(v, "image")).pack(side=tk.LEFT, padx=2)

                # Delete button
                if len(question.get('pairs', [])) > 1:
                    tk.Button(pair_container, text="🗑️ Delete This Pair", bg='#FF6347', fg='black',
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
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Pairs", command=save_pairs,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

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

        options_list_frame = tk.Frame(options_frame, bg=self.colors['white'])
        options_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.sequence_audio_option_vars = []

        def refresh_options():
            for widget in options_list_frame.winfo_children():
                widget.destroy()
            self.sequence_audio_option_vars.clear()

            for i, option in enumerate(question.get('audio_options', [])):
                row_frame = tk.Frame(options_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"🎵 Audio {i+1} Description:", bg=self.colors['white'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                option_var = tk.StringVar(value=option.get('option', ''))
                tk.Entry(row_frame, textvariable=option_var, bg=self.colors['entry'], 
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.sequence_audio_option_vars.append(option_var)

                if len(question.get('audio_options', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_option(idx)).pack(side=tk.RIGHT, padx=2)

        # Correct sequence section
        sequence_frame = tk.LabelFrame(options_frame, text="✅ Correct Sequence Order ✅", 
                                      font=('Arial', 11, 'bold'), bg=self.colors['white'],
                                      fg=self.colors['text'])
        sequence_frame.pack(fill=tk.X, padx=5, pady=10)

        tk.Label(sequence_frame, text="💡 Enter correct order using indices (0, 1, 2, etc.)\nExample: [2, 0, 1] means 3rd item first, then 1st, then 2nd",
                bg=self.colors['white'], fg=self.colors['text'], font=('Arial', 9, 'italic')).pack(pady=5)

        sequence_var = tk.StringVar(value=str(question.get('answer', [])))
        sequence_entry = tk.Entry(sequence_frame, textvariable=sequence_var, bg=self.colors['entry'], 
                                 width=40, justify=tk.CENTER, font=('Arial', 11))
        sequence_entry.pack(pady=5)

        def add_option():
            question.setdefault('audio_options', []).append({'option': 'New Audio Description'})
            refresh_options()

        def delete_option(idx):
            if len(question.get('audio_options', [])) > 2:
                del question['audio_options'][idx]
                refresh_options()

        def save_all():
            # Save options
            question['audio_options'] = [{'option': var.get()} for var in self.sequence_audio_option_vars if var.get().strip()]

            # Save sequence
            try:
                sequence_text = sequence_var.get().strip()
                if sequence_text.startswith('[') and sequence_text.endswith(']'):
                    sequence = eval(sequence_text)  # Simple eval for list parsing
                else:
                    sequence = [int(x.strip()) for x in sequence_text.split(',')]

                if isinstance(sequence, list) and all(isinstance(x, int) for x in sequence):
                    question['answer'] = sequence
                    messagebox.showinfo("Success! 💖", "Audio sequence saved beautifully!")
                else:
                    messagebox.showerror("Oopsie! 😢", "Please enter a valid sequence format: [0, 1, 2] or 0, 1, 2")
            except:
                messagebox.showerror("Oopsie! 😢", "Please enter a valid sequence format: [0, 1, 2] or 0, 1, 2")

        refresh_options()

        # Buttons
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Audio Option", command=add_option,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save Everything", command=save_all,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

    def edit_order_phrase(self, question, index):
        """Editor for order_phrase questions - get those phrases in order! 📋"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Phrases section
        phrases_frame = tk.LabelFrame(self.editor_frame, text="📋 Phrase Ordering (So organized!) 📋", 
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        phrases_frame.pack(fill=tk.X, padx=10, pady=10)

        # Shuffled phrases (what students see)
        shuffled_frame = tk.LabelFrame(phrases_frame, text="🔀 Shuffled Order (What students see first)", 
                                      font=('Arial', 11, 'bold'), bg=self.colors['white'],
                                      fg=self.colors['text'])
        shuffled_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(shuffled_frame, text="💡 These are shown to students in random/incorrect order", 
                bg=self.colors['white'], fg=self.colors['text'], 
                font=('Arial', 9, 'italic')).pack(pady=2)

        shuffled_list_frame = tk.Frame(shuffled_frame, bg=self.colors['white'])
        shuffled_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.order_phrase_shuffled_vars = []

        def refresh_shuffled():
            for widget in shuffled_list_frame.winfo_children():
                widget.destroy()
            self.order_phrase_shuffled_vars.clear()

            for i, phrase in enumerate(question.get('phrase_shuffled', [])):
                row_frame = tk.Frame(shuffled_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Phrase {i+1}:", bg=self.colors['white'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                phrase_var = tk.StringVar(value=phrase)
                tk.Entry(row_frame, textvariable=phrase_var, bg=self.colors['entry'], 
                        width=60, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.order_phrase_shuffled_vars.append(phrase_var)

                if len(question.get('phrase_shuffled', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_shuffled_phrase(idx)).pack(side=tk.RIGHT, padx=2)

        # Correct order (the answer)
        correct_frame = tk.LabelFrame(phrases_frame, text="✅ Correct Order (The right answer!)", 
                                     font=('Arial', 11, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        correct_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(correct_frame, text="💡 This is the correct sequence students should achieve!", 
                bg=self.colors['white'], fg=self.colors['text'], 
                font=('Arial', 9, 'italic')).pack(pady=2)

        correct_list_frame = tk.Frame(correct_frame, bg=self.colors['white'])
        correct_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.order_phrase_correct_vars = []

        def refresh_correct():
            for widget in correct_list_frame.winfo_children():
                widget.destroy()
            self.order_phrase_correct_vars.clear()

            for i, phrase in enumerate(question.get('answer', [])):
                row_frame = tk.Frame(correct_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Position {i+1}:", bg=self.colors['white'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                phrase_var = tk.StringVar(value=phrase)
                tk.Entry(row_frame, textvariable=phrase_var, bg=self.colors['entry'], 
                        width=60, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.order_phrase_correct_vars.append(phrase_var)

                if len(question.get('answer', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_correct_phrase(idx)).pack(side=tk.RIGHT, padx=2)

        def add_shuffled_phrase():
            question.setdefault('phrase_shuffled', []).append('New Phrase to Order')
            refresh_shuffled()

        def delete_shuffled_phrase(idx):
            if len(question.get('phrase_shuffled', [])) > 2:
                del question['phrase_shuffled'][idx]
                refresh_shuffled()

        def add_correct_phrase():
            question.setdefault('answer', []).append('New Correct Phrase')
            refresh_correct()

        def delete_correct_phrase(idx):
            if len(question.get('answer', [])) > 2:
                del question['answer'][idx]
                refresh_correct()

        def save_all():
            question['phrase_shuffled'] = [var.get() for var in self.order_phrase_shuffled_vars if var.get().strip()]
            question['answer'] = [var.get() for var in self.order_phrase_correct_vars if var.get().strip()]
            messagebox.showinfo("Success! 💖", "All phrases saved in perfect order, babe!")

        refresh_shuffled()
        refresh_correct()

        # Buttons
        btn_frame = tk.Frame(phrases_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Shuffled", command=add_shuffled_phrase,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="➕ Add Correct", command=add_correct_phrase,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save All Phrases", command=save_all,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

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
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_category(idx)).pack(side=tk.RIGHT, padx=2)

        # Items section - what gets categorized
        stimuli_frame = tk.LabelFrame(self.editor_frame, text="🎯 Items to Categorize (So many cute things!) 🎯", 
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

                # Text
                text_frame = tk.Frame(stim_container, bg=self.colors['secondary'])
                text_frame.pack(fill=tk.X, padx=5, pady=2)
                tk.Label(text_frame, text="📝 Text:", bg=self.colors['secondary'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
                text_var = tk.StringVar(value=stimulus.get('text', ''))
                tk.Entry(text_frame, textvariable=text_var, bg=self.colors['entry'], 
                        width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                # Image (optional but cute!)
                image_frame = tk.Frame(stim_container, bg=self.colors['secondary'])
                image_frame.pack(fill=tk.X, padx=5, pady=2)
                tk.Label(image_frame, text="🖼️ Image (optional):", bg=self.colors['secondary'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
                image_var = tk.StringVar(value=stimulus.get('image', '') or '')
                tk.Entry(image_frame, textvariable=image_var, bg=self.colors['entry'], 
                        width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                tk.Button(image_frame, text="Browse 📁", bg=self.colors['button'], fg='black',
                         command=lambda v=image_var: self.browse_media_file(v, "image")).pack(side=tk.LEFT, padx=2)

                # Category assignment - the important part!
                category_frame = tk.Frame(stim_container, bg=self.colors['secondary'])
                category_frame.pack(fill=tk.X, padx=5, pady=2)
                tk.Label(category_frame, text="📂 Correct Category:", bg=self.colors['secondary'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                # Get current answer for this stimulus
                current_answer = question.get('answer', {}).get(stimulus.get('text', ''), '')
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
                    tk.Button(stim_container, text="🗑️ Delete This Item", bg='#FF6347', fg='black',
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
                if stimulus.get('text') in answer:
                    del answer[stimulus['text']]
                del question['stimuli'][idx]
                refresh_stimuli()

        def save_all():
            # Save categories
            question['categories'] = [var.get() for var in self.categorization_category_vars if var.get().strip()]

            # Save stimuli and answers
            stimuli = []
            answer = {}
            for text_var, image_var, category_var in self.categorization_stimuli_data:
                text = text_var.get().strip()
                image = image_var.get().strip() if image_var.get().strip() else None
                category = category_var.get().strip()

                if text:  # Only save if there's text
                    stimuli.append({'text': text, 'image': image})
                    if category:
                        answer[text] = category

            question['stimuli'] = stimuli
            question['answer'] = answer
            messagebox.showinfo("Success! 💖", "All categorization data saved perfectly, darling!")

        refresh_categories()
        refresh_stimuli()

        # Buttons
        btn_frame = tk.Frame(stimuli_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Category", command=add_category,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="➕ Add Item", command=add_stimulus,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save Everything", command=save_all,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

    def edit_fill_blanks_dropdown(self, question, index):
        """Editor for fill_blanks_dropdown questions - dropdown magic! ⬇️"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Sentence parts section
        parts_frame = tk.LabelFrame(self.editor_frame, text="📝 Sentence Parts (Between dropdowns) 📝", 
                                   font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                   fg=self.colors['text'])
        parts_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(parts_frame, text="💡 Example: 'I love ' [DROPDOWN] ' and ' [DROPDOWN] ' so much!'\nParts: ['I love ', ' and ', ' so much!']",
                bg=self.colors['white'], fg=self.colors['text'], font=('Arial', 9, 'italic')).pack(pady=5)

        parts_list_frame = tk.Frame(parts_frame, bg=self.colors['white'])
        parts_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fill_blanks_parts_vars = []

        def refresh_parts():
            for widget in parts_list_frame.winfo_children():
                widget.destroy()
            self.fill_blanks_parts_vars.clear()

            for i, part in enumerate(question.get('sentence_parts', [])):
                row_frame = tk.Frame(parts_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Part {i+1}:", bg=self.colors['white'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                part_var = tk.StringVar(value=part)
                tk.Entry(row_frame, textvariable=part_var, bg=self.colors['entry'], 
                        width=60, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.fill_blanks_parts_vars.append(part_var)

                if len(question.get('sentence_parts', [])) > 2:
                    tk.Button(row_frame, text="🗑️", bg='#FF6347', fg='black',
                             command=lambda idx=i: delete_part(idx)).pack(side=tk.RIGHT, padx=2)

        # Dropdown options section - the magic happens here!
        options_frame = tk.LabelFrame(self.editor_frame, text="⬇️ Dropdown Options (So many choices!) ⬇️", 
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        options_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(options_frame, text="💡 Each dropdown can have different options - students choose one from each!", 
                bg=self.colors['white'], fg=self.colors['text'], 
                font=('Arial', 9, 'italic')).pack(pady=5)

        options_list_frame = tk.Frame(options_frame, bg=self.colors['white'])
        options_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fill_blanks_options_data = []

        def refresh_options():
            for widget in options_list_frame.winfo_children():
                widget.destroy()
            self.fill_blanks_options_data.clear()

            for i, options_list in enumerate(question.get('options_for_blanks', [])):
                # Container for each dropdown - so organized!
                dropdown_container = tk.LabelFrame(options_list_frame, text=f"💖 Dropdown {i+1} Options 💖", 
                                                  bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                dropdown_container.pack(fill=tk.X, pady=3, padx=2)

                # Options for this dropdown
                options_inner_frame = tk.Frame(dropdown_container, bg=self.colors['secondary'])
                options_inner_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                dropdown_option_vars = []

                for j, option in enumerate(options_list):
                    opt_row = tk.Frame(options_inner_frame, bg=self.colors['secondary'])
                    opt_row.pack(fill=tk.X, pady=1)

                    tk.Label(opt_row, text=f"  Option {j+1}:", bg=self.colors['secondary'], 
                            font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                    opt_var = tk.StringVar(value=option)
                    tk.Entry(opt_row, textvariable=opt_var, bg=self.colors['entry'], 
                            width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    dropdown_option_vars.append(opt_var)

                    if len(options_list) > 1 and option.strip():  # Don't delete empty options
                        tk.Button(opt_row, text="🗑️", bg='#FF6347', fg='black',
                                 command=lambda di=i, oi=j: delete_dropdown_option(di, oi)).pack(side=tk.RIGHT, padx=2)

                # Buttons for this dropdown
                dropdown_btn_frame = tk.Frame(dropdown_container, bg=self.colors['secondary'])
                dropdown_btn_frame.pack(fill=tk.X, pady=5)

                tk.Button(dropdown_btn_frame, text="➕ Add Option to This Dropdown", 
                         bg=self.colors['button'], fg='black', font=('Arial', 9, 'bold'),
                         command=lambda di=i: add_dropdown_option(di)).pack(side=tk.LEFT, padx=2)

                if len(question.get('options_for_blanks', [])) > 1:
                    tk.Button(dropdown_btn_frame, text="🗑️ Delete Entire Dropdown", 
                             bg='#FF6347', fg='black', font=('Arial', 9, 'bold'),
                             command=lambda di=i: delete_dropdown(di)).pack(side=tk.LEFT, padx=2)

                self.fill_blanks_options_data.append(dropdown_option_vars)

        # Answers section - the correct choices!
        answers_frame = tk.LabelFrame(self.editor_frame, text="✅ Correct Answers (One per dropdown) ✅", 
                                     font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                     fg=self.colors['text'])
        answers_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(answers_frame, text="💡 Enter the correct answer for each dropdown!", 
                bg=self.colors['white'], fg=self.colors['text'], 
                font=('Arial', 9, 'italic')).pack(pady=5)

        answers_list_frame = tk.Frame(answers_frame, bg=self.colors['white'])
        answers_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.fill_blanks_answers_vars = []

        def refresh_answers():
            for widget in answers_list_frame.winfo_children():
                widget.destroy()
            self.fill_blanks_answers_vars.clear()

            for i, answer in enumerate(question.get('answers', [])):
                row_frame = tk.Frame(answers_list_frame, bg=self.colors['white'])
                row_frame.pack(fill=tk.X, pady=2)

                tk.Label(row_frame, text=f"Correct Answer for Dropdown {i+1}:", 
                        bg=self.colors['white'], font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                answer_var = tk.StringVar(value=answer)
                tk.Entry(row_frame, textvariable=answer_var, bg=self.colors['entry'], 
                        width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                self.fill_blanks_answers_vars.append(answer_var)

        def add_part():
            question.setdefault('sentence_parts', []).append('')
            refresh_parts()

        def delete_part(idx):
            if len(question.get('sentence_parts', [])) > 2:
                del question['sentence_parts'][idx]
                refresh_parts()

        def add_dropdown():
            question.setdefault('options_for_blanks', []).append([' ', 'Option 1', 'Option 2'])
            question.setdefault('answers', []).append('Option 1')
            refresh_options()
            refresh_answers()

        def delete_dropdown(idx):
            if len(question.get('options_for_blanks', [])) > 1:
                del question['options_for_blanks'][idx]
                if idx < len(question.get('answers', [])):
                    del question['answers'][idx]
                refresh_options()
                refresh_answers()

        def add_dropdown_option(dropdown_idx):
            if dropdown_idx < len(question.get('options_for_blanks', [])):
                question['options_for_blanks'][dropdown_idx].append('New Cute Option')
                refresh_options()

        def delete_dropdown_option(dropdown_idx, option_idx):
            if (dropdown_idx < len(question.get('options_for_blanks', [])) and 
                option_idx < len(question['options_for_blanks'][dropdown_idx]) and
                len(question['options_for_blanks'][dropdown_idx]) > 1):
                del question['options_for_blanks'][dropdown_idx][option_idx]
                refresh_options()

        def save_all():
            # Save sentence parts
            question['sentence_parts'] = [var.get() for var in self.fill_blanks_parts_vars]

            # Save dropdown options
            options_for_blanks = []
            for dropdown_vars in self.fill_blanks_options_data:
                dropdown_options = [var.get() for var in dropdown_vars if var.get().strip()]
                if dropdown_options:
                    options_for_blanks.append(dropdown_options)
            question['options_for_blanks'] = options_for_blanks

            # Save answers
            question['answers'] = [var.get() for var in self.fill_blanks_answers_vars if var.get().strip()]
            messagebox.showinfo("Success! 💖", "All dropdown data saved perfectly, sweetie!")

        refresh_parts()
        refresh_options()
        refresh_answers()

        # Main buttons
        btn_frame = tk.Frame(options_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add Sentence Part", command=add_part,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="➕ Add New Dropdown", command=add_dropdown,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

        tk.Button(btn_frame, text="💾 Save Everything", command=save_all,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)

    def edit_match_phrases(self, question, index):
        """Editor for match_phrases questions - match those cute phrases! 🔗"""
        self.create_question_text_section(question, index)
        self.create_media_section(question, index)

        # Pairs section - the main attraction!
        pairs_frame = tk.LabelFrame(self.editor_frame, text="🔗 Phrase Matching Pairs (So romantic!) 🔗", 
                                   font=('Arial', 12, 'bold'), bg=self.colors['white'],
                                   fg=self.colors['text'])
        pairs_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(pairs_frame, text="💡 Students match phrase beginnings with their perfect endings!", 
                bg=self.colors['white'], fg=self.colors['text'], 
                font=('Arial', 9, 'italic')).pack(pady=5)

        pairs_list_frame = tk.Frame(pairs_frame, bg=self.colors['white'])
        pairs_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.match_phrases_pairs_data = []

        def refresh_pairs():
            for widget in pairs_list_frame.winfo_children():
                widget.destroy()
            self.match_phrases_pairs_data.clear()

            for i, pair in enumerate(question.get('pairs', [])):
                # Container for each pair - so beautiful!
                pair_container = tk.LabelFrame(pairs_list_frame, text=f"💖 Matching Pair {i+1} 💖", 
                                              bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                pair_container.pack(fill=tk.X, pady=5, padx=2)

                # Source phrase (the beginning)
                source_frame = tk.Frame(pair_container, bg=self.colors['secondary'])
                source_frame.pack(fill=tk.X, padx=5, pady=3)
                tk.Label(source_frame, text="📝 Phrase Beginning:", bg=self.colors['secondary'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
                source_var = tk.StringVar(value=pair.get('source', ''))
                tk.Entry(source_frame, textvariable=source_var, bg=self.colors['entry'], 
                        width=60, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

                # Target options (possible endings)
                targets_frame = tk.LabelFrame(pair_container, text="🎯 Possible Endings (Students choose from these)", 
                                             bg=self.colors['secondary'], font=('Arial', 10, 'bold'))
                targets_frame.pack(fill=tk.X, padx=5, pady=5)

                targets_list_frame = tk.Frame(targets_frame, bg=self.colors['secondary'])
                targets_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

                target_vars = []
                for j, target in enumerate(pair.get('targets', [])):
                    target_row = tk.Frame(targets_list_frame, bg=self.colors['secondary'])
                    target_row.pack(fill=tk.X, pady=1)

                    tk.Label(target_row, text=f"  Option {j+1}:", bg=self.colors['secondary'], 
                            font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                    target_var = tk.StringVar(value=target)
                    tk.Entry(target_row, textvariable=target_var, bg=self.colors['entry'], 
                            width=50, font=('Arial', 10)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
                    target_vars.append(target_var)

                    if len(pair.get('targets', [])) > 2 and target.strip():
                        tk.Button(target_row, text="🗑️", bg='#FF6347', fg='black',
                                 command=lambda pi=i, ti=j: delete_target(pi, ti)).pack(side=tk.RIGHT, padx=2)

                # Correct answer for this pair - the perfect match!
                answer_frame = tk.Frame(pair_container, bg=self.colors['secondary'])
                answer_frame.pack(fill=tk.X, padx=5, pady=3)
                tk.Label(answer_frame, text="✅ Correct Ending:", bg=self.colors['secondary'], 
                        font=('Arial', 10, 'bold')).pack(side=tk.LEFT)

                current_answer = question.get('answer', {}).get(pair.get('source', ''), '')
                answer_var = tk.StringVar(value=current_answer)

                # Create combobox with current targets
                targets_list = [t for t in pair.get('targets', []) if t.strip()]
                if targets_list:
                    answer_combo = ttk.Combobox(answer_frame, textvariable=answer_var, 
                                               values=targets_list, state='readonly', width=40)
                    answer_combo.pack(side=tk.LEFT, padx=5)
                else:
                    tk.Entry(answer_frame, textvariable=answer_var, bg=self.colors['entry'], 
                            width=40, font=('Arial', 10)).pack(side=tk.LEFT, padx=5)

                # Buttons for this pair
                pair_btn_frame = tk.Frame(pair_container, bg=self.colors['secondary'])
                pair_btn_frame.pack(fill=tk.X, pady=5)

                tk.Button(pair_btn_frame, text="➕ Add Target Option", bg=self.colors['button'], fg='black',
                         command=lambda pi=i: add_target(pi), font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

                if len(question.get('pairs', [])) > 1:
                    tk.Button(pair_btn_frame, text="🗑️ Delete Entire Pair", bg='#FF6347', fg='black',
                             command=lambda pi=i: delete_pair(pi), font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=2)

                self.match_phrases_pairs_data.append((source_var, target_vars, answer_var))

        def add_pair():
            new_pair = {
                'source': 'New phrase beginning...',
                'targets': [' ', 'ending option 1', 'ending option 2', 'ending option 3']
            }
            question.setdefault('pairs', []).append(new_pair)
            refresh_pairs()

        def delete_pair(idx):
            if len(question.get('pairs', [])) > 1:
                pair = question['pairs'][idx]
                # Remove from answer mapping
                answer = question.get('answer', {})
                if pair.get('source') in answer:
                    del answer[pair['source']]
                del question['pairs'][idx]
                refresh_pairs()

        def add_target(pair_idx):
            if pair_idx < len(question.get('pairs', [])):
                question['pairs'][pair_idx].setdefault('targets', []).append('new cute ending')
                refresh_pairs()

        def delete_target(pair_idx, target_idx):
            if (pair_idx < len(question.get('pairs', [])) and 
                target_idx < len(question['pairs'][pair_idx].get('targets', [])) and
                len(question['pairs'][pair_idx]['targets']) > 2):
                del question['pairs'][pair_idx]['targets'][target_idx]
                refresh_pairs()

        def save_all():
            pairs = []
            answer = {}

            for source_var, target_vars, answer_var in self.match_phrases_pairs_data:
                source = source_var.get().strip()
                targets = [var.get() for var in target_vars if var.get().strip()]
                correct_answer = answer_var.get().strip()

                if source and targets:  # Only save if we have both source and targets
                    pairs.append({'source': source, 'targets': targets})
                    if correct_answer:
                        answer[source] = correct_answer

            question['pairs'] = pairs
            question['answer'] = answer
            messagebox.showinfo("Success! 💖", "All phrase matching pairs saved beautifully, darling!")

        refresh_pairs()

        # Main buttons
        btn_frame = tk.Frame(pairs_frame, bg=self.colors['white'])
        btn_frame.pack(fill=tk.X, pady=8)

        tk.Button(btn_frame, text="➕ Add New Matching Pair", command=add_pair,
                 bg=self.colors['button'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="💾 Save All Pairs", command=save_all,
                 bg=self.colors['accent'], fg='black', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)


def main():
    """Main function to run the cutest editor ever! 💖"""
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
    root.minsize(1000, 700)

    # Create the amazing app
    app = WifeyMOOCEditor(root)

    # Add some cute finishing touches
    root.protocol("WM_DELETE_WINDOW", lambda: (
        messagebox.showinfo("Goodbye! 💖", "Thanks for using Wifey MOOC Editor, babe! 💕") 
        if messagebox.askyesno("Leaving? 💔", "Are you sure you want to close the editor, sweetie?")
        else None,
        root.destroy() if messagebox.askyesno("Leaving? 💔", "Are you sure you want to close the editor, sweetie?") else None
    )[1])

    # Start the magical application!
    root.mainloop()

if __name__ == "__main__":
    print("💖 Starting the most adorable MOOC editor ever! 💖")
    print("✨ Made with love for all the girlies! ✨")
    main()
