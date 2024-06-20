from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import os
import sys

sys.path.append(os.path.abspath('../repos/yolov7'))
sys.path.append(os.path.abspath('./utils'))
from hubconf import custom
from processing import color_map, clasess, draw_boxes     

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load model
model = custom(path_or_model='./models/best_yolov7.pt')

def model_infer(img):
    results = model(img)
    xywh = results.xywh[0].numpy()
    draw_boxes(img, xywh)
    return img

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
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    size = (frame_width, frame_height)

    if save_video:
        out = cv2.VideoWriter('./static/output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 20, size)
    
    batch_frames = []
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Collect frames in batches
            batch_frames.append(frame)
            if len(batch_frames) == batch_size:
                # Process batch
                processed_batch = [model_infer(f) for f in batch_frames]
                
                for frame in processed_batch:
                    if save_video:
                        out.write(frame)

                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame = buffer.tobytes()

                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
                batch_frames = []

    # Process remaining frames in batch
    if batch_frames:
        processed_batch = [model_infer(f) for f in batch_frames]
        for frame in processed_batch:
            if save_video:
                out.write(frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    
    cap.release()
    if save_video:
        out.release()

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
