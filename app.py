from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import base64
import uuid
import piexif
from PIL import Image

app = Flask(__name__)

# Configure Upload Folders
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)


def extract_metadata(image_path):
    """ Extract metadata from an image file. """
    try:
        exif_data = piexif.load(image_path)
        if not exif_data:
            return {"Error": "No EXIF metadata found"}

        metadata = {}
        for ifd in exif_data:
            for tag in exif_data[ifd]:
                tag_name = piexif.TAGS[ifd][tag]["name"]
                tag_value = exif_data[ifd][tag]
                
                if isinstance(tag_value, bytes):
                    tag_value = base64.b64encode(tag_value).decode('utf-8')
                
                metadata[tag_name] = tag_value

        return metadata
    except Exception:
        return {"Error": "No metadata found"}


def remove_metadata(input_path, output_path):
    """ Remove metadata and save a clean image. """
    try:
        image = Image.open(input_path)
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        image_without_exif.save(output_path, format='JPEG')  # ✅ Fix: Save Image as JPEG without EXIF
    except Exception as e:
        print(f"Error processing {input_path}: {e}")


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/clean', methods=['POST'])
def clean_image():
    uploaded_file = request.files['image']
    
    if uploaded_file:
        unique_id = uuid.uuid4().hex
        filename = unique_id + "_" + uploaded_file.filename
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_path = os.path.join(PROCESSED_FOLDER, "cleaned_" + filename)

        uploaded_file.save(input_path)

        metadata_before = extract_metadata(input_path)
        remove_metadata(input_path, output_path)
        metadata_after = {key: 0 for key in metadata_before}  # ✅ Fix: Set all values to 0

        return jsonify({
            "image_url": url_for('get_processed_file', filename="cleaned_" + filename),
            "metadata_after": metadata_after
        })

    return jsonify({"error": "No file uploaded!"})


@app.route('/processed/<filename>')
def get_processed_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename))


if __name__ == '__main__':
    app.run(debug=True)
