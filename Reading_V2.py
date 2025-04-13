import tkinter as tk
from gtts import gTTS
import os
import tempfile
import threading
import math
import random
import pygame
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

        word_list = [
            "the", "and", "go", "had", "he", "see", "has", "you", "we", "of",
            "am", "at", "to", "as", "have", "in", "is", "it", "can", "his", "on", "did",
            "girl", "for", "up", "but", "all", "look", "with", "her", "what", "was", "were"
        ]

        self.words = sorted([Word(w) for w in word_list], key=lambda w: w.text)

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
        self.create_word_buttons()
        self.setup_controls()

    def setup_menu(self):
        menu_bar = tk.Menu(self.root)

        options_menu = tk.Menu(menu_bar, tearoff=0)
        theme_menu = tk.Menu(options_menu, tearoff=0)
        for theme_name in self.themes:
            theme_menu.add_command(label=theme_name, command=lambda name=theme_name: self.apply_theme(name))
        options_menu.add_cascade(label="Themes", menu=theme_menu)

        size_menu = tk.Menu(options_menu, tearoff=0)
        self.sizes = {"Small": 20, "Medium": 30, "Large": 36}
        for size_name, size_value in self.sizes.items():
            size_menu.add_command(label=size_name, command=lambda value=size_value: self.apply_size(value))
        options_menu.add_cascade(label="Size", menu=size_menu)

        difficulty_menu = tk.Menu(options_menu, tearoff=0)
        for level in ["Easy", "Medium", "Hard"]:
            difficulty_menu.add_command(label=level, command=lambda lvl=level: self.set_difficulty(lvl))
        options_menu.add_cascade(label="Difficulty", menu=difficulty_menu)

        menu_bar.add_cascade(label="Options", menu=options_menu)
        self.root.config(menu=menu_bar)

    def set_difficulty(self, level):
        self.current_difficulty = level

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        theme = self.themes.get(theme_name)
        if not theme:
            return

        self.root.config(bg=theme["bg"])
        self.frame.config(bg=theme["bg"])
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

    def create_word_buttons(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        cols = self.adjust_window_size(len(self.words), self.current_font_size)
        for i, word in enumerate(self.words):
            button = tk.Button(self.frame, text=word.text, font=("Arial", self.current_font_size, "bold"),
                               width=5, height=1, command=lambda w=word: self.check_word(w.text))
            button.grid(row=i // cols, column=i % cols, padx=5, pady=5)
            self.buttons[word.text] = button

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

        button_width = font_size * 8
        button_height = font_size * 2.5

        max_cols = int(screen_width * 0.95 // button_width)
        cols = max(2, min(num_words, max_cols))
        rows = math.ceil(num_words / cols)

        width = min(int(50 + cols * button_width), int(screen_width * 0.95))
        height = min(int(350 + rows * button_height), int(screen_height * 0.95))

        self.root.geometry(f"{width}x{height}")
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

    def play_sound(self, file):
        pygame.mixer.Sound(file).play()

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
