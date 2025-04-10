import tkinter as tk
from gtts import gTTS
import os
import tempfile
import threading
import math
import random
import pygame
import playsound
from pathlib import Path
from collections import deque

class Word:
    def __init__(self, text):
        self.text = text        # the actual word, like "cat"
        self.clicks = 0         # how many times it's been clicked

    def increment_clicks(self):
        self.clicks += 1        # add one when it's clicked


class ReadingApp:
    def __init__(self):
        pygame.mixer.init()

        self.root = tk.Tk()
        self.root.title("Learn to Read")
        self.root.geometry("800x600")
        self.current_theme = "Pastel Pink"  


        word_list = [
    "the", "and", "go", "had", "he", "see", "has", "you", "we", "of",
    "am", "at", "to", "as", "have", "in", "is", "it", "can", "his", "on", "did",
    "girl", "for", "up", "but", "all", "look", "with", "her", "what", "was", "were"
]

        self.words = sorted([Word(w) for w in word_list], key=lambda w: w.text)


        self.themes = {
            "Default": {"bg": "#f0f0f0","button_bg":"SystemButtonFace","button_fg":"#000000"},
            "Pastel Pink": {"bg": "#ffe6f0", "button_bg": "#ffb6c1", "button_fg": "#000"},
            "Soft Lavender": {"bg": "#f3e5f5", "button_bg": "#d1c4e9", "button_fg": "#000"},
            "Pale Yellow": {"bg": "#fff9c4", "button_bg": "#fff176", "button_fg": "#000"},
            "Mint Green": {"bg": "#e0f2f1", "button_bg": "#a5d6a7", "button_fg": "#000"},
            "Sky Blue": {"bg": "#e1f5fe", "button_bg": "#81d4fa", "button_fg": "#000"},
        }

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
        view_menu = tk.Menu(menu_bar, tearoff=0)
        for theme_name in self.themes:
            view_menu.add_command(label=theme_name, command=lambda name=theme_name: self.apply_theme(name))
        menu_bar.add_cascade(label="View", menu=view_menu)
        self.root.config(menu=menu_bar)

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

    def create_word_buttons(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        cols = self.adjust_window_size(len(self.words))
        for i, word in enumerate(self.words):
            button = tk.Button(self.frame, text=word.text, font=("Arial", 40, "bold"),
                       width=6, height=2, command=lambda w=word: self.check_word(w.text))
            button.grid(row=i // cols, column=i % cols, padx=10, pady=10)
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

    def adjust_window_size(self, num_words):
        max_width = self.root.winfo_screenwidth() * 0.8
        button_width = 180
        button_height = 120
        cols = max(2, min(num_words, int(max_width // button_width)))
        rows = math.ceil(num_words / cols)
        width = int(50 + cols * button_width)
        height = int(250 + rows * button_height)
        self.root.geometry(f"{width}x{height}")
        return cols

    def speak_word(self, word):
        def play_audio():
            temp_file = os.path.join(tempfile.gettempdir(), f"{word}.mp3")
            if not os.path.exists(temp_file):
                tts = gTTS(text=word, lang='en')
                tts.save(temp_file)
            playsound.playsound(temp_file) 
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
        self.root.after(500, lambda: self.speak_word(new_word))

    def toggle_game(self):
        if self.game_active:
            self.game_active = False
            self.game_button.config(bg="blue", text="Word Game")
            self.repeat_button.config(state="disabled", bg="gray")
            self.current_word = None
            self.score = 0
            self.score_label.config(text="Score: 0")
        else:
            self.game_active = True
            self.game_button.config(bg="red", text="Stop Game")
            self.repeat_button.config(state="normal", bg="green")
            self.score = 0
            self.score_label.config(text="Score: 0")
            self.start_game()

    def check_word(self, selected_word):
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
            # Track clicks for that word
            for word in self.words:
                if word.text == selected_word:
                    word.increment_clicks()
                    print(f"{word.text} has been clicked {word.clicks} times")  # Dev feedback

    def repeat_current_word(self):
        if self.game_active and self.current_word:
            self.speak_word(self.current_word)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ReadingApp()
    app.run()
