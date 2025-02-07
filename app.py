from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import base64
import uuid
import piexif
from flask_cors import CORS
from PIL import Image, ExifTags

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

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
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return {"Error": "No metadata found"}


def remove_metadata(input_path, output_path):
    """ Remove metadata and save a clean image. """
    try:
        image = Image.open(input_path)
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(image.getdata())

        # ✅ Fix: Ensure the correct format is used
        image_format = image.format if image.format else 'JPEG'
        image_without_exif.save(output_path, format=image_format)
        print(f"✅ Cleaned image saved at: {output_path}")  # ✅ Debugging

    except Exception as e:
        print(f"❌ Error processing {input_path}: {e}")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/clean', methods=['POST'])
def clean_image():
    if 'image' not in request.files:
        return jsonify({"error": "No file uploaded!"}), 400

    uploaded_file = request.files['image']

    if uploaded_file:
        try:
            unique_id = uuid.uuid4().hex
            filename = unique_id + "_" + uploaded_file.filename
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            output_path = os.path.join(PROCESSED_FOLDER, "cleaned_" + filename)

            uploaded_file.save(input_path)

            metadata_before = extract_metadata(input_path)
            remove_metadata(input_path, output_path)

            if not os.path.exists(output_path):
                print("❌ Error: Output file was not created!")  # ✅ Debugging
                return jsonify({"error": "File processing failed!"}), 500

            metadata_after = {key: "Removed" for key in metadata_before}

            return jsonify({
                "image_url": url_for('get_processed_file', filename="cleaned_" + filename, _external=True),
                "metadata_after": metadata_after
            })
        except Exception as e:
            print(f"❌ Server error: {e}")  # ✅ Debugging
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    return jsonify({"error": "No file uploaded!"}), 400


@app.route('/processed/<filename>')
def get_processed_file(filename):
    """ Serve cleaned images to frontend """
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    print(f"❌ Error: File {filename} not found!")  # ✅ Debugging
    return jsonify({"error": "File not found!"}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)  # ✅ Ensure it works on Render
