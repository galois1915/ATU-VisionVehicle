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
    view_in_counts=False,
    view_out_counts=False,
    line_thickness=1,
)

counter2 = solutions.ObjectCounter(
    view_img=False,
    reg_pts=region_points2,
    classes_names=model.names,
    draw_tracks=True,
    view_in_counts=False, 
    view_out_counts=False,
    line_thickness=1,
)

# Constants for window and frame size
#(1920, 1080, 25)
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 1800
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

def update_row(class_name, line1_value, line2_value, total_value):
    for item in tree.get_children():
        item_values = tree.item(item, 'values')
        if item_values[0] == class_name:
            tree.item(item, values=(class_name, line1_value, line2_value, total_value))


def update_frame():
    if running:
        ret, frame = cap.read()

        ## MODEL
        tracks = model.track(frame, persist=True, show=False)
        frame = counter.start_counting(frame, tracks)
        frame = counter2.start_counting(frame, tracks)

        count1 = counter.class_wise_count
        total1 = {}
        for i in count1.keys():
            total1[i] = count1[i]['IN'] + count1[i]['OUT']
        
        count2 = counter2.class_wise_count
        total2 = {}
        for i in count2.keys():
            total2[i] = count2[i]['IN'] + count2[i]['OUT']

        # Unir diccionarios
        diccionario_unido = {}

        # Recorrer todas las claves únicas de ambos diccionarios
        for clave in set(total1.keys()).union(total2.keys()):
            valor1 = total1.get(clave, 0)  # Obtiene el valor del diccionario1 o 0 si no existe
            valor2 = total2.get(clave, 0)  # Obtiene el valor del diccionario2 o 0 si no existe

            if isinstance(valor1, int) and isinstance(valor2, int) and valor1 == 0 and valor2 == 0:
                diccionario_unido[clave] = [0,0]  # Si ambos valores son 0, poner 0 en el diccionario unido
            else:
                diccionario_unido[clave] = [valor1, valor2]  # Combinar los valores en una lista


        for i in diccionario_unido.keys():   
            update_row(i, diccionario_unido[i][0], diccionario_unido[i][1], diccionario_unido[i][1]+diccionario_unido[i][0])


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
    global label, tree
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
    columns = ('Class', 'Line1', 'Line2', 'total')
    tree = ttk.Treeview(control_frame, columns=columns, show='headings', height=19,)
    tree.heading('Class', text='Class')
    tree.heading('Line1', text='Line1')
    tree.heading('Line2', text='Line2')
    tree.heading('total', text='total')
    # Set the width of the columns
    tree.column('Class', width=200)
    tree.column('Line1', width=50)
    tree.column('Line2', width=50)
    tree.column('total', width=50)
    tree.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
    for name_i in range(len(model.names)):
        tree.insert('', 'end', values=(f'{model.names[name_i]}', 0, 0, 0))

    # Create a label to display the video stream
    label = tk.Label(root)
    label.pack(side=tk.RIGHT, padx=10, pady=10)
    # Load and display an image
    img = Image.open('./notebooks/img.jpeg')
    img_tk = ImageTk.PhotoImage(img)
    label.config(image=img_tk)
    label.image = img_tk

    return root
