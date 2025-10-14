import os
import socket
import zipfile
import qrcode
from flask import Flask, request, render_template_string, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Save files to Desktop/uploads
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
UPLOAD_FOLDER = os.path.join(DESKTOP, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Get local IP ---
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

LOCAL_IP = get_local_ip()

# --- Generate QR Code for URL ---
SERVER_URL = f"http://{LOCAL_IP}:5000"
QR_PATH = os.path.join(UPLOAD_FOLDER, "server_qr.png")

if not os.path.exists(QR_PATH):
    qr = qrcode.make(SERVER_URL)
    qr.save(QR_PATH)

# --- HTML Templates ---
HOME_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Golden Drop 🚀</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a1a; color: gold; text-align: center; margin: 0; }
    h1 { font-size: 2.5em; margin-top: 30px; }
    h2 { font-size: 1.8em; margin-bottom: 15px; }
    .card { background: #2a2a2a; padding: 40px; margin: 30px auto; border-radius: 20px; width: 70%; max-width: 600px; box-shadow: 0 0 20px rgba(255,215,0,0.4); }
    input[type=file] { margin: 15px 0; font-size: 1.1em; color: white; }
    button, input[type=submit], a.button {
      display: inline-block;
      background: linear-gradient(45deg, gold, #ffcc00);
      border: none;
      padding: 14px 30px;
      margin: 12px;
      font-size: 1.1em;
      border-radius: 12px;
      cursor: pointer;
      color: black;
      font-weight: bold;
      text-decoration: none;
      transition: all 0.3s ease-in-out;
    }
    button:hover, input[type=submit]:hover, a.button:hover {
      background: linear-gradient(45deg, #ffdb4d, gold);
      transform: scale(1.05);
      box-shadow: 0 0 10px gold;
    }
    img.qr { margin: 15px; border: 4px solid gold; border-radius: 12px; }
    small { display: block; margin-top: 10px; font-size: 1em; color: #ffdb4d; }
  </style>
</head>
<body>
  <h1>✨ Golden Drop ✨</h1>
  
  <div class="card">
    <h2>📱 Connect Your Phone</h2>
    <p>Scan this QR with your phone camera:</p>
    <img src="/qr" width="250" class="qr"><br>
    <small>{{server_url}}</small>
  </div>

  <div class="card">
    <h2>⬆️ Upload Files</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
      <input type="file" name="files" multiple>
      <br>
      <input type="submit" value="Upload Files">
    </form>
    
    <h2>⬆️ Upload Folder (as Zip)</h2>
    <form method="POST" action="/upload_zip" enctype="multipart/form-data">
      <input type="file" name="zipfile" accept=".zip">
      <br>
      <input type="submit" value="Upload Zip">
    </form>
  </div>

  <div class="card">
    <h2>⬇️ Download Files</h2>
    <a class="button" href="/files">Browse Files</a>
  </div>
</body>
</html>
"""

FILES_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Golden Drop Files</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a1a; color: gold; text-align: center; }
    h1 { margin-top: 30px; font-size: 2.2em; }
    ul { list-style: none; padding: 0; }
    li { margin: 12px 0; font-size: 1.2em; }
    a { color: gold; text-decoration: none; font-weight: bold; }
    a:hover { text-decoration: underline; }
    .back { display: inline-block; margin-top: 20px; background: linear-gradient(45deg, gold, #ffcc00); padding: 12px 25px; border-radius: 12px; color: black; font-weight: bold; text-decoration: none; }
    .back:hover { background: linear-gradient(45deg, #ffdb4d, gold); transform: scale(1.05); box-shadow: 0 0 10px gold; }
  </style>
</head>
<body>
  <h1>📂 Files in Uploads</h1>
  <ul>
    {% for f in files %}
      <li><a href="/download/{{f}}" download>{{f}}</a></li>
    {% endfor %}
  </ul>
  <a href="/" class="back">⬅ Back Home</a>
</body>
</html>
"""

SUCCESS_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <title>Upload Success</title>
  <style>
    body { font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a1a; color: gold; text-align: center; }
    h1 { margin-top: 40px; font-size: 2em; }
    a { display: inline-block; margin-top: 25px; background: linear-gradient(45deg, gold, #ffcc00); padding: 12px 25px; border-radius: 12px; color: black; font-weight: bold; text-decoration: none; }
    a:hover { background: linear-gradient(45deg, #ffdb4d, gold); transform: scale(1.05); box-shadow: 0 0 10px gold; }
  </style>
</head>
<body>
  <h1>✅ {{message}}</h1>
  <a href="/">⬅ Back Home</a>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def index():
    return render_template_string(HOME_PAGE, server_url=SERVER_URL)

@app.route('/qr')
def qr():
    return send_from_directory(UPLOAD_FOLDER, "server_qr.png")

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_files = request.files.getlist("files")
    saved = []
    for file in uploaded_files:
        if file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            saved.append(filename)
    return render_template_string(SUCCESS_PAGE, message=f"Uploaded {len(saved)} file(s)")

@app.route('/upload_zip', methods=['POST'])
def upload_zip():
    zip_file = request.files["zipfile"]
    if zip_file.filename.endswith(".zip"):
        zip_path = os.path.join(UPLOAD_FOLDER, secure_filename(zip_file.filename))
        zip_file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(UPLOAD_FOLDER)
        os.remove(zip_path)
        return render_template_string(SUCCESS_PAGE, message="Zip extracted successfully!")
    return render_template_string(SUCCESS_PAGE, message="Invalid file type!")

@app.route('/files')
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(FILES_PAGE, files=files)

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
