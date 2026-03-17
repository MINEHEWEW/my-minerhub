from flask import Flask, render_template, request, jsonify, send_from_directory
import os, shutil, re, json

app = Flask(__name__)

# Папки
UPLOAD_FOLDER, ADDONS_FOLDER, META_FOLDER = 'uploads', 'addons', 'metadata'
for f in [UPLOAD_FOLDER, ADDONS_FOLDER, META_FOLDER]: 
    os.makedirs(f, exist_ok=True)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if data.get('login') == '1234' and data.get('password') == '1234':
        return jsonify({"role": "admin"})
    return jsonify({"err": "Error"}), 401

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    name, desc = request.form.get('name', 'Без названия'), request.form.get('desc', '---')
    if file:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        meta = {"name": name, "desc": desc, "file": filename}
        with open(os.path.join(META_FOLDER, filename + '.json'), 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False)
        return jsonify({"ok": True})
    return jsonify({"err": "No file"}), 400

@app.route('/api/addons/list')
def get_addons():
    files = os.listdir(ADDONS_FOLDER)
    result = []
    for f in files:
        meta_p = os.path.join(META_FOLDER, f + '.json')
        if os.path.exists(meta_p):
            with open(meta_p, 'r', encoding='utf-8') as m: result.append(json.load(m))
        else: result.append({"name": f, "desc": "Без описания", "file": f})
    return jsonify({"files": result})

@app.route('/api/admin/queue')
def get_queue():
    files = os.listdir(UPLOAD_FOLDER)
    result = []
    for f in files:
        meta_p = os.path.join(META_FOLDER, f + '.json')
        if os.path.exists(meta_p):
            with open(meta_p, 'r', encoding='utf-8') as m: result.append(json.load(m))
    return jsonify({"files": result})

@app.route('/api/admin/approve/<filename>', methods=['POST'])
def approve(filename):
    shutil.move(os.path.join(UPLOAD_FOLDER, filename), os.path.join(ADDONS_FOLDER, filename))
    return jsonify({"ok": True})

@app.route('/api/admin/delete/<filename>', methods=['DELETE'])
def delete(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    mp = os.path.join(META_FOLDER, filename + '.json')
    if os.path.exists(mp): os.remove(mp)
    return jsonify({"ok": True})

@app.route('/download/<name>')
def download(name): return send_from_directory(ADDONS_FOLDER, name)

@app.route('/api/admin/preview/<name>')
def preview(name): return send_from_directory(UPLOAD_FOLDER, name)

@app.route('/api/deobfuscate', methods=['POST'])
def deobf():
    code = request.json.get('code', '')
    code = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), code)
    code = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), code)
    return jsonify({"result": code})

if __name__ == '__main__': app.run(debug=True, port=5000)

