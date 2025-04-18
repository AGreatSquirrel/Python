import tkinter as tk
from gtts import gTTS
import os
import tempfile
import threading
import math
import random
import pygame
import sys
from pathlib import Path
from collections import deque

class Word:
    def __init__(self, text):
        self.text = text
        self.clicks = 0

    def increment_clicks(self):
        self.clicks += 1

class ReadingApp:
    def __init__(self):
        pygame.mixer.init()

        self.root = tk.Tk()
        self.root.title("Learn to Read")
        self.current_font_size = 24

        self.word_themes = {
            "High Frequency": [
                "the", "and", "go", "had", "he", "see", "has", "you", "we", "of",
                "am", "at", "to", "as", "have", "in", "is", "it", "can", "his", "on", "did",
                "girl", "for", "up", "but", "all", "look", "with", "her", "what", "was", "were"
            ],
            "Animals": [
                "cat", "dog", "bird", "fish", "lion", "tiger", "bear", "cow", "duck", "sheep",
                "goose", "pig", "panda", "monkey", "giraffe", "elephant", "jagur", "cheeta",
                "whale", "eagle", "gorilla", "monster", "frog"
            ],
            "House": [
                "table", "chair", "bed", "door", "window", "lamp", "sofa", "cup", "plate", "spoon",
                "fork", "knife", "jar", "wipe", "paper", "computer", "couch", "stove", "pan",
                "pillow", "blanket", "toy", "water", "food"
            ],
            "School": [
                "book", "pen", "pencil", "bag", "teacher", "desk", "chalk", "board", "class", "student",
                "marker", "hallway", "lunch", "gym", "school", "math", "centers", "science",
                "reading", "learn", "write", "name"
            ],
            "Food": [
                "apple", "banana", "grapes", "peach", "berry", "bread", "pizza", "salad", "nuggets",
                "orange", "cerial", "pancake", "waffel", "potato", "fries", "burger", "strawberry",
                "bacon", "ham", "steak", "chicken", "meat", "cheese"
            ]
        }

        self.current_theme_name = "High Frequency"
        self.words = sorted([Word(w) for w in self.word_themes[self.current_theme_name]], key=lambda w: w.text)

        self.themes = {
            "Default": {"bg": "#f0f0f0", "button_bg": "SystemButtonFace", "button_fg": "#000000"},
            "Pastel Pink": {"bg": "#ffe6f0", "button_bg": "#ffb6c1", "button_fg": "#000"},
            "Soft Lavender": {"bg": "#f3e5f5", "button_bg": "#d1c4e9", "button_fg": "#000"},
            "Pale Yellow": {"bg": "#fff9c4", "button_bg": "#fff176", "button_fg": "#000"},
            "Mint Green": {"bg": "#e0f2f1", "button_bg": "#a5d6a7", "button_fg": "#000"},
            "Sky Blue": {"bg": "#e1f5fe", "button_bg": "#81d4fa", "button_fg": "#000"},
        }

        self.current_theme = "Default"
        self.current_difficulty = "Hard"
        self.current_word = None
        self.score = 0
        self.game_active = False
        self.recent_words = deque(maxlen=5)
        self.buttons = {}

        self.setup_menu()
        self.setup_scrollable_word_area()
        self.create_word_buttons()
        self.setup_controls()

    def setup_scrollable_word_area(self):
        self.button_area_frame = tk.Frame(self.root)
        self.button_area_frame.pack(side="top", fill="both", expand=True)

        self.canvas = tk.Canvas(self.button_area_frame, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.button_area_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", tags="frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        def resize_canvas_frame():
            canvas_width = self.canvas.winfo_width()
            self.canvas.itemconfig("frame", width=canvas_width)

        self.canvas.bind("<Configure>", lambda e: self.root.after_idle(resize_canvas_frame))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Create a container for controls
        self.control_container = tk.Frame(self.root)
        self.control_container.pack(side="bottom", fill="x", pady=10)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def play_sound(self, file):
        sound_path = self.resource_path(file)
        pygame.mixer.Sound(sound_path).play()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme_name in self.themes:
            theme_menu.add_command(label=theme_name, command=lambda name=theme_name: self.apply_theme(name))
        view_menu.add_cascade(label="Themes", menu=theme_menu)

        size_menu = tk.Menu(view_menu, tearoff=0)
        self.sizes = {"Small": 20, "Medium": 30, "Large": 36}
        for size_name, size_value in self.sizes.items():
            size_menu.add_command(label=size_name, command=lambda value=size_value: self.apply_size(value))
        view_menu.add_cascade(label="Size", menu=size_menu)

        difficulty_menu = tk.Menu(view_menu, tearoff=0)
        for level in ["Easy", "Medium", "Hard"]:
            difficulty_menu.add_command(label=level, command=lambda lvl=level: self.set_difficulty(lvl))
        view_menu.add_cascade(label="Difficulty", menu=difficulty_menu)

        word_theme_menu = tk.Menu(view_menu, tearoff=0)
        for theme_name in self.word_themes:
            word_theme_menu.add_command(label=theme_name, command=lambda name=theme_name: self.set_word_theme(name))
        view_menu.add_cascade(label="Word Themes", menu=word_theme_menu)

        menu_bar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=menu_bar)

    def set_word_theme(self, theme_name):
        self.current_theme_name = theme_name
        self.words = sorted([Word(w) for w in self.word_themes[theme_name]], key=lambda w: w.text)
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.buttons.clear()
        self.create_word_buttons()
        self.apply_theme(self.current_theme)
        self.root.update_idletasks()
        self.canvas.itemconfig("frame", width=self.canvas.winfo_width())
        self.root.after_idle(lambda: self.canvas.itemconfig("frame", width=self.canvas.winfo_width()))
        self.adjust_window_size(len(self.words), self.current_font_size)

    def create_word_buttons(self):
        cols = self.adjust_window_size(len(self.words), self.current_font_size)

        # Force each column to expand equally
        for col in range(cols):
            self.scrollable_frame.grid_columnconfigure(col, weight=1)

        for i, word in enumerate(self.words):
            button = tk.Button(self.scrollable_frame, text=word.text, font=("Arial", self.current_font_size, "bold"),
                               width=9, height=1, command=lambda w=word: self.check_word(w.text))
            button.grid(row=i // cols, column=i % cols, padx=5, pady=5)
            self.buttons[word.text] = button


    def set_difficulty(self, level):
        self.current_difficulty = level

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = self.themes.get(theme_name)
        if not theme:
            return

        self.root.config(bg=theme["bg"])
        self.scrollable_frame.config(bg=theme["bg"])
        self.control_frame.config(bg=theme["bg"])
        self.score_label.config(bg=theme["bg"], fg=theme["button_fg"])
        for button in self.buttons.values():
            button.config(bg=theme["button_bg"], fg=theme["button_fg"])
        self.game_button.config(bg=theme["button_bg"], fg=theme["button_fg"])
        self.repeat_button.config(bg=theme["button_bg"], fg=theme["button_fg"])

    def apply_size(self, font_size):
        self.current_font_size = font_size
        for button in self.buttons.values():
            button.config(font=("Arial", font_size, "bold"))
        self.game_button.config(font=("Arial", font_size, "bold"))
        self.repeat_button.config(font=("Arial", font_size))
        self.score_label.config(font=("Arial", int(font_size * 0.75)))
        self.adjust_window_size(len(self.buttons), font_size)

    def setup_controls(self):
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        self.game_button = tk.Button(self.control_frame, text="Word Game", font=("Arial", 24, "bold"),
                                     bg="blue", fg="white", command=self.toggle_game)
        self.game_button.grid(row=0, column=0, padx=10)

        self.repeat_button = tk.Button(self.control_frame, text="Repeat Word", font=("Arial", 24),
                                       bg="gray", fg="white", command=self.repeat_current_word)
        self.repeat_button.grid(row=0, column=1, padx=10)
        self.repeat_button.config(state="disabled")

        self.score_label = tk.Label(self.root, text="Score: 0", font=("Arial", 18))
        self.score_label.pack()

    def adjust_window_size(self, num_words, font_size):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        button_width_px = font_size * 12  # estimate pixel width per button
        button_height_px = font_size * 3  # estimate height per button

        max_cols = max(2, screen_width // button_width_px)
        cols = min(num_words, max_cols)
        rows = math.ceil(num_words / cols)

        width = min(50 + cols * button_width_px, screen_width * 0.95)
        height = min(300 + rows * button_height_px, screen_height * 0.95)

        self.root.geometry(f"{int(width)}x{int(height)}")
        return cols

    def speak_word(self, word):
        def play_audio():
            temp_file = os.path.join(tempfile.gettempdir(), f"{word}.mp3")
            if not os.path.exists(temp_file):
                tts = gTTS(text=word, lang='en')
                tts.save(temp_file)
            from playsound import playsound
            playsound(temp_file)
        threading.Thread(target=play_audio, daemon=True).start()

    def start_game(self):
        available_words = [word for word in self.buttons if word not in self.recent_words]
        if not available_words:
            available_words = list(self.buttons.keys())

        new_word = random.choice(available_words)
        self.current_word = new_word
        self.recent_words.append(new_word)

        button_keys = list(self.buttons.keys())
        if self.current_difficulty == "Easy":
            hide_ratio = 0.75
        elif self.current_difficulty == "Medium":
            hide_ratio = 0.5
        else:
            hide_ratio = 0.0

        to_hide = random.sample([b for b in button_keys if b != new_word], int(len(button_keys) * hide_ratio))
        for word in button_keys:
            if word in to_hide:
                self.buttons[word].config(state="disabled", bg="gray")
            else:
                theme = self.themes[self.current_theme]
                self.buttons[word].config(state="normal", bg=theme["button_bg"], fg=theme["button_fg"])

        self.root.after(500, lambda: self.speak_word(new_word))

    def toggle_game(self):
        if self.game_active:
            self.game_active = False
            self.game_button.config(bg="blue", text="Word Game")
            self.repeat_button.config(state="disabled", bg="gray")
            self.current_word = None
            self.score = 0
            self.score_label.config(text="Score: 0")

            theme = self.themes[self.current_theme]
            for button in self.buttons.values():
                button.config(state="normal", bg=theme["button_bg"], fg=theme["button_fg"])
        else:
            self.game_active = True
            self.game_button.config(bg="red", text="Stop Game")
            self.repeat_button.config(state="normal", bg="green")
            self.score = 0
            self.score_label.config(text="Score: 0")
            self.start_game()

    def check_word(self, selected_word):
        for word in self.words:
            if word.text == selected_word:
                word.increment_clicks()

        if self.game_active:
            if selected_word == self.current_word:
                self.buttons[selected_word].config(bg="green")
                self.play_sound("correct.wav")
                self.root.after(1000, lambda: self.buttons[selected_word].config(
                    bg=self.themes[self.current_theme]["button_bg"],
                    fg=self.themes[self.current_theme]["button_fg"]
                ))
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")
                self.root.after(1500, self.start_game)
            else:
                self.buttons[selected_word].config(bg="red")
                self.play_sound("wrong.wav")
                self.root.after(1000, lambda: self.buttons[selected_word].config(
                    bg=self.themes[self.current_theme]["button_bg"],
                    fg=self.themes[self.current_theme]["button_fg"]
                ))
                self.score = 0
                self.score_label.config(text="Score: 0")
        else:
            self.speak_word(selected_word)

    def repeat_current_word(self):
        if self.game_active and self.current_word:
            self.speak_word(self.current_word)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ReadingApp()
    app.run()
