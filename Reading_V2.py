import tkinter as tk
from gtts import gTTS
import os
import tempfile
import playsound
import threading

def speak_word(word):
    def play_audio():
        temp_file = os.path.join(tempfile.gettempdir(), f"{word}.mp3")
        
        # Generate only once per word
        if not os.path.exists(temp_file):
            tts = gTTS(text=word, lang='en')
            tts.save(temp_file)
        
        playsound.playsound(temp_file)  # Play without blocking

    threading.Thread(target=play_audio, daemon=True).start()  # Prevents Tkinter from freezing

def create_word_buttons(root, words):
    frame = tk.Frame(root)
    frame.pack(pady=10)
    
    rows, cols = 5, 3
    for i, word in enumerate(words):
        button = tk.Button(frame, text=word, font=("Arial", 24), command=lambda w=word: speak_word(w))
        button.grid(row=i // cols, column=i % cols, padx=10, pady=10)

# Main application
root = tk.Tk()
root.title("Learn to Read")
root.geometry("600x400")

words = ["the", "and", "go", "had", "he", "see", "has", "you", "we", "of", "am", "at", "to", "as", "have", "in", "is", "it", "can", "his", "on", "did", "girl", "for", "up", "but", "all", "look", "with", "her", "what", "was", "were"]  # Add more words as needed
create_word_buttons(root, words)

root.mainloop()

