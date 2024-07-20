# app_tkinter/gui.py
import tkinter as tk
from tkinter import filedialog, ttk
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO, solutions
import os

os.environ['QT_QPA_PLATFORM'] = 'xcb'

# load model
model = YOLO("./data/models/best.pt")
region_points = [(380, 370), (380, 390), (1350, 280), (1350, 260)]
line_points = [[450, 350], [1250, 280]]

region_points2 = [ (1380, 280),(1400, 280),(1850, 460), (1830, 460)]
# Init Object Counter
counter = solutions.ObjectCounter(
    view_img=False,
    reg_pts=region_points,
    classes_names=model.names,
    draw_tracks=True,
    line_thickness=2,
)

counter2 = solutions.ObjectCounter(
    view_img=False,
    reg_pts=region_points2,
    classes_names=model.names,
    draw_tracks=True,
    line_thickness=2,
)

# Constants for window and frame size
#(1920, 1080, 25)
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1000
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
        frame = counter2.start_counting(frame, tracks)


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
    #root.attributes('-fullscreen', True)

    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

    # Create a button to load a video
    load_button = tk.Button(control_frame, text="Load Video", command=load_video)
    load_button.pack(side=tk.TOP, padx=10, pady=10)

    # Create a button to stop the video
    stop_button = tk.Button(control_frame, text="Stop Video", command=stop_video)
    stop_button.pack(side=tk.TOP, padx=10, pady=10)

    # Create a table to display the object count
    columns = ('Class', 'Count')
    tree = ttk.Treeview(control_frame, columns=columns, show='headings', height=19)
    tree.heading('Class', text='Class')
    tree.heading('Count', text='Count')
    tree.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
    for name_i in range(len(model.names)):
        tree.insert('', 'end', values=(f'{model.names[name_i]}', 0))

    columns = ('Class', 'Count')
    tree2 = ttk.Treeview(control_frame, columns=columns, show='headings', height=19)
    tree2.heading('Class', text='Class')
    tree2.heading('Count', text='Count')
    tree2.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)

    # Create a label to display the video stream
    label = tk.Label(root)
    label.pack(side=tk.RIGHT, padx=10, pady=10)
    # Load and display an image
    img = Image.open('./notebooks/img.jpeg')
    img_tk = ImageTk.PhotoImage(img)
    label.config(image=img_tk)
    label.image = img_tk

    return root
