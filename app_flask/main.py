from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import os
from ultralytics import YOLO, solutions   

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

model = YOLO("./models/best.pt")

@app.route('/')
def index():
    return render_template('index.html', video_path=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        return redirect(url_for('video_feed', video_source=filepath, save_video=request.form.get('save_video'), batch_size=request.form.get('batch_size')))

def gen_frames(video_source, save_video, batch_size):
    cap = cv2.VideoCapture(video_source)

    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
    # Video writer
    
    region_points = [(400, 250), (450, 320), (1250, 280), (1000, 220)]

    # Init Object Counter
    counter = solutions.ObjectCounter(
        view_img=True,
        reg_pts=region_points,
        classes_names=model.names,
        draw_tracks=True,
        line_thickness=2,
    )
    
    frame_width = w
    frame_height = h
    size = (frame_width, frame_height)

    #if save_video:
    video_writer = cv2.VideoWriter("object_counting_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    
    co = 0
    while True:
        success, im0 = cap.read()
        if not success:
            break
        tracks = model.track(im0, persist=True, show=False)
        im0 = counter.start_counting(im0, tracks)
        video_writer.write(im0)

        ret, buffer = cv2.imencode('.jpg', im0)
        im0 = buffer.tobytes()

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + im0 + b'\r\n')

        
        
        if co == 10:
            if video_writer:
                video_writer.release()
            cap.release()
            
            # Redirect to main page after processing ends
            return redirect('/')
        
        co += 1
        



# Video feed route
@app.route('/video_feed')
def video_feed():
    video_source = request.args.get('video_source', default=0, type=str)
    save_video = request.args.get('save_video', default=0, type=int)
    batch_size = 1  # Hardcoded batch size for simplicity
    return Response(gen_frames(video_source, save_video, batch_size),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
