import cv2
color_map = {
    1: (255, 0, 0),        # Red
    13: (0, 255, 0),       # Green
    11: (0, 0, 255),       # Blue
    12: (255, 255, 0),     # Yellow
    4: (255, 0, 255),      # Magenta
    5: (0, 255, 255),      # Cyan
    9: (128, 0, 0),        # Maroon
    10: (0, 128, 0),       # Dark Green
    14: (0, 0, 128),       # Navy
    2: (128, 128, 0),      # Olive
    3: (128, 0, 128),      # Purple
    6: (0, 128, 128),      # Teal
    7: (192, 192, 192),    # Silver
    8: (128, 128, 128),    # Gray
    15: (255, 165, 0),     # Orange
    16: (255, 105, 180),   # Hot Pink
    17: (0, 255, 127),     # Spring Green
    18: (70, 130, 180),    # Steel Blue
    19: (255, 215, 0)      # Gold
}


clasess = {
    1:'1_Auto Privado',
    13: '13_Bus',
    11: '11_Camioneta rural',
    12:'12_Microbus',
    4:'4_Mototaxi',
    5:'5_Moto lineal',
    9:'9_Omnibus Interprovincial',
    10:'10_Auto colectivo',
    14:'14_Articulado',
    2:'2_Cam. PickUp',
    3:'3_Taxi',
    6:'6_Bicicletas',
    7:'7_Scooter',
    8:'8_TransportenEscolar Personal',
    15:'15_TC_Ligeros',
    16:'16_TC Pesados',
    17:'17_TC SemiTrailler Trailer',
    18:'18_Triciclo',
    19:'19_Ambulancia'
}

def draw_boxes(image, boxes):
    for box in boxes:
        x, y, w, h, conf, cls = box
        x1 = int(x - w / 2)
        y1 = int(y - h / 2)
        x2 = int(x + w / 2)
        y2 = int(y + h / 2)
        color = color_map.get(int(cls), (0, 255, 255))  # Default to yellow if class not in color_map
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        label = f'{clasess.get(int(cls)+1, "desconocido")}, {conf:.2f}'
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)