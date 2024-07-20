import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import numpy as np

# Mock imports since ultralytics and cv2 are not needed for this example
# import cv2
# from ultralytics import YOLO, solutions

# Dummy initialization to avoid import errors
# model = YOLO("./data/models/best.pt")
# counter = solutions.ObjectCounter()

# Constants for window size
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 400

# Create the main window
root = tk.Tk()
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.title("Random Number Table Update")

# Create a frame to hold buttons and table
control_frame = tk.Frame(root)
control_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

# Create buttons
load_button = tk.Button(control_frame, text='Load Video')
load_button.pack(side=tk.TOP, padx=10, pady=10)
stop_button = tk.Button(control_frame, text='Stop Video')
stop_button.pack(side=tk.TOP, padx=10, pady=10)

# Create a table to display the object count
columns = ('Class', 'Count')
tree = ttk.Treeview(control_frame, columns=columns, show='headings')
tree.heading('Class', text='Class')
tree.heading('Count', text='Count')
tree.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

# Create a label for displaying an image
label = tk.Label(root)
label.pack(side=tk.RIGHT, padx=10, pady=10)

# Load and display an image
img = Image.open('img.jpeg')
img_tk = ImageTk.PhotoImage(img)
label.config(image=img_tk)
label.image = img_tk

# Function to update table with new random numbers
def update_table():
    for item in tree.get_children():
        tree.delete(item)
    
    # Generate new random numbers
    random_numbers = np.random.randint(100, size=(10))  # Generate 10 new random numbers
    
    # Insert new random numbers into the table
    for obj_class, count in enumerate(random_numbers):
        tree.insert('', 'end', values=(f'Class {obj_class}', count))
    
    # Schedule the next update after 1 second (1000 milliseconds)
    root.after(1000, update_table)

# Start updating the table periodically
update_table()

# Start the tkinter main loop
root.mainloop()
