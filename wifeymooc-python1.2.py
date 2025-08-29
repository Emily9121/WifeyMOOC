import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import json
import os
import subprocess
import platform
import random

# Constants
DEBUG = True # Print debug info for image tagging
ENABLE_SKIP_BUTTON = True
PADDING_X = 6
PADDING_Y = 3
TAG_START_X = 10
TAG_START_Y = 10
RESERVED_HEIGHT = 160 # Reserved space at bottom for buttons
FONT_QUESTION_LABEL = ("Arial", 14)
FONT_OPTION = ("Arial", 12)
FONT_TAG = ("Arial", 14, "bold")
FONT_FEEDBACK = ("Arial", 12)
CANVAS_MIN_WIDTH = 200
CANVAS_MIN_HEIGHT = 200

class WifeyMOOCApp:
    def __init__(self, root, question_file=None, progress_file=None):
        self.root = root
        self.root.title("Wifey MOOC")
        self.questions = []
        self.current_question = 0
        self.score = 0
        self.student_answers = {} # key: question index, value: student answer data
        self.progress_file = None
        self.current_question_file = None
        self.json_dir = None # Directory of the JSON file
        self.tag_positions_dict = {}
        self.tag_items = {} # For canvas tag items {tag_id: (rect_id, text_id)}
        self.drag_data = {"tag_id": None, "x": 0, "y": 0}
        self.last_focused_entry = None
        self.lesson_pdf_path = None # ✨ ADD THIS LINE ✨
        
        # NEW: Multi-question support
        self.current_multi_question_widgets = {}
        self.current_multi_question_vars = {}
        
        # Image tagging support
        self.image_tagging_alt_idx = 0
        
        self.create_menu()
        self.create_widgets()
        
        if progress_file:
            self.load_progress_from_file(progress_file)
        elif question_file:
            self.load_questions_from_file(question_file)
        else:
            self.display_welcome()

    # ✨ REPLACE the entire load_questions_from_file method with this ✨
    def load_questions_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both old format (list) and new format (dict)
            if isinstance(data, list):
                self.questions = data
            elif isinstance(data, dict):
                self.questions = data.get("questions", [])
            else:
                messagebox.showerror("Error", "Invalid JSON format! Must be an array or an object with a 'questions' key.")
                return

            self.current_question_file = file_path
            self.json_dir = os.path.dirname(file_path)
            self.display_question()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load questions:\n{e}")

    def load_progress_from_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            quiz_path = data.get('question_file')
            if not quiz_path or not os.path.exists(quiz_path):
                messagebox.showerror("Load Error", "Quiz file missing or not specified in progress file.")
                return

            with open(quiz_path, 'r', encoding='utf-8') as f_q:
                self.questions = json.load(f_q)

            self.current_question_file = quiz_path
            self.json_dir = os.path.dirname(quiz_path) # Store the directory of the JSON file
            self.current_question = data.get('current_question', 0)
            self.student_answers = data.get('student_answers', {})
            self.score = data.get('score', 0)
            self.tag_positions_dict = data.get("tag_positions_dict", {})
            self.progress_file = file_path
            self.display_question()
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load progress:\n{e}")

    def resolve_media_path(self, path):
        """Resolve the media path relative to the JSON file directory."""
        if self.json_dir and not os.path.isabs(path):
            return os.path.join(self.json_dir, path)
        return path

    def create_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load Questions", command=self.load_questions)
        filemenu.add_command(label="Save Progress", command=self.save_progress)
        filemenu.add_command(label="Load Progress", command=self.load_progress)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        self.container = tk.Frame(self.root)
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.question_label = tk.Label(
            self.container,
            text="",
            font=FONT_QUESTION_LABEL,
            wraplength=900,
            justify=tk.LEFT
        )
        self.question_label.pack(anchor=tk.W, pady=10)

        self.media_label = tk.Label(self.container)
        self.media_label.pack()

        options_holder = tk.Frame(self.container)
        options_holder.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.options_canvas = tk.Canvas(options_holder, highlightthickness=0)
        self.options_canvas.grid(row=0, column=0, sticky="nsew")

        self.options_scrollbar_v = tk.Scrollbar(options_holder, orient=tk.VERTICAL, command=self.options_canvas.yview)
        self.options_scrollbar_v.grid(row=0, column=1, sticky="ns")

        self.options_scrollbar_h = tk.Scrollbar(options_holder, orient=tk.HORIZONTAL, command=self.options_canvas.xview)
        self.options_scrollbar_h.grid(row=1, column=0, sticky="ew")

        options_holder.grid_rowconfigure(0, weight=1)
        options_holder.grid_columnconfigure(0, weight=1)

        self.options_canvas.configure(yscrollcommand=self.options_scrollbar_v.set, xscrollcommand=self.options_scrollbar_h.set)

        self.options_frame = tk.Frame(self.options_canvas)
        self.options_window = self.options_canvas.create_window((0, 0), window=self.options_frame, anchor="nw")

        self.options_frame.bind("<Configure>", self.update_options_scrollregion)
        self.options_canvas.bind("<Configure>", self.update_options_scrollregion)
        self._bind_options_canvas_mousewheel()

        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.feedback_label = tk.Label(
            self.button_frame,
            text="",
            fg="red",
            font=FONT_FEEDBACK
        )
        self.feedback_label.pack(side=tk.LEFT)

        # ✨ Creating our new hint button! ✨
        self.hint_button = tk.Button(
            self.button_frame,
            text="💡 Hint!",
            command=self.show_hint
        )
        # We don't pack it yet, we'll show it when there's a hint!
        # ✨ START of ADDED CODE ✨
        self.lesson_button = tk.Button(
            self.button_frame,
            text="📚 View Lesson",
            command=self.view_lesson_pdf
        )
        # ✨ END of ADDED CODE ✨

        self.submit_button = tk.Button(
            self.button_frame,
            text="Submit Answer",
            command=self.check_answer
        )
        self.submit_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.next_button = tk.Button(
            self.button_frame,
            text="Next Question",
            state=tk.DISABLED,
            command=self.next_question
        )
        self.next_button.pack(side=tk.LEFT, padx=10, pady=10)

        if ENABLE_SKIP_BUTTON:
            self.skip_button = tk.Button(
                self.button_frame,
                text="SKIP QUESTION (DEBUG)",
                fg="white",
                bg="red",
                command=self.skip_question
            )
            self.skip_button.pack(side=tk.LEFT, padx=10, pady=10)

        self.alt_image_button = tk.Button(
            self.button_frame,
            text="Alternative Version"
        )
        # Don't pack it initially - it will be packed when needed

    def update_options_scrollregion(self, event=None):
        self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all"))
        frame_h = self.options_frame.winfo_height()
        frame_w = self.options_frame.winfo_width()
        canvas_h = self.options_canvas.winfo_height()
        canvas_w = self.options_canvas.winfo_width()

        if frame_h > canvas_h:
            self.options_scrollbar_v.grid()
        else:
            self.options_scrollbar_v.grid_remove()

        if frame_w > canvas_w:
            self.options_scrollbar_h.grid()
        else:
            self.options_scrollbar_h.grid_remove()

    def reset_options_canvas(self):
        try:
            self.options_canvas.yview_moveto(0)
            self.options_canvas.xview_moveto(0)
            self.update_options_scrollregion()
        except Exception:
            pass

    def _bind_options_canvas_mousewheel(self):
        def on_mousewheel(event):
            if event.state & 0x1:
                self.options_canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            else:
                self.options_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        self.options_canvas.bind("<MouseWheel>", on_mousewheel)
        self.options_canvas.bind("<Button-4>", on_mousewheel)
        self.options_canvas.bind("<Button-5>", lambda e: self.options_canvas.yview_scroll(-1, "units"))

    def show_hint(self):
        """A cute function to show our hint in a messagebox! 💖"""
        if self.current_hint:
            messagebox.showinfo("💖 A Little Hint For You! 💖", self.current_hint)


    def clear_widgets(self):
        self.question_label.config(text="")
        self.media_label.config(image="")
        self.media_label.image = None
        self.media_label.config(cursor="")
        self.media_label.unbind("<Button-1>")
        self.feedback_label.config(text="", fg="red")
        
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # Clear multi-question data
        self.current_multi_question_widgets.clear()
        self.current_multi_question_vars.clear()
        
        self.submit_button.config(state=tk.DISABLED)
        self.next_button.config(state=tk.DISABLED)
        self.alt_image_button.pack_forget()  # Hide alternative button
        self.hint_button.pack_forget() # ✨ Make sure to hide it! ✨
        self.lesson_button.pack_forget() # ✨ ADD THIS LINE ✨
        self.reset_options_canvas()

    def display_welcome(self):
        self.clear_widgets()
        self.question_label.config(text="Welcome to Wifey MOOC! Load a question file to start.")

        btn = tk.Button(
            self.options_frame,
            text="Load Questions",
            font=(FONT_OPTION[0], 14, "bold"),
            command=self.load_questions
        )
        btn.pack(pady=20)

    def load_questions(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        self.load_questions_from_file(path)

    def save_progress(self):
        if not self.questions:
            messagebox.showwarning("Save Progress", "No quiz loaded.")
            return

        if not self.current_question_file:
            messagebox.showwarning("Save Progress", "No question file path stored.")
            return

        data = {
            "current_question": self.current_question,
            "student_answers": self.student_answers,
            "score": self.score,
            "question_file": self.current_question_file,
            "tag_positions_dict": self.tag_positions_dict,
        }

        save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not save_path:
            return

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Save Progress", "Progress saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save progress:\n{e}")

    def load_progress(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        self.load_progress_from_file(path)

    def add_media_buttons(self, media):
        if not media:
            return

        if "audio" in media:
            btn = tk.Button(
                self.options_frame,
                text="Play Audio",
                command=lambda: self.open_audio(self.resolve_media_path(media["audio"]))
            )
            btn.pack(pady=2)

        if "video" in media:
            btn = tk.Button(
                self.options_frame,
                text="Play Video",
                command=lambda: self.launch_file(self.resolve_media_path(media["video"]))
            )
            btn.pack(pady=2)

    # ✨ ADD THIS NEW METHOD inside the WifeyMOOCApp class ✨
    def view_lesson_pdf(self):
        """A super smart function to open our lesson PDF! 📚"""
        if self.lesson_pdf_path and os.path.exists(self.lesson_pdf_path):
            self.launch_file(self.lesson_pdf_path)
        else:
            messagebox.showwarning("Oopsie!", "The lesson PDF is missing, sweetie!")

    def display_question(self):
        self.clear_widgets()

        if not self.questions or self.current_question >= len(self.questions):
            self.activity_completed()
            return

        question_block = self.questions[self.current_question]
        # ✨ REPLACE the hint logic with this new block ✨
        # Handle Hint
        self.current_hint = question_block.get('hint', '')
        if self.current_hint:
            self.hint_button.pack(side=tk.LEFT, padx=10, pady=10)
        else:
            self.hint_button.pack_forget()

        # Handle Lesson PDF
        lesson_info = question_block.get("lesson")
        if lesson_info and "pdf" in lesson_info and lesson_info["pdf"]:
            self.lesson_pdf_path = self.resolve_media_path(lesson_info["pdf"])
            if os.path.exists(self.lesson_pdf_path):
                self.lesson_button.pack(side=tk.LEFT, padx=10, pady=10)
            else:
                self.lesson_button.pack_forget()
        else:
            self.lesson_pdf_path = None
            self.lesson_button.pack_forget()
        # ✨ END of REPLACEMENT ✨

        qtype = question_block.get('type')

        # NEW: Handle multi_questions type
        if qtype == "multi_questions":
            self._display_multi_questions(question_block)
            return

        # Handle regular single questions
        question = question_block
        self.question_label.config(text=f"Q{self.current_question + 1}: {question.get('question', '')}")
        self.feedback_label.config(text="")
        self.submit_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)

        media = question.get('media')
        if media and "image" in media and qtype != "image_tagging":
            self.display_media_image(self.resolve_media_path(media["image"]))
        else:
            self.media_label.config(image="")
            self.media_label.image = None
            self.media_label.config(cursor="")
            self.media_label.unbind("<Button-1>")

        if qtype == "image_tagging":
            self._display_image_tagging(question)
        else:
            handler = getattr(self, f'_display_{qtype}', None)
            if handler:
                handler(question)
            else:
                self.feedback_label.config(text=f"Unsupported question type: {qtype}", fg='red')

        self.root.focus()

    # NEW: Multi-questions display method
    def _display_multi_questions(self, question_block):
        """Display a block containing multiple sub-questions"""
        self.question_label.config(text=f"Question Block {self.current_question + 1}: Multiple Parts")
        self.feedback_label.config(text="")
        self.submit_button.config(state=tk.NORMAL)
        self.next_button.config(state=tk.DISABLED)

        # Handle block-level media
        block_media = question_block.get('media')
        if block_media:
            self.add_media_buttons(block_media)

        # Display each sub-question in a labeled frame
        sub_questions = question_block.get('questions', [])
        for i, sub_question in enumerate(sub_questions):
            sub_key = f"{self.current_question}-{i}"
            
            # Create a frame for this sub-question
            sub_frame = tk.LabelFrame(self.options_frame, text=f"Part {i + 1}", font=("Arial", 12, "bold"))
            sub_frame.pack(fill=tk.X, pady=5, padx=5)

            # Add question text
            q_text = sub_question.get('question', '')
            if q_text:
                q_label = tk.Label(sub_frame, text=q_text, wraplength=800, justify=tk.LEFT)
                q_label.pack(anchor=tk.W, pady=5)

            # Store the sub-question widgets and vars
            self.current_multi_question_widgets[sub_key] = sub_frame
            self.current_multi_question_vars[sub_key] = {}

            # Display the sub-question content
            sub_qtype = sub_question.get('type')
            if sub_qtype == 'mcq_single':
                self._display_mcq_single_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'mcq_multiple':
                self._display_mcq_multiple_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'word_fill':
                self._display_word_fill_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'list_pick':
                self._display_list_pick_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'sequence_audio':
                self._display_sequence_audio_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'match_sentence':
                self._display_match_sentence_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'match_phrases':
                self._display_match_phrases_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'fill_blanks_dropdown':
                self._display_fill_blanks_dropdown_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'order_phrase':
                self._display_order_phrase_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'categorization_multiple':
                self._display_categorization_multiple_in_frame(sub_question, sub_frame, sub_key)
            elif sub_qtype == 'image_tagging':
                self._display_image_tagging_in_frame(sub_question, sub_frame, sub_key)
            else:
                # Fallback for other question types
                self._display_generic_in_frame(sub_question, sub_frame, sub_key)

    # NEW: MCQ methods for multi-questions (in frames)
    def _display_mcq_single_in_frame(self, question, parent_frame, key):
        var = tk.IntVar(value=-1)
        self.current_multi_question_vars[key]['mcq_var'] = var

        for idx, opt in enumerate(question.get('options', [])):
            if isinstance(opt, dict):
                self._create_image_text_option(opt, idx, parent_frame, var, "radio")
            else:
                rb = tk.Radiobutton(parent_frame, text=opt, variable=var, value=idx, font=FONT_OPTION)
                rb.pack(anchor=tk.W)

    def _display_mcq_multiple_in_frame(self, question, parent_frame, key):
        vars_list = []
        for idx, opt in enumerate(question.get('options', [])):
            var = tk.IntVar(value=0)
            vars_list.append(var)
            
            if isinstance(opt, dict):
                self._create_image_text_option(opt, idx, parent_frame, var, "check")
            else:
                cb = tk.Checkbutton(parent_frame, text=opt, variable=var, font=FONT_OPTION)
                cb.pack(anchor=tk.W)
        
        self.current_multi_question_vars[key]['mcq_vars'] = vars_list

    def _display_word_fill_in_frame(self, question, parent_frame, key):
        entries = []
        parts = question.get('sentence_parts', [])
        answers = question.get('answers', [])
        
        # Simplified version for multi-questions
        for i, answer in enumerate(answers):
            if i < len(parts):
                # Add the part text
                part_label = tk.Label(parent_frame, text=parts[i], wraplength=700, justify=tk.LEFT)
                part_label.pack(anchor=tk.W, pady=2)
            
            # Add entry field
            entry = tk.Entry(parent_frame, font=FONT_OPTION, width=30)
            entry.pack(anchor=tk.W, pady=2)
            entries.append(entry)
        
        # Add final part if exists
        if len(parts) > len(answers):
            final_label = tk.Label(parent_frame, text=parts[-1], wraplength=700, justify=tk.LEFT)
            final_label.pack(anchor=tk.W, pady=2)
        
        self.current_multi_question_vars[key]['entries'] = entries

    def _display_list_pick_in_frame(self, question, parent_frame, key):
        listbox = tk.Listbox(parent_frame, selectmode=tk.MULTIPLE, height=5, font=FONT_OPTION)
        for opt in question.get('options', []):
            listbox.insert(tk.END, opt)
        listbox.pack(fill=tk.X, pady=5)
        self.current_multi_question_vars[key]['listbox'] = listbox

    def _display_sequence_audio_in_frame(self, question, parent_frame, key):
        entries = []
        options = question.get('audio_options', [])
        
        for i, option in enumerate(options):
            row_frame = tk.Frame(parent_frame)
            row_frame.pack(anchor=tk.W, pady=2)
            
            option_text = option.get('option', f'Option {i+1}') if isinstance(option, dict) else str(option)
            tk.Label(row_frame, text=option_text, font=FONT_OPTION).pack(side=tk.LEFT)
            
            entry = tk.Entry(row_frame, width=5)
            entry.pack(side=tk.LEFT, padx=5)
            entries.append(entry)
        
        self.current_multi_question_vars[key]['seq_entries'] = entries

    def _display_match_sentence_in_frame(self, question, parent_frame, key):
        match_vars = {}
        pairs = question.get('pairs', [])
        
        # Create grid layout
        grid_frame = tk.Frame(parent_frame)
        grid_frame.pack(fill=tk.X, pady=5)
        
        for idx, pair in enumerate(pairs):
            row = idx // 2  # 2 columns
            col = idx % 2
            
            pair_frame = tk.Frame(grid_frame, relief=tk.RIDGE, borderwidth=1, padx=5, pady=5)
            pair_frame.grid(row=row, column=col, padx=5, pady=5, sticky=tk.W)
            
            # Handle image
            if 'image_path' in pair:
                try:
                    img = Image.open(self.resolve_media_path(pair['image_path']))
                    img = img.resize((100, 100))
                    tkimg = ImageTk.PhotoImage(img)
                    img_label = tk.Label(pair_frame, image=tkimg)
                    img_label.image = tkimg  # Keep reference
                    img_label.pack()
                except Exception:
                    tk.Label(pair_frame, text='[Image not found]', fg='red').pack()
            
            # Create dropdown with all sentence options
            var = tk.StringVar()
            sentences = [p['sentence'] for p in pairs]
            dropdown = ttk.Combobox(pair_frame, textvariable=var, values=sentences, state='readonly', width=20)
            dropdown.pack(pady=5)
            
            match_vars[pair['image_path']] = var
        
        self.current_multi_question_vars[key]['match_vars'] = match_vars

    def _display_match_phrases_in_frame(self, question, parent_frame, key):
        """FIXED: Added missing match_phrases implementation for multi-questions"""
        match_vars = {}
        pairs = question.get('pairs', [])
        
        for pair in pairs:
            pair_frame = tk.Frame(parent_frame)
            pair_frame.pack(anchor=tk.W, pady=3, fill=tk.X)
            
            # Source phrase
            source_label = tk.Label(pair_frame, text=pair.get('source', ''), font=FONT_OPTION)
            source_label.pack(side=tk.LEFT)
            
            # Arrow
            tk.Label(pair_frame, text=" → ", font=FONT_OPTION).pack(side=tk.LEFT)
            
            # Target dropdown
            var = tk.StringVar()
            targets = pair.get('targets', [])
            var.set(targets[0] if targets else '')
            combo = ttk.Combobox(pair_frame, textvariable=var, values=targets, state='readonly', width=25)
            combo.pack(side=tk.LEFT, padx=5)
            
            match_vars[pair.get('source', '')] = var
        
        self.current_multi_question_vars[key]['match_vars'] = match_vars

    def _display_fill_blanks_dropdown_in_frame(self, question, parent_frame, key):
        fill_vars = []
        parts = question.get('sentence_parts', [])
        blanks = question.get('options_for_blanks', [])
        
        # Create sentence with dropdowns
        sentence_frame = tk.Frame(parent_frame)
        sentence_frame.pack(fill=tk.X, pady=5)
        
        row_frame = tk.Frame(sentence_frame)
        row_frame.pack(anchor=tk.W)
        
        for i, blank_options in enumerate(blanks):
            # Add part before blank
            if i < len(parts):
                part_text = parts[i].replace('\n', ' ')  # Simplify for multi-questions
                if part_text.strip():
                    tk.Label(row_frame, text=part_text, font=FONT_OPTION).pack(side=tk.LEFT)
            
            # Add dropdown
            var = tk.StringVar()
            var.set(blank_options[0] if blank_options else '')
            dropdown = ttk.Combobox(row_frame, textvariable=var, values=blank_options, state='readonly', width=15)
            dropdown.pack(side=tk.LEFT, padx=2)
            fill_vars.append(var)
        
        # Add final part
        if len(parts) > len(blanks):
            final_text = parts[-1].replace('\n', ' ')
            if final_text.strip():
                tk.Label(row_frame, text=final_text, font=FONT_OPTION).pack(side=tk.LEFT)
        
        self.current_multi_question_vars[key]['fill_vars'] = fill_vars

    def _display_order_phrase_in_frame(self, question, parent_frame, key):
        words = list(question.get('phrase_shuffled', []))
        word_vars = [tk.StringVar(value=w) for w in words]
        
        # Create word ordering interface
        words_frame = tk.Frame(parent_frame)
        words_frame.pack(fill=tk.X, pady=5)
        
        word_labels = []
        for i, word_var in enumerate(word_vars):
            word_frame = tk.Frame(words_frame)
            word_frame.pack(fill=tk.X, pady=2)
            
            # Word label
            label = tk.Label(word_frame, text=word_var.get(), relief=tk.RAISED, width=30)
            label.pack(side=tk.LEFT, padx=5)
            word_labels.append(label)
            
            # Move buttons
            if i > 0:
                up_btn = tk.Button(word_frame, text="↑", width=3,
                                 command=lambda idx=i: self._move_word_in_frame(idx, -1, word_labels, key))
                up_btn.pack(side=tk.LEFT, padx=2)
            
            if i < len(word_vars) - 1:
                down_btn = tk.Button(word_frame, text="↓", width=3,
                                   command=lambda idx=i: self._move_word_in_frame(idx, 1, word_labels, key))
                down_btn.pack(side=tk.LEFT, padx=2)
        
        self.current_multi_question_vars[key]['word_labels'] = word_labels

    def _move_word_in_frame(self, index, direction, word_labels, key):
        """Move word up or down in the order"""
        new_index = index + direction
        if 0 <= new_index < len(word_labels):
            # Swap the labels
            text1 = word_labels[index]['text']
            text2 = word_labels[new_index]['text']
            word_labels[index].config(text=text2)
            word_labels[new_index].config(text=text1)

    def _display_categorization_multiple_in_frame(self, question, parent_frame, key):
        cat_vars = {}
        stimuli = question.get('stimuli', [])
        categories = question.get('categories', [])
        
        # Create grid for stimuli
        grid_frame = tk.Frame(parent_frame)
        grid_frame.pack(fill=tk.X, pady=5)
        
        max_cols = 3  # Simplified for multi-questions
        for idx, stimulus in enumerate(stimuli):
            row = idx // max_cols
            col = idx % max_cols
            
            stim_frame = tk.Frame(grid_frame, relief=tk.GROOVE, borderwidth=1, padx=5, pady=5)
            stim_frame.grid(row=row, column=col, padx=3, pady=3)
            
            # Add stimulus content
            obj_id = None
            if 'text' in stimulus:
                obj_id = stimulus['text']
                tk.Label(stim_frame, text=obj_id, font=FONT_OPTION, wraplength=100).pack()
            elif 'image' in stimulus:
                obj_id = os.path.basename(stimulus['image'])
                try:
                    img = Image.open(self.resolve_media_path(stimulus['image']))
                    img = img.resize((60, 60))
                    tkimg = ImageTk.PhotoImage(img)
                    img_label = tk.Label(stim_frame, image=tkimg)
                    img_label.image = tkimg
                    img_label.pack()
                except Exception:
                    tk.Label(stim_frame, text='[Image not found]', fg='red').pack()
            else:
                obj_id = f'obj_{idx}'
            
            # Add category dropdown
            var = tk.StringVar()
            var.set(categories[0] if categories else '')
            dropdown = ttk.Combobox(stim_frame, textvariable=var, values=categories, state='readonly', width=12)
            dropdown.pack(pady=2)
            
            cat_vars[obj_id] = var
        
        self.current_multi_question_vars[key]['cat_vars'] = cat_vars

    def _display_image_tagging_in_frame(self, question, parent_frame, key):
        """FIXED: Full image tagging implementation for multi-questions with 1:1 scale"""
        # Get all alternatives including main question
        alternatives = [question] + question.get("alternatives", [])
        
        # Initialize alternative index for this specific multi-question
        if f'{key}_alt_idx' not in self.current_multi_question_vars:
            self.current_multi_question_vars[f'{key}_alt_idx'] = 0
            
        alt_idx = self.current_multi_question_vars[f'{key}_alt_idx']
        
        # Ensure valid index
        if alt_idx >= len(alternatives):
            alt_idx = 0
            self.current_multi_question_vars[f'{key}_alt_idx'] = alt_idx

        # Get current alternative question
        altq = alternatives[alt_idx]
        
        # Set up alternative button if there are multiple alternatives
        if len(alternatives) > 1:
            alt_btn = tk.Button(parent_frame, text=f"Alternative {alt_idx + 1}",
                               command=lambda: self._switch_multi_image_alternative(key, alternatives, parent_frame, question))
            alt_btn.pack(pady=5)

        # Get media and tags from current alternative
        media = altq.get('media', {})
        img_path = media.get("image")
        tags = altq.get("tags", [])

        if not img_path:
            tk.Label(parent_frame, text="Image path missing!", fg='red').pack()
            return

        try:
            img = Image.open(self.resolve_media_path(img_path))
            # FIXED: USE ORIGINAL SIZE - NO SCALING FOR IMAGE TAGGING!
            canvas_w, canvas_h = img.size
            tag_bg_img = ImageTk.PhotoImage(img)
            
            if DEBUG:
                print(f"[DEBUG] Image tagging multi-question: Using original size {canvas_w}x{canvas_h}")
                
        except Exception as e:
            tk.Label(parent_frame, text=f"Failed to load image: {e}", fg='red').pack()
            return

        # Create canvas container with scrollbars for large images
        canvas_frame = tk.Frame(parent_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add scrollbars for large images
        hbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        vbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        
        # Create canvas with scrolling support
        canvas = tk.Canvas(canvas_frame, 
                          width=min(canvas_w, 800),  # Max display width
                          height=min(canvas_h, 600),  # Max display height
                          background='white',
                          xscrollcommand=hbar.set,
                          yscrollcommand=vbar.set)
        
        # Configure scrollbars
        hbar.config(command=canvas.xview)
        vbar.config(command=canvas.yview)
        canvas.config(scrollregion=(0, 0, canvas_w, canvas_h))
        
        # Pack scrollbars only if needed
        if canvas_w > 800:
            hbar.pack(side=tk.BOTTOM, fill=tk.X)
        if canvas_h > 600:
            vbar.pack(side=tk.RIGHT, fill=tk.Y)
            
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Display background image at original size
        canvas.create_image(0, 0, anchor=tk.NW, image=tag_bg_img)
        
        # Keep reference to prevent garbage collection
        canvas.image = tag_bg_img

        # Initialize tag positions for this multi-question
        tag_positions_key = f"{key}_{alt_idx}"
        if tag_positions_key not in self.tag_positions_dict:
            self.tag_positions_dict[tag_positions_key] = {}
        
        curr_tag_pos = self.tag_positions_dict[tag_positions_key]
        tag_items = {}

        # Create draggable tags
        for i, tag in enumerate(tags):
            tag_id = tag.get('id')
            label = tag.get('label', '')

            # Get saved position or use default
            if tag_id in curr_tag_pos:
                x0, y0 = curr_tag_pos[tag_id]
            else:
                x0 = TAG_START_X
                y0 = TAG_START_Y + i * 30  # Smaller spacing for multi-questions
                curr_tag_pos[tag_id] = [x0, y0]

            # Calculate text size
            temp_text_id = canvas.create_text(0, 0, text=label, font=FONT_TAG, anchor=tk.NW)
            bbox = canvas.bbox(temp_text_id)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            canvas.delete(temp_text_id)

            # Create tag rectangle and text
            rect_id = canvas.create_rectangle(
                x0, y0, x0 + text_w + 2 * PADDING_X, y0 + text_h + 2 * PADDING_Y,
                fill="black", outline="yellow", tags=(tag_id, "draggable")
            )

            text_id = canvas.create_text(
                x0 + PADDING_X, y0 + PADDING_Y, text=label,
                font=FONT_TAG, fill="yellow", anchor=tk.NW, tags=(tag_id, "draggable")
            )

            tag_items[tag_id] = (rect_id, text_id)

        # Store canvas and tag items for this multi-question
        self.current_multi_question_vars[key]['canvas'] = canvas
        self.current_multi_question_vars[key]['tag_items'] = tag_items
        self.current_multi_question_vars[key]['tag_positions'] = curr_tag_pos

        # Tag dragging functionality
        drag_data = {"tag_id": None, "x": 0, "y": 0}
        
        def start_drag(event):
            canvas_x = canvas.canvasx(event.x)
            canvas_y = canvas.canvasy(event.y)
            item = canvas.find_closest(canvas_x, canvas_y)[0]
            
            tag_id = None
            for tid, (rect_id, text_id) in tag_items.items():
                if item == rect_id or item == text_id:
                    tag_id = tid
                    break

            if tag_id:
                drag_data["tag_id"] = tag_id
                drag_data["x"] = canvas_x
                drag_data["y"] = canvas_y

        def drag(event):
            if not drag_data["tag_id"]:
                return

            canvas_x = canvas.canvasx(event.x)
            canvas_y = canvas.canvasy(event.y)
            dx = canvas_x - drag_data["x"]
            dy = canvas_y - drag_data["y"]

            tag_id = drag_data["tag_id"]
            if tag_id in tag_items:
                rect_id, text_id = tag_items[tag_id]
                canvas.move(rect_id, dx, dy)
                canvas.move(text_id, dx, dy)

            drag_data["x"] = canvas_x
            drag_data["y"] = canvas_y

        def end_drag(event):
            if drag_data["tag_id"]:
                tag_id = drag_data["tag_id"]
                if tag_id in tag_items:
                    rect_id, text_id = tag_items[tag_id]
                    bbox = canvas.bbox(rect_id)
                    if bbox:
                        x, y = bbox[0], bbox[1]
                        curr_tag_pos[tag_id] = [x, y]
                        
                        if DEBUG:
                            print(f"[DEBUG] Multi-question {key}: Tag '{tag_id}' moved to ({x}, {y})")

            drag_data["tag_id"] = None

        # Bind drag events
        canvas.bind("<Button-1>", start_drag)
        canvas.bind("<B1-Motion>", drag)
        canvas.bind("<ButtonRelease-1>", end_drag)

    def _switch_multi_image_alternative(self, key, alternatives, parent_frame, question):
        """Switch to next alternative for multi-question image tagging"""
        current_alt = self.current_multi_question_vars[f'{key}_alt_idx']
        next_alt = (current_alt + 1) % len(alternatives)
        self.current_multi_question_vars[f'{key}_alt_idx'] = next_alt
        
        if DEBUG:
            print(f"[DEBUG] Multi-question {key}: Switching from alternative {current_alt} to {next_alt}")
        
        # Clear and redisplay
        for widget in parent_frame.winfo_children():
            widget.destroy()
            
        # Add question text back
        q_text = question.get('question', '')
        if q_text:
            q_label = tk.Label(parent_frame, text=q_text, wraplength=800, justify=tk.LEFT)
            q_label.pack(anchor=tk.W, pady=5)
            
        # Redisplay with new alternative
        self._display_image_tagging_in_frame(question, parent_frame, key)

    def _display_generic_in_frame(self, question, parent_frame, key):
        tk.Label(parent_frame, text=f"Question type '{question.get('type')}' not supported in multi-questions",
                fg="red").pack()

    # NEW: MCQ single with support for image+text options
    def _display_mcq_single(self, question):
        self.add_media_buttons(question.get('media'))
        self.mcq_var = tk.IntVar(value=-1)

        for idx, opt in enumerate(question.get('options', [])):
            # NEW: Support both old string format and new object format
            if isinstance(opt, dict):
                # New format: {"image": "path", "text": "label"}
                self._create_image_text_option(opt, idx, self.options_frame, self.mcq_var, "radio")
            else:
                # Old format: just text
                rb = tk.Radiobutton(self.options_frame, text=opt, variable=self.mcq_var, value=idx, font=FONT_OPTION)
                rb.pack(anchor=tk.W)

    # NEW: MCQ multiple with support for image+text options
    def _display_mcq_multiple(self, question):
        self.add_media_buttons(question.get('media'))
        self.mcq_vars = []

        for idx, opt in enumerate(question.get('options', [])):
            var = tk.IntVar(value=0)
            # NEW: Support both old string format and new object format
            if isinstance(opt, dict):
                # New format: {"image": "path", "text": "label"}
                cb = self._create_image_text_option(opt, idx, self.options_frame, var, "check")
            else:
                # Old format: just text
                cb = tk.Checkbutton(self.options_frame, text=opt, variable=var, font=FONT_OPTION)
                cb.pack(anchor=tk.W)
            self.mcq_vars.append(var)

    # NEW: Helper method to create image+text options
    def _create_image_text_option(self, opt_dict, idx, parent, variable, button_type):
        """Create a button with both image and text"""
        frame = tk.Frame(parent)
        frame.pack(anchor=tk.W, pady=2)

        # Create the appropriate button type
        if button_type == "radio":
            button = tk.Radiobutton(frame, variable=variable, value=idx, font=FONT_OPTION)
        else:  # checkbox
            button = tk.Checkbutton(frame, variable=variable, font=FONT_OPTION)

        # Add image if present
        if "image" in opt_dict and opt_dict["image"]:
            try:
                img_path = self.resolve_media_path(opt_dict["image"])
                img = Image.open(img_path)
                img = img.resize((64, 64), Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
                photo = ImageTk.PhotoImage(img)
                img_label = tk.Label(frame, image=photo)
                img_label.image = photo  # Keep a reference
                img_label.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                # Fallback if image fails to load
                tk.Label(frame, text="[Image]", fg="gray").pack(side=tk.LEFT, padx=5)

        # Add text
        if "text" in opt_dict and opt_dict["text"]:
            button.config(text=opt_dict["text"])

        button.pack(side=tk.LEFT, padx=5)
        return button

    def _display_word_fill(self, question):
        self.add_media_buttons(question.get('media'))

        # Accent buttons
        accent_rows = [
            ['é', 'è', 'ê', 'ë', 'à', 'â', 'î', 'ï', 'ô', 'û', 'ù', 'ç', 'œ', 'æ'],
            ['É', 'È', 'Ê', 'Ë', 'À', 'Â', 'Î', 'Ï', 'Ô', 'Û', 'Ù', 'Ç', 'Œ', 'Æ']
        ]

        accent_frame = tk.Frame(self.options_frame)
        accent_frame.pack(anchor=tk.W, pady=2)

        self.last_focused_entry = None

        def insert_accent(ch):
            if self.last_focused_entry:
                self.last_focused_entry.insert(tk.INSERT, ch)

        for row in accent_rows:
            rframe = tk.Frame(accent_frame)
            rframe.pack(anchor=tk.W)
            for ch in row:
                btn = tk.Button(rframe, text=ch, width=2, font=FONT_OPTION, command=lambda c=ch: insert_accent(c))
                btn.pack(side=tk.LEFT, padx=1)

        self.fill_words_entries = []
        parts = question.get('sentence_parts', [])
        answers = question.get('answers', [])

        if parts and isinstance(answers, list) and len(parts) >= len(answers):
            for i in range(len(answers)):
                for line in parts[i].split('\n'):
                    pf = tk.Frame(self.options_frame)
                    pf.pack(anchor=tk.W, fill=tk.X)
                    lbl = tk.Label(pf, text=line, font=(FONT_OPTION[0], 14), wraplength=850, justify=tk.LEFT)
                    lbl.pack(anchor=tk.W)

                ef = tk.Frame(self.options_frame)
                ef.pack(anchor=tk.W, fill=tk.X)
                ent = tk.Entry(ef, font=(FONT_OPTION[0], 14), width=30)
                ent.pack(anchor=tk.W)
                ent.bind("<FocusIn>", lambda e, ent=ent: setattr(self, 'last_focused_entry', ent))
                self.fill_words_entries.append(ent)

            for line in parts[-1].split('\n'):
                lf = tk.Frame(self.options_frame)
                lf.pack(anchor=tk.W, fill=tk.X)
                lbl = tk.Label(lf, text=line, font=(FONT_OPTION[0], 14), wraplength=850, justify=tk.LEFT)
                lbl.pack(anchor=tk.W)
        else:
            self.entry = tk.Entry(self.options_frame, font=FONT_OPTION, width=40)
            self.entry.pack()
            self.entry.bind("<FocusIn>", lambda e: setattr(self, 'last_focused_entry', self.entry))

    def _display_list_pick(self, question):
        self.add_media_buttons(question.get('media'))
        self.listbox = tk.Listbox(self.options_frame, selectmode=tk.MULTIPLE, height=5, font=FONT_OPTION)
        for opt in question.get('options', []):
            self.listbox.insert(tk.END, opt)
        self.listbox.pack()

    def _display_match_sentence(self, question):
        self.add_media_buttons(question.get('media'))
        self.match_vars = {}

        pairs = question.get('pairs', [])
        randomized_opts = [p['sentence'] for p in pairs]
        randomized_opts = random.sample(randomized_opts, len(randomized_opts))

        max_cols = 4
        for idx, pair in enumerate(pairs):
            r = idx // max_cols
            c = idx % max_cols

            frm = tk.Frame(self.options_frame, relief=tk.RIDGE, borderwidth=1, padx=5, pady=5)
            frm.grid(row=r, column=c, padx=10, pady=10, sticky=tk.N)

            try:
                img = Image.open(self.resolve_media_path(pair['image_path']))
                img = img.resize((150, 150))
                tkimg = ImageTk.PhotoImage(img)
                lbl = tk.Label(frm, image=tkimg)
                lbl.image = tkimg
                lbl.pack()
                lbl.bind('<Button-1>', lambda e, p=self.resolve_media_path(pair['image_path']): self.show_full_image(p))
            except Exception:
                tk.Label(frm, text='[Image not found]', fg='red').pack()

            var = tk.StringVar()
            var.set(randomized_opts[0] if randomized_opts else '')
            dropdown = ttk.Combobox(frm, textvariable=var, values=randomized_opts, state='readonly', width=30)
            dropdown.pack(pady=(5, 0))

            self.match_vars[pair['image_path']] = var

    def _display_categorization(self, question):
        self.add_media_buttons(question.get('media'))

        stim = question.get('stimulus')
        if stim:
            if 'image' in stim:
                try:
                    img = Image.open(self.resolve_media_path(stim['image']))
                    img = img.resize((120, 120))
                    tkimg = ImageTk.PhotoImage(img)
                    self.media_label.config(image=tkimg)
                    self.media_label.image = tkimg
                    self.media_label.bind('<Button-1>', lambda e, p=self.resolve_media_path(stim['image']): self.show_full_image(p))
                except Exception:
                    self.feedback_label.config(text=f"Stimulus image not found: {stim['image']}", fg='red')
            elif 'text' in stim:
                tk.Label(self.options_frame, text=stim['text'], font=("Arial", 16)).pack()

        self.categ_var = tk.StringVar()
        categories = question.get('categories', [''])
        self.categ_var.set(categories[0] if categories else '')
        tk.OptionMenu(self.options_frame, self.categ_var, *categories).pack()

    def _display_categorization_multiple(self, question):
        self.add_media_buttons(question.get('media'))
        self.cat_vars = {}

        grid_frame = tk.Frame(self.options_frame)
        grid_frame.pack(anchor=tk.W, pady=5)

        max_cols = question.get("max_columns", 6)
        stimuli = question.get('stimuli', [])
        n_stim = len(stimuli)
        n_rows = (n_stim + max_cols - 1) // max_cols if max_cols else n_stim

        for idx, stim in enumerate(stimuli):
            r = idx % n_rows
            c = idx // n_rows

            frm = tk.Frame(grid_frame, relief=tk.GROOVE, borderwidth=1, padx=8, pady=8)
            frm.grid(row=r, column=c, padx=5, pady=5, sticky=tk.N)

            obj_id = None
            if 'text' in stim:
                obj_id = stim['text']
                tk.Label(frm, text=obj_id, font=FONT_OPTION).pack()
            elif 'image' in stim:
                obj_id = os.path.basename(stim['image'])
                try:
                    img = Image.open(self.resolve_media_path(stim['image']))
                    img = img.resize((100, 100))
                    tkimg = ImageTk.PhotoImage(img)
                    lbl = tk.Label(frm, image=tkimg)
                    lbl.image = tkimg
                    lbl.pack()
                    lbl.bind('<Button-1>', lambda e, p=self.resolve_media_path(stim['image']): self.show_full_image(p))
                except Exception:
                    tk.Label(frm, text=f"Image not found: {stim['image']}", fg='red').pack()
            else:
                obj_id = f'obj_{idx}'

            var = tk.StringVar()
            categories = question.get('categories', [''])
            var.set(categories[0] if categories else '')
            tk.OptionMenu(frm, var, *categories).pack()

            self.cat_vars[obj_id] = var

    def _display_sequence_audio(self, question):
        self.add_media_buttons(question.get('media'))
        self.seq_entries = []

        options = question.get('audio_options', [])
        for option in options:
            row_frame = tk.Frame(self.options_frame)
            row_frame.pack(anchor=tk.W, pady=2)

            tk.Label(row_frame, text=option.get('option', ''), font=FONT_OPTION).pack(side=tk.LEFT)
            ent = tk.Entry(row_frame, width=3)
            ent.pack(side=tk.LEFT, padx=5)
            self.seq_entries.append(ent)

    def _display_order_phrase(self, question):
        self.words = list(question.get('phrase_shuffled', []))
        self.word_vars = [tk.StringVar(value=w) for w in self.words]
        self.render_order_phrase_widgets()
        self.add_media_buttons(question.get('media'))

    def render_order_phrase_widgets(self):
        self.word_buttons = []
        for i, word_var in enumerate(self.word_vars):
            frm = tk.Frame(self.options_frame)
            frm.pack(anchor=tk.W, pady=2)

            lbl = tk.Label(frm, text=word_var.get(), font=FONT_OPTION, relief=tk.RAISED, width=40)
            lbl.pack(side=tk.LEFT)

            if i > 0:
                up_btn = tk.Button(frm, text="↑", command=lambda idx=i: self.move_word(idx, -1))
                up_btn.pack(side=tk.LEFT, padx=5)

            if i < len(self.word_vars) - 1:
                down_btn = tk.Button(frm, text="↓", command=lambda idx=i: self.move_word(idx, 1))
                down_btn.pack(side=tk.LEFT)

            self.word_buttons.append(lbl)

    def move_word(self, index, direction):
        new_index = index + direction
        if 0 <= new_index < len(self.word_vars):
            # Swap values
            temp = self.word_vars[index].get()
            self.word_vars[index].set(self.word_vars[new_index].get())
            self.word_vars[new_index].set(temp)
            # Update display
            self.word_buttons[index].config(text=self.word_vars[index].get())
            self.word_buttons[new_index].config(text=self.word_vars[new_index].get())

    def _display_fill_blanks_dropdown(self, question):
        self.add_media_buttons(question.get('media'))
        self.fill_vars = []

        parts = question.get('sentence_parts', [])
        blanks = question.get('options_for_blanks', [])
        n_blanks = len(blanks)

        sentence_frame = tk.Frame(self.options_frame)
        sentence_frame.pack(anchor=tk.W, fill=tk.X, pady=10)

        tokens = []
        for i in range(n_blanks):
            tokens.append(parts[i])
            tokens.append(('dropdown', blanks[i]))
        tokens.append(parts[-1])

        current_row = tk.Frame(sentence_frame)
        current_row.pack(anchor=tk.W, fill=tk.X)

        for token in tokens:
            if isinstance(token, str):
                lines = token.split('\n')
                for idx, line in enumerate(lines):
                    if line:
                        lbl = tk.Label(current_row, text=line, font=(FONT_OPTION[0], 14), anchor=tk.W, justify=tk.LEFT)
                        lbl.pack(side=tk.LEFT)
                    if idx < len(lines) - 1:
                        current_row = tk.Frame(sentence_frame)
                        current_row.pack(anchor=tk.W, fill=tk.X)
            elif isinstance(token, tuple) and token[0] == 'dropdown':
                options = token[1]
                max_len = max(len(str(opt)) for opt in options) if options else 10
                var = tk.StringVar()
                var.set(options[0] if options else '')
                cmb = ttk.Combobox(current_row, textvariable=var, values=options, state='readonly', width=max_len + 2)
                cmb.pack(side=tk.LEFT, padx=5)
                self.fill_vars.append(var)

    def _display_match_phrases(self, question):
        self.add_media_buttons(question.get('media'))
        self.match_vars = {}

        for pair in question.get('pairs', []):
            frm = tk.Frame(self.options_frame)
            frm.pack(anchor=tk.W, pady=5, fill=tk.X)

            tk.Label(frm, text=pair.get('source', ''), font=FONT_OPTION).pack(side=tk.LEFT)

            var = tk.StringVar()
            targets = pair.get('targets', [])
            var.set(targets[0] if targets else '')
            combo = ttk.Combobox(frm, textvariable=var, values=targets, state='readonly', width=30)
            combo.pack(side=tk.LEFT, padx=10)

            self.match_vars[pair.get('source', '')] = var

    def _display_image_tagging(self, question, alt_idx=None):
        """FIXED: Standalone image tagging with proper alternative switching"""
        # Get all alternatives including main question
        alternatives = [question] + question.get("alternatives", [])
        
        # Set or update alternative index
        if alt_idx is not None:
            self.image_tagging_alt_idx = alt_idx
        elif not hasattr(self, "image_tagging_alt_idx"):
            self.image_tagging_alt_idx = 0
            
        # Ensure valid index
        if self.image_tagging_alt_idx >= len(alternatives):
            self.image_tagging_alt_idx = 0

        # Get current alternative question
        altq = alternatives[self.image_tagging_alt_idx]
        
        # Set up alternative button labels
        labels = [
            question.get("button_label", "Alternative Version")
        ] + [
            alt.get("button_label", f"Alternative {i+1}") for i, alt in enumerate(question.get("alternatives", []))
        ]

        # FIXED: Show alternative button if there are multiple alternatives
        if len(alternatives) > 1:
            def switch_alternative():
                self.image_tagging_alt_idx = (self.image_tagging_alt_idx + 1) % len(alternatives)
                if DEBUG:
                    print(f"[DEBUG] Standalone image tagging: Switching to alternative {self.image_tagging_alt_idx}")
                self._display_image_tagging(question)  # Don't pass alt_idx, let it use the updated index
            
            self.alt_image_button.config(
                text=labels[self.image_tagging_alt_idx],
                state=tk.NORMAL,
                command=switch_alternative
            )
            self.alt_image_button.pack(side=tk.LEFT, padx=10, pady=10)
        else:
            self.alt_image_button.pack_forget()

        # Get media and tags from current alternative
        media = altq.get('media', {})
        img_path = media.get("image")
        tags = altq.get("tags", [])

        if not img_path:
            self.feedback_label.config(text="Image path missing in image tagging question!", fg='red')
            return

        try:
            img = Image.open(self.resolve_media_path(img_path))
            canvas_w, canvas_h = img.size
            resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
            img = img.resize((canvas_w, canvas_h), resample)
            self.tag_bg_img = ImageTk.PhotoImage(img)
            
            if DEBUG:
                print(f"[DEBUG] Standalone image tagging: Using original size {canvas_w}x{canvas_h}, alternative {self.image_tagging_alt_idx}")
                
        except Exception as e:
            self.feedback_label.config(text=f"Failed to open image: {img_path}\n{e}", fg='red')
            return

        # Clear existing widgets
        for widget in self.options_frame.winfo_children():
            widget.destroy()

        # Create canvas container
        outer_frame = tk.Frame(self.options_frame)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        hbar = tk.Scrollbar(outer_frame, orient=tk.HORIZONTAL)
        vbar = tk.Scrollbar(outer_frame, orient=tk.VERTICAL)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Get visible size
        def get_visible_size():
            try:
                w = self.root.winfo_width()
                h = self.root.winfo_height()
                return max(CANVAS_MIN_WIDTH, min(w, canvas_w)), max(CANVAS_MIN_HEIGHT, min(h - RESERVED_HEIGHT, canvas_h))
            except Exception:
                return CANVAS_MIN_WIDTH * 3, CANVAS_MIN_HEIGHT * 2

        visible_w, visible_h = get_visible_size()

        # Create canvas
        self.tag_canvas_frame = outer_frame
        self.tag_canvas = tk.Canvas(
            outer_frame,
            width=visible_w,
            height=visible_h,
            background='white',
            xscrollcommand=hbar.set,
            yscrollcommand=vbar.set
        )
        self.tag_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        hbar.config(command=self.tag_canvas.xview)
        vbar.config(command=self.tag_canvas.yview)
        self.tag_canvas.config(scrollregion=(0, 0, canvas_w, canvas_h))

        # Display background image
        self.tag_canvas_image_id = self.tag_canvas.create_image(0, 0, anchor=tk.NW, image=self.tag_bg_img)
        self.bg_image_id = self.tag_canvas_image_id

        # Handle window resize
        def on_resize(event):
            w, h = get_visible_size()
            self.tag_canvas.config(width=w, height=h)

        self.root.bind("<Configure>", on_resize)

        # Mouse wheel scrolling
        def on_mouse_wheel(event):
            if hasattr(event, 'delta'):
                if event.state & 0x1:
                    self.tag_canvas.xview_scroll(int(-event.delta / 120), "units")
                else:
                    self.tag_canvas.yview_scroll(int(-event.delta / 120), "units")
            else:
                if event.num == 4:
                    self.tag_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.tag_canvas.yview_scroll(1, "units")
            return "break"

        self.tag_canvas.bind("<MouseWheel>", on_mouse_wheel)
        self.tag_canvas.bind("<Button-4>", on_mouse_wheel)
        self.tag_canvas.bind("<Button-5>", on_mouse_wheel)

        # Clear existing tag items
        self.tag_items = {}

        # Initialize tag positions dictionary if not exists
        if not hasattr(self, "tag_positions_dict"):
            self.tag_positions_dict = {}

        # FIXED: Get positions for current alternative index
        curr_tag_pos = self.tag_positions_dict.setdefault(str(self.image_tagging_alt_idx), {})

        # Create draggable tags
        for i, tag in enumerate(tags):
            tag_id = tag.get('id')
            label = tag.get('label', '')

            # Get saved position or use default
            if tag_id in curr_tag_pos:
                x0, y0 = curr_tag_pos[tag_id]
            else:
                x0 = TAG_START_X
                y0 = TAG_START_Y + i * 40
                curr_tag_pos[tag_id] = [x0, y0]

            # Calculate text size
            temp_text_id = self.tag_canvas.create_text(0, 0, text=label, font=FONT_TAG, anchor=tk.NW)
            bbox = self.tag_canvas.bbox(temp_text_id)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            self.tag_canvas.delete(temp_text_id)

            # Create tag rectangle and text
            rect_id = self.tag_canvas.create_rectangle(
                x0, y0, x0 + text_w + 2 * PADDING_X, y0 + text_h + 2 * PADDING_Y,
                fill="black", outline="yellow", tags=(tag_id, "draggable")
            )

            text_id = self.tag_canvas.create_text(
                x0 + PADDING_X, y0 + PADDING_Y, text=label,
                font=FONT_TAG, fill="yellow", anchor=tk.NW, tags=(tag_id, "draggable")
            )

            self.tag_items[tag_id] = (rect_id, text_id)

        # Tag dragging functionality
        def tag_canvas_start_drag(event):
            canvas = event.widget
            canvas_x = canvas.canvasx(event.x)
            canvas_y = canvas.canvasy(event.y)
            item = canvas.find_closest(canvas_x, canvas_y)
            if not item:
                return

            item = item[0]
            tag_id = None
            for tid, (rect_id, text_id) in self.tag_items.items():
                if item == rect_id or item == text_id:
                    tag_id = tid
                    break

            if tag_id:
                self.drag_data["tag_id"] = tag_id
                self.drag_data["x"] = canvas_x
                self.drag_data["y"] = canvas_y

        def tag_canvas_drag(event):
            canvas = event.widget
            if not self.drag_data["tag_id"]:
                return

            canvas_x = canvas.canvasx(event.x)
            canvas_y = canvas.canvasy(event.y)
            dx = canvas_x - self.drag_data["x"]
            dy = canvas_y - self.drag_data["y"]

            tag_id = self.drag_data["tag_id"]
            if tag_id in self.tag_items:
                rect_id, text_id = self.tag_items[tag_id]
                canvas.move(rect_id, dx, dy)
                canvas.move(text_id, dx, dy)

            self.drag_data["x"] = canvas_x
            self.drag_data["y"] = canvas_y

        def tag_canvas_end_drag(event):
            if self.drag_data["tag_id"]:
                tag_id = self.drag_data["tag_id"]
                if tag_id in self.tag_items:
                    rect_id, text_id = self.tag_items[tag_id]
                    bbox = self.tag_canvas.bbox(rect_id)
                    if bbox:
                        x, y = bbox[0], bbox[1]
                        # FIXED: Save to current alternative index
                        curr_tag_pos = self.tag_positions_dict.setdefault(str(self.image_tagging_alt_idx), {})
                        curr_tag_pos[tag_id] = [x, y]
                        
                        if DEBUG:
                            print(f"[DEBUG] Standalone image tagging: Tag '{tag_id}' moved to ({x}, {y}) on alternative {self.image_tagging_alt_idx}")

            self.drag_data["tag_id"] = None

        # Bind drag events
        self.tag_canvas.bind("<Button-1>", tag_canvas_start_drag)
        self.tag_canvas.bind("<B1-Motion>", tag_canvas_drag)
        self.tag_canvas.bind("<ButtonRelease-1>", tag_canvas_end_drag)

    def display_media_image(self, path):
        try:
            img = Image.open(path)
            base_width = 200
            wpercent = (base_width / float(img.size[0]))
            hsize = int((float(img.size[1]) * float(wpercent)))
            resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
            img = img.resize((base_width, hsize), resample)
            self.media_img = ImageTk.PhotoImage(img)
            self.media_label.config(image=self.media_img, cursor="hand2")
            self.media_label.bind("<Button-1>", lambda e, p=path: self.show_full_image(p))
        except Exception:
            self.feedback_label.config(text=f"Image not found: {path}", fg="red")

    def check_answer(self):
        if not self.questions or self.current_question >= len(self.questions):
            return

        question_block = self.questions[self.current_question]
        qtype = question_block.get('type')

        try:
            if qtype == "multi_questions":
                if DEBUG:
                    print(f"[DEBUG] Checking multi-questions block {self.current_question}")
                    
                # Check all sub-questions
                all_correct = True
                sub_questions = question_block.get('questions', [])
                
                for i, sub_question in enumerate(sub_questions):
                    sub_key = f"{self.current_question}-{i}"
                    sub_qtype = sub_question.get('type')
                    
                    if DEBUG:
                        print(f"[DEBUG] Checking sub-question {i} of type {sub_qtype}")
                    
                    # Check each sub-question type
                    if sub_qtype == 'mcq_single':
                        correct = self._check_mcq_single_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'mcq_multiple':
                        correct = self._check_mcq_multiple_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'word_fill':
                        correct = self._check_word_fill_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'list_pick':
                        correct = self._check_list_pick_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'sequence_audio':
                        correct = self._check_sequence_audio_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'match_sentence':
                        correct = self._check_match_sentence_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'match_phrases':
                        correct = self._check_match_phrases_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'fill_blanks_dropdown':
                        correct = self._check_fill_blanks_dropdown_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'order_phrase':
                        correct = self._check_order_phrase_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'categorization_multiple':
                        correct = self._check_categorization_multiple_in_frame(sub_question, sub_key)
                    elif sub_qtype == 'image_tagging':
                        correct = self._check_image_tagging_in_frame(sub_question, sub_key)
                    else:
                        # For unsupported types in multi-questions, assume incorrect
                        correct = False
                    
                    if DEBUG:
                        print(f"[DEBUG] Sub-question {i} result: {correct}")
                    
                    if not correct:
                        all_correct = False
                        break

                if all_correct:
                    self.feedback_label.config(text="All parts correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = "multi_question_completed"
                else:
                    self.feedback_label.config(text="Some parts are incorrect, please try again.", fg='red')

            elif qtype == "mcq_single":
                if DEBUG:
                    print(f"[DEBUG] Checking mcq_single: selected={self.mcq_var.get()}, correct={question_block.get('answer', [])}")
                    
                if self.mcq_var.get() < 0:
                    self.feedback_label.config(text="Please select an answer.", fg='red')
                    return
                correct_answer = question_block.get('answer', [])
                if self.mcq_var.get() in correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = self.mcq_var.get()
                else:
                    self.feedback_label.config(text="Incorrect, please try again.", fg='red')

            elif qtype == "mcq_multiple":
                selected = [i for i, var in enumerate(self.mcq_vars) if var.get() == 1]
                
                if DEBUG:
                    print(f"[DEBUG] Checking mcq_multiple: selected={selected}, correct={question_block.get('answer', [])}")
                    
                if not selected:
                    self.feedback_label.config(text="Please select at least one answer.", fg='red')
                    return
                correct_answer = set(question_block.get('answer', []))
                if set(selected) == correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = selected
                else:
                    self.feedback_label.config(text="Incorrect selection, please try again.", fg='red')
            elif qtype == "word_fill":
                user_answers = [entry.get().strip() for entry in self.fill_words_entries]
                correct_answers = question_block.get('answers', [])

                if DEBUG:
                    print(f"[DEBUG] Checking word_fill: user={user_answers}, correct={correct_answers}")

                all_correct = (
                    len(user_answers) == len(correct_answers)
                    and all(user.lower() == correct.lower() for user, correct in zip(user_answers, correct_answers))
                )

                if all_correct:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answers
                else:
                    self.feedback_label.config(text="Some answers are incorrect, please try again.", fg='red')
            elif qtype == "list_pick":
                selected_indices = list(self.listbox.curselection())
                correct_answer = set(question_block.get('answer', []))
                
                if DEBUG:
                    print(f"[DEBUG] Checking list_pick: selected={selected_indices}, correct={list(correct_answer)}")
                    
                if not selected_indices:
                    self.feedback_label.config(text="Please select at least one option.", fg='red')
                    return
                if set(selected_indices) == correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = selected_indices
                else:
                    self.feedback_label.config(text="Incorrect selection, please try again.", fg='red')

            elif qtype == "match_sentence":
                user_answer = {key: var.get() for key, var in self.match_vars.items()}
                correct_answer = question_block.get('answer', {})
                
                if DEBUG:
                    print(f"[DEBUG] Checking match_sentence: user={user_answer}, correct={correct_answer}")
                    
                if user_answer == correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answer
                else:
                    self.feedback_label.config(text="Incorrect matching, please try again.", fg='red')

            elif qtype == "categorization":
                user_answer = self.categ_var.get()
                correct_answer = question_block.get('correct', '')
                
                if DEBUG:
                    print(f"[DEBUG] Checking categorization: user='{user_answer}', correct='{correct_answer}'")
                    
                if user_answer == correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answer
                else:
                    self.feedback_label.config(text="Incorrect category, please try again.", fg='red')

            elif qtype == "categorization_multiple":
                user_answer = {key: var.get() for key, var in self.cat_vars.items()}
                correct_answer = question_block.get('answer', {})
                
                if DEBUG:
                    print(f"[DEBUG] Checking categorization_multiple: user={user_answer}, correct={correct_answer}")
                    
                if user_answer == correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answer
                else:
                    self.feedback_label.config(text="One or more categories incorrect, please try again.", fg='red')

            elif qtype == "sequence_audio":
                try:
                    user_sequence = [int(entry.get()) - 1 for entry in self.seq_entries if entry.get()]
                    correct_sequence = question_block.get('answer', [])
                    
                    if DEBUG:
                        print(f"[DEBUG] Checking sequence_audio: user={user_sequence}, correct={correct_sequence}")
                        
                    if len(user_sequence) != len(self.seq_entries):
                        self.feedback_label.config(text="Please complete the sequence.", fg='red')
                        return
                    if user_sequence == correct_sequence:
                        self.feedback_label.config(text="Correct!", fg='green')
                        self.submit_button.config(state=tk.DISABLED)
                        self.next_button.config(state=tk.NORMAL)
                        if self.current_question not in self.student_answers:
                            self.score += 1
                        self.student_answers[self.current_question] = user_sequence
                    else:
                        self.feedback_label.config(text="Incorrect sequence, please try again.", fg='red')
                except ValueError:
                    self.feedback_label.config(text="Please enter valid numbers.", fg='red')

            elif qtype == "order_phrase":
                user_order = [var.get() for var in self.word_vars]
                correct_order = question_block.get('answer', [])
                
                if DEBUG:
                    print(f"[DEBUG] Checking order_phrase: user={user_order}, correct={correct_order}")
                    
                if user_order == correct_order:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_order
                else:
                    self.feedback_label.config(text="Incorrect order, please try again.", fg='red')

            elif qtype == "fill_blanks_dropdown":
                user_answers = [var.get() for var in self.fill_vars]
                correct_answers = question_block.get('answers', [])
                
                if DEBUG:
                    print(f"[DEBUG] Checking fill_blanks_dropdown: user={user_answers}, correct={correct_answers}")
                    
                if user_answers == correct_answers:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answers
                else:
                    self.feedback_label.config(text="Some blanks are incorrect, please try again.", fg='red')

            elif qtype == "match_phrases":
                user_answer = {key: var.get() for key, var in self.match_vars.items()}
                correct_answer = question_block.get('answer', {})
                
                if DEBUG:
                    print(f"[DEBUG] Checking match_phrases: user={user_answer}, correct={correct_answer}")
                    
                if user_answer == correct_answer:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answer
                else:
                    self.feedback_label.config(text="Incorrect matching, please try again.", fg='red')

            elif qtype == "image_tagging":
                # Get the current alternative's answer
                alternatives = [question_block] + question_block.get("alternatives", [])
                alt_idx = getattr(self, "image_tagging_alt_idx", 0)
                
                if DEBUG:
                    print(f"[DEBUG] Checking image_tagging: alternative {alt_idx} of {len(alternatives)}")
                
                if alt_idx < len(alternatives):
                    current_alternative = alternatives[alt_idx]
                else:
                    current_alternative = question_block
                
                # Get current tag positions
                curr_tag_pos = self.tag_positions_dict.get(str(alt_idx), {})
                user_answer = curr_tag_pos.copy()
                
                # Get correct answer
                ans = current_alternative.get('answer', {})
                tolerance = 50
                correct = True
                
                if DEBUG:
                    print(f"[DEBUG] Image tagging positions: {curr_tag_pos}")
                    print(f"[DEBUG] Expected positions: {ans}")
                
                for tag_id, (cx, cy) in ans.items():
                    ux, uy = curr_tag_pos.get(tag_id, [-10000, -10000])
                    dist = ((cx - ux) ** 2 + (cy - uy) ** 2) ** 0.5
                    if DEBUG:
                        print(f"[DEBUG] Tag '{tag_id}': placed at ({ux:.1f},{uy:.1f}), expected ({cx},{cy}), distance {dist:.1f}")
                    if dist > tolerance:
                        correct = False
                        break

                if correct:
                    self.feedback_label.config(text="Correct!", fg='green')
                    self.submit_button.config(state=tk.DISABLED)
                    self.next_button.config(state=tk.NORMAL)
                    if self.current_question not in self.student_answers:
                        self.score += 1
                    self.student_answers[self.current_question] = user_answer
                else:
                    self.feedback_label.config(text="Incorrect, please try again.", fg='red')

            else:
                if DEBUG:
                    print(f"[DEBUG] Unsupported question type: {qtype}")
                self.feedback_label.config(text=f"Unsupported question type: {qtype}", fg='red')
                return

        except Exception as e:
            if DEBUG:
                print(f"[DEBUG] Error checking answer: {e}")
            self.feedback_label.config(text=f"Error checking answer: {e}", fg='red')
            return

    # NEW: Check methods for multi-question sub-questions
    def _check_mcq_single_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        var = self.current_multi_question_vars[key].get('mcq_var')
        if not var or var.get() < 0:
            return False
        correct_answer = question.get('answer', [])
        result = var.get() in correct_answer
        if DEBUG:
            print(f"[DEBUG] MCQ Single in frame {key}: selected={var.get()}, correct={correct_answer}, result={result}")
        return result

    def _check_mcq_multiple_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        vars_list = self.current_multi_question_vars[key].get('mcq_vars', [])
        selected = [i for i, var in enumerate(vars_list) if var.get() == 1]
        correct_answer = set(question.get('answer', []))
        result = set(selected) == correct_answer
        if DEBUG:
            print(f"[DEBUG] MCQ Multiple in frame {key}: selected={selected}, correct={list(correct_answer)}, result={result}")
        return result

    def _check_word_fill_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False

        entries = self.current_multi_question_vars[key].get('entries', [])
        user_answers = [entry.get().strip() for entry in entries]
        correct_answers = question.get('answers', [])

        result = (
            len(user_answers) == len(correct_answers)
            and all(user.lower() == correct.lower() for user, correct in zip(user_answers, correct_answers))
        )

        if DEBUG:
            print(f"[DEBUG] Word Fill in frame {key}: user={user_answers}, correct={correct_answers}, result={result}")

        return result


    def _check_list_pick_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        listbox = self.current_multi_question_vars[key].get('listbox')
        if not listbox:
            return False
        selected_indices = list(listbox.curselection())
        correct_answer = set(question.get('answer', []))
        result = set(selected_indices) == correct_answer
        if DEBUG:
            print(f"[DEBUG] List Pick in frame {key}: selected={selected_indices}, correct={list(correct_answer)}, result={result}")
        return result

    def _check_sequence_audio_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        entries = self.current_multi_question_vars[key].get('seq_entries', [])
        try:
            user_sequence = [int(entry.get()) - 1 for entry in entries if entry.get()]
            if len(user_sequence) != len(entries):
                return False
            correct_sequence = question.get('answer', [])
            result = user_sequence == correct_sequence
            if DEBUG:
                print(f"[DEBUG] Sequence Audio in frame {key}: user={user_sequence}, correct={correct_sequence}, result={result}")
            return result
        except ValueError:
            if DEBUG:
                print(f"[DEBUG] Sequence Audio in frame {key}: Invalid number format")
            return False

    def _check_match_sentence_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        match_vars = self.current_multi_question_vars[key].get('match_vars', {})
        user_answer = {k: var.get() for k, var in match_vars.items()}
        correct_answer = question.get('answer', {})
        result = user_answer == correct_answer
        if DEBUG:
            print(f"[DEBUG] Match Sentence in frame {key}: user={user_answer}, correct={correct_answer}, result={result}")
        return result

    def _check_match_phrases_in_frame(self, question, key):
        """FIXED: Added missing match_phrases check method"""
        if key not in self.current_multi_question_vars:
            return False
        match_vars = self.current_multi_question_vars[key].get('match_vars', {})
        user_answer = {k: var.get() for k, var in match_vars.items()}
        correct_answer = question.get('answer', {})
        result = user_answer == correct_answer
        if DEBUG:
            print(f"[DEBUG] Match Phrases in frame {key}: user={user_answer}, correct={correct_answer}, result={result}")
        return result

    def _check_fill_blanks_dropdown_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        fill_vars = self.current_multi_question_vars[key].get('fill_vars', [])
        user_answers = [var.get() for var in fill_vars]
        correct_answers = question.get('answers', [])
        result = user_answers == correct_answers
        if DEBUG:
            print(f"[DEBUG] Fill Blanks Dropdown in frame {key}: user={user_answers}, correct={correct_answers}, result={result}")
        return result

    def _check_order_phrase_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        word_labels = self.current_multi_question_vars[key].get('word_labels', [])
        user_order = [label['text'] for label in word_labels]
        correct_order = question.get('answer', [])
        result = user_order == correct_order
        if DEBUG:
            print(f"[DEBUG] Order Phrase in frame {key}: user={user_order}, correct={correct_order}, result={result}")
        return result

    def _check_categorization_multiple_in_frame(self, question, key):
        if key not in self.current_multi_question_vars:
            return False
        cat_vars = self.current_multi_question_vars[key].get('cat_vars', {})
        user_answer = {k: var.get() for k, var in cat_vars.items()}
        correct_answer = question.get('answer', {})
        result = user_answer == correct_answer
        if DEBUG:
            print(f"[DEBUG] Categorization Multiple in frame {key}: user={user_answer}, correct={correct_answer}, result={result}")
        return result

    def _check_image_tagging_in_frame(self, question, key):
        """FIXED: Added image tagging check for multi-questions"""
        if key not in self.current_multi_question_vars:
            return False
        
        # Get current alternative index for this multi-question
        alt_idx = self.current_multi_question_vars.get(f'{key}_alt_idx', 0)
        alternatives = [question] + question.get("alternatives", [])
        
        if alt_idx < len(alternatives):
            current_alternative = alternatives[alt_idx]
        else:
            current_alternative = question
        
        # Get tag positions for this multi-question
        tag_positions_key = f"{key}_{alt_idx}"
        curr_tag_pos = self.tag_positions_dict.get(tag_positions_key, {})
        
        # Get correct answer
        ans = current_alternative.get('answer', {})
        tolerance = 50
        
        if DEBUG:
            print(f"[DEBUG] Image Tagging in frame {key}: alternative {alt_idx}")
            print(f"[DEBUG] User positions: {curr_tag_pos}")
            print(f"[DEBUG] Expected positions: {ans}")
        
        for tag_id, (cx, cy) in ans.items():
            ux, uy = curr_tag_pos.get(tag_id, [-10000, -10000])
            dist = ((cx - ux) ** 2 + (cy - uy) ** 2) ** 0.5
            if DEBUG:
                print(f"[DEBUG] Tag '{tag_id}': placed at ({ux}, {uy}), expected ({cx}, {cy}), distance {dist:.1f}")
            if dist > tolerance:
                return False
        
        return True

    def next_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.activity_completed()
        else:
            self.display_question()

    def skip_question(self):
        self.current_question += 1
        if self.current_question >= len(self.questions):
            self.activity_completed()
        else:
            self.display_question()

    def activity_completed(self):
        messagebox.showinfo("Complete", f"Quiz completed! Your score: {self.score}/{len(self.questions)}")
        self.root.destroy()

    def show_full_image(self, path):
        try:
            top = tk.Toplevel(self.root)
            top.title("Image Preview")
            top.geometry('700x500')

            img = Image.open(path)
            w, h = img.size

            label = tk.Label(top, bg='black')
            label.pack(expand=True, fill=tk.BOTH)

            def resize(event=None):
                max_w = top.winfo_width() - 20
                max_h = top.winfo_height() - 20
                if max_w <= 0 or max_h <= 0:
                    return

                aspect = w / h
                if max_w / aspect < max_h:
                    new_w = max_w
                    new_h = int(max_w / aspect)
                else:
                    new_h = max_h
                    new_w = int(max_h * aspect)

                resample = getattr(Image, "Resampling", Image).LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS
                resized = img.resize((new_w, new_h), resample)
                photo = ImageTk.PhotoImage(resized)
                label.config(image=photo)
                label.image = photo

            top.bind('<Configure>', resize)
            top.after(100, resize)
            top.focus_set()
            top.grab_set()
            top.bind('<Escape>', lambda e: top.destroy())

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image preview:\n{e}")

    def launch_file(self, path):
        try:
            if platform.system() == 'Darwin':
                subprocess.Popen(['open', path])
            elif os.name == 'nt':
                os.startfile(path)
            elif os.name == 'posix':
                subprocess.Popen(['xdg-open', path])
            else:
                messagebox.showinfo("Info", f"Please open the file manually: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def open_audio(self, path):
        try:
            if platform.system() == 'Darwin':
                mac_ver = platform.mac_ver()[0]
                if mac_ver.startswith('10.6'):
                    subprocess.Popen(['open', '-a', 'QuickTime Player', path])
                    return
            self.launch_file(path)
        except Exception as e:
            messagebox.showerror("Audio Error", f"Failed to play audio:\n{e}")

def main():
    parser = argparse.ArgumentParser(description='Wifey MOOC Application')
    parser.add_argument('--question-file', type=str, help='Path to the question file to load')
    parser.add_argument('--progress-file', type=str, help='Path to the progress file to load')

    args = parser.parse_args()

    root = tk.Tk()
    app = WifeyMOOCApp(root, args.question_file, args.progress_file)
    root.mainloop()

if __name__ == '__main__':
    main()
