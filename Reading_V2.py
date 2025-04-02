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

# Initialize pygame mixer
pygame.mixer.init()

# Load real sound files
CORRECT_SOUND_PATH = "correct.wav"  # Replace with actual path
WRONG_SOUND_PATH = "wrong.mp3"  # Replace with actual path

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
    """Dynamically adjusts window size and column count"""
    max_width = root.winfo_screenwidth() // 2  
    button_width = 150  
    cols = max(2, min(num_words, max_width // button_width))  
    rows = math.ceil(num_words / cols)  
    width = 200 + (cols * button_width)  
    height = 100 + (rows * 80) + 120  

    root.geometry(f"{width}x{height}")
    return cols  

def create_word_buttons(root, words):
    """Creates word buttons dynamically"""
    frame = tk.Frame(root)
    frame.pack(pady=10)

    cols = adjust_window_size(root, len(words))  
    buttons = {}

    for i, word in enumerate(words):
        button = tk.Button(frame, text=word, font=("Arial", 24), command=lambda w=word: check_word(w, buttons))
        button.grid(row=i // cols, column=i % cols, padx=10, pady=10)
        buttons[word] = button  

    game_button = tk.Button(root, text="Word Game", font=("Arial", 20, "bold"), bg="blue", fg="white", command=lambda: toggle_game(buttons, game_button))
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
    """Picks a random word and speaks it for the player to find"""
    global current_word  
    if game_active:
        current_word = random.choice(list(buttons.keys()))  
        root.after(500, lambda: speak_word(current_word))  # 0.5s delay before speaking the word

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

# Main application
root = tk.Tk()
root.title("Learn to Read")

words = sorted(["cat", "dog", "sun", "moon", "tree", "house", "car", "bird", "fish", "apple", "banana", 
                "chair", "table", "book", "phone", "star", "cloud", "river", "mountain"])

game_active = False  
current_word = None  
score = 0  

create_word_buttons(root, words)

root.mainloop()
