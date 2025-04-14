from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import base64
import uuid
import piexif
from flask_cors import CORS
from PIL import Image, ExifTags

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Enable CORS for all routes and origins

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
        print(f"Opening image: {input_path}")  # Debugging
        image = Image.open(input_path)
        data = list(image.getdata())
        print(f"Image data loaded successfully.")  # Debugging

        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        print(f"Image without EXIF created.")  # Debugging

        # Ensure correct format
        image_format = image.format if image.format else 'JPEG'
        if image_format not in ['JPEG', 'PNG']:
            image_format = 'JPEG'  # Default to JPEG if unsupported format
        print(f"Image format determined: {image_format}")  # Debugging

        image_without_exif.save(output_path, format=image_format)
        print(f"✅ Cleaned image saved at: {output_path}")  # Debugging

    except Exception as e:
        print(f"❌ Error processing {input_path}: {e}")  # Debugging
        raise e


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico')


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
            print(f"✅ File saved at: {input_path}")  # Debugging

            metadata_before = extract_metadata(input_path)
            print(f"Metadata before cleaning: {metadata_before}")  # Debugging

            remove_metadata(input_path, output_path)

            if not os.path.exists(output_path):
                print(f"❌ Error: Processed file was not created at {output_path}!")  # Debugging
                return jsonify({"error": "File processing failed!"}), 500

            metadata_after ="Metadata removed successfully with Lossless compression."

            return jsonify({
                "image_url": url_for('get_processed_file', filename="cleaned_" + filename, _external=True),
                "metadata_after": metadata_after
            })
        except Exception as e:
            print(f"❌ Server error: {e}")  # Debugging
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    return jsonify({"error": "No file uploaded!"}), 400


@app.route('/processed/<filename>')
def get_processed_file(filename):
    """ Serve cleaned images to frontend with a download prompt """
    file_path = os.path.join(PROCESSED_FOLDER, filename)
    print(f"Looking for file at: {file_path}")  # Debugging
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,  # This forces the browser to download the file
            download_name=filename  # Suggests the filename for the download
        )
    print(f"❌ Error: File {filename} not found at {file_path}!")  # Debugging
    return jsonify({"error": "File not found!"}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)  # ✅ Ensure it works on Render
