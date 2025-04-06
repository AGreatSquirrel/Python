import tkinter as tk
from gtts import gTTS
import os
import tempfile
import playsound
import threading
import math
import random
import pygame  
import time
from pathlib import Path
from collections import deque

recent_words = deque(maxlen=5)  # Will hold the last 5 words


# Initialize pygame mixer
pygame.mixer.init()

# Load real sound files
CORRECT_SOUND_PATH = "correct.wav"  # Replace with actual path
WRONG_SOUND_PATH = "wrong.wav"  # Replace with actual path

def play_sound(sound_file):
    """Plays the given sound file"""
    pygame.mixer.Sound(sound_file).play()

def speak_word(word):
    """Plays the spoken word using gTTS"""
    def play_audio():
        temp_file = os.path.join(tempfile.gettempdir(), f"{word}.mp3")

        if not os.path.exists(temp_file):
            tts = gTTS(text=word, lang='en')
            tts.save(temp_file)

        playsound.playsound(temp_file)

    threading.Thread(target=play_audio, daemon=True).start()

def adjust_window_size(root, num_words):
    """Dynamically adjusts window size and column count based on bigger buttons."""
    max_width = root.winfo_screenwidth() * 0.8  # Use 80% of screen width
    button_width = 180   # increased for bigger buttons
    button_height = 120  # increased for taller buttons

    cols = max(2, min(num_words, int(max_width // button_width)))
    rows = math.ceil(num_words / cols)

    width = int(50 + cols * button_width)
    height = int(150 + rows * button_height)  # room for buttons + score + controls

    root.geometry(f"{width}x{height}")
    return cols
 

def create_word_buttons(root, words):
    """Creates word buttons dynamically"""
    frame = tk.Frame(root)
    frame.pack(pady=10)

    cols = adjust_window_size(root, len(words))  
    buttons = {}

    for i, word in enumerate(words):
        button = tk.Button(frame, text=word, font=("Arial", 24, "bold"), width=6, height=2, command=lambda w=word: check_word(w, buttons))
        button.grid(row=i // cols, column=i % cols, padx=10, pady=10)
        buttons[word] = button  

    game_button = tk.Button(root, text="Word Game", font=("Arial", 24, "bold"), bg="blue", fg="white", command=lambda: toggle_game(buttons, game_button))
    game_button.pack(pady=10)

    global score_label
    score_label = tk.Label(root, text="Score: 0", font=("Arial", 18))
    score_label.pack()

def toggle_game(buttons, game_button):
    """Turns the word game ON or OFF"""
    global game_active, current_word, score  

    if game_active:  
        game_active = False  
        game_button.config(bg="blue", text="Word Game")  
        current_word = None  
        score = 0  
        score_label.config(text="Score: 0")  
    else:  
        game_active = True  
        game_button.config(bg="red", text="Stop Game")  
        score = 0  
        score_label.config(text="Score: 0")  
        start_game(buttons)  

def start_game(buttons):
    global current_word

    if not game_active:
        return

    available_words = [word for word in buttons.keys() if word not in recent_words]

    # If not enough unique words, allow repeats from the recent list
    if not available_words:
        available_words = list(buttons.keys())

    new_word = random.choice(available_words)
    current_word = new_word
    recent_words.append(new_word)

    root.after(500, lambda: speak_word(new_word))  # 0.5s delay before speaking

def check_word(selected_word, buttons):
    """Checks if the selected word matches the game word and updates score"""
    global score
    if game_active:
        if selected_word == current_word:
            buttons[selected_word].config(bg="green")  
            play_sound(CORRECT_SOUND_PATH)  # Play correct sound  
            root.after(1000, lambda: buttons[selected_word].config(bg="SystemButtonFace"))  
            score += 1  
            score_label.config(text=f"Score: {score}")  
            root.after(1500, lambda: start_game(buttons))  # **1.5s delay before next word**
        else:
            buttons[selected_word].config(bg="red")  
            play_sound(WRONG_SOUND_PATH)  # Play wrong sound  
            root.after(1000, lambda: buttons[selected_word].config(bg="SystemButtonFace"))  
            score = 0  
            score_label.config(text="Score: 0")  
    else:
        speak_word(selected_word)  # Just say the word if game is off

def repeat_current_word():
    if game_active and current_word:
        speak_word(current_word)

def toggle_game(buttons, game_button):
    global game_active, current_word, score

    if game_active:
        game_active = False
        game_button.config(bg="blue", text="Word Game")
        current_word = None
        score = 0
        score_label.config(text="Score: 0")
        repeat_button.config(state="disabled", bg="gray")
    else:
        game_active = True
        game_button.config(bg="red", text="Stop Game")
        score = 0
        score_label.config(text="Score: 0")
        repeat_button.config(state="normal", bg="green")
        start_game(buttons)


# Main application
root = tk.Tk()
root.title("Learn to Read")

words = sorted(["the", "and", "go", "had", "he", "see", "has", "you", "we", "of", "am", "at", "to", "as", "have", "in", "is", "it", "can", "his", "on", "did", "girl", "for", "up", "but", "all", "look", "with", "her", "what", "was", "were"])

game_active = False  
current_word = None  
score = 0  

create_word_buttons(root, words)

repeat_button = tk.Button(
    root,
    text="Repeat Word",
    font=("Arial", 24),
    bg="gray",
    fg="white",
    command=lambda: repeat_current_word()
)
repeat_button.pack(pady=5)


root.mainloop()
