# Message Codec App

This is a simple encoder/decoder application built with Python 3.11 and Tkinter. The application provides a graphical interface that lets users enter messages and then encode or decode them using placeholder functions. These functions—`message_encode` and `message_decode`—are provided as stubs that currently reverse the text. They are intended to be customized by the developer to implement custom encoding/decoding logic.

## File Structure

- **msgcodec.py**: The main Python script containing the application code.
- **requirements.txt**: An empty file (no external dependencies are required).
- **.venv/**: A virtual environment folder for Python 3.11.

## Features

- **Graphical User Interface (GUI):**  
  Built using Tkinter, the app provides a resizable and scrollable window with a modern look.

- **Dynamic Message Lines:**  
  Each message line consists of:
  - A multiline text input area that auto-resizes to fit its content.
  - Buttons for **Encode**, **Decode**, and **Delete**.
  - Custom tab navigation for intuitive keyboard control.

- **Theming:**  
  The app detects the system's light or dark mode and adjusts the background colors of the message line containers to provide a visual cue for the currently focused message.

- **Customizable Encoding/Decoding:**  
  The placeholder functions `message_encode` and `message_decode` are implemented as simple text reversals for demonstration. Developers can modify these functions to implement any encoding or decoding algorithm.

## Requirements

- Python 3.11
- Tkinter (bundled with Python)
- No additional packages are required (the `requirements.txt` file is empty).

## Setup

1. **Create a Virtual Environment:**  
   From your project directory, run:
   ```bash
   python3.11 -m venv .venv
   ```

2. **Activate the Virtual Environment:**
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```

3. **Install Requirements (if any):**  
   The `requirements.txt` file is currently empty:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the application, simply run:
```bash
python msgcodec.py
```

## Customizing the Encoding/Decoding Logic

Inside `msgcodec.py`, you will find the following placeholder functions:

```python
def message_encode(text: str) -> str:
    return text[::-1]  # Reverse the text (placeholder)

def message_decode(text: str) -> str:
    return text[::-1]  # Reverse the text (placeholder)
```

These functions are currently set to reverse the input text. You can customize them to perform any desired encoding or decoding by replacing their implementations.
