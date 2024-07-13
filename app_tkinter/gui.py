# app_tkinter/gui.py
import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO, solutions
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'

# load model
model = YOLO("./data/models/best.pt")
region_points = [(400, 250), (450, 320), (1250, 280), (1000, 220)]
line_points = [[450, 350], [1250, 280]]
# Init Object Counter
counter = solutions.ObjectCounter(
    view_img=False,
    reg_pts=line_points,
    classes_names=model.names,
    draw_tracks=True,
    line_thickness=2,
)

# Constants for window and frame size
#(1920, 1080, 25)
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
FRAME_WIDTH = 800
FRAME_HEIGHT = 480

# Flag to control the video capture
running = False

def load_video():
    global cap, running
    video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")])
    if video_path:
        cap = cv2.VideoCapture(video_path)
        running = True
        update_frame()

def stop_video():
    global running
    running = False
    if 'cap' in globals():
        cap.release()
    label.config(image='')

def update_frame():
    if running:
        ret, frame = cap.read()

        ## MODEL
        tracks = model.track(frame, persist=True, show=False)
        frame = counter.start_counting(frame, tracks)


        if ret:
            # Resize the frame to fit the specified dimensions
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk
            label.configure(image=imgtk)
        label.after(10, update_frame)

def create_main_window():
    global label
    # Create a window
    root = tk.Tk()
    root.title("Video Stream")

    # Set a fixed size for the window
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

    # Create a button to load a video
    load_button = tk.Button(root, text="Load Video", command=load_video)
    load_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Create a button to stop the video
    stop_button = tk.Button(root, text="Stop Video", command=stop_video)
    stop_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Create a label to display the video stream
    label = tk.Label(root)
    label.pack(side=tk.RIGHT, padx=10, pady=10)

    return root
