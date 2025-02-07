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

        # ✅ Convert all images to JPEG to ensure compatibility
        image = image.convert("RGB")

        # ✅ Resize large images (Prevent memory errors)
        max_width = 1920
        if image.width > max_width:
            aspect_ratio = image.height / image.width
            new_height = int(aspect_ratio * max_width)
            image = image.resize((max_width, new_height), Image.ANTIALIAS)

        # ✅ Save without metadata
        image.save(output_path, format='JPEG')

    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        raise  # Re-throw error for debugging


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

            # ✅ Ensure output image exists
            if not os.path.exists(output_path):
                raise Exception("Processed image not created!")

            metadata_after = {key: "Removed" for key in metadata_before}

            return jsonify({
                "image_url": url_for('get_processed_file', filename="cleaned_" + filename, _external=True),
                "metadata_after": metadata_after
            })
        except Exception as e:
            print(f"Error processing image: {e}")  # ✅ Log error
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    return jsonify({"error": "No file uploaded!"}), 400


@app.route('/processed/<filename>')
def get_processed_file(filename):
    """ Serve cleaned images to frontend """
    return send_file(os.path.join(PROCESSED_FOLDER, filename))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)  # ✅ Ensure it works on Render
