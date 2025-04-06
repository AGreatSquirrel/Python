# Word Game Application

A simple word-based interactive game that uses sounds, text-to-speech, and a graphical user interface (GUI) to enhance the gameplay experience.

## Features
- **Sound Effects:** Plays correct and incorrect sound effects for actions.
- **Text-to-Speech:** Speaks out the target words for an improved learning experience.
- **GUI:** A user-friendly interface for interacting with the game.
- **Game Logic:**
  - Players are provided with a set of words.
  - The objective is to select the correct word, receive feedback, and keep track of your score!

## Prerequisites

Ensure you have **Python 3.9** or later installed in your system.

## Installation

1. Clone the repository:

2. Navigate to the project folder:
   ```bash
   cd <project_folder>
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python Reading_V2.py
   ```

2. Interact with the game through the GUI:
   - Follow instructions on the screen to toggle the game, start, and play.


## Dependencies

The application relies on the following libraries:

- **[pygame](https://www.pygame.org/):** For playing sound effects in the application.
- **[pyttsx3](https://pyttsx3.readthedocs.io/):** For text-to-speech functionality.
- **tkinter:** For creating the GUI. Pre-installed with Python.
- **gtts:** Google Text to Speach allows for clearly dictated words.
- **threading:** Useful for processing multple things at a time.
- **tempfile:** This app creates temp files on the fly for the audio files
- **random:** Powers the word game.
- **Math:** Math :P
- **Playsound:** plays the word files
  

## Contributing

Feel free to fork the repository and submit pull requests with improvements or new features.
