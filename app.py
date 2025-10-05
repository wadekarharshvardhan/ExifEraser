from flask import Flask, render_template, request, jsonify, send_file, url_for
import os
import base64
import uuid
import piexif
from flask_cors import CORS
from PIL import Image, ExifTags
import tempfile
import io

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Enable CORS for all routes and origins

# Configure Upload Folders for Vercel (use temp directories)
UPLOAD_FOLDER = tempfile.mkdtemp()
PROCESSED_FOLDER = tempfile.mkdtemp()

# Ensure folders exist
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
            # Process image in memory instead of saving to disk
            image_data = uploaded_file.read()
            
            # Extract metadata before cleaning
            with tempfile.NamedTemporaryFile(delete=False) as temp_input:
                temp_input.write(image_data)
                temp_input.flush()
                metadata_before = extract_metadata(temp_input.name)
            
            # Clean the image
            image = Image.open(io.BytesIO(image_data))
            
            # Remove EXIF data
            data = list(image.getdata())
            image_without_exif = Image.new(image.mode, image.size)
            image_without_exif.putdata(data)
            
            # Convert to bytes
            img_io = io.BytesIO()
            image_format = image.format if image.format else 'JPEG'
            if image_format not in ['JPEG', 'PNG']:
                image_format = 'JPEG'
            
            image_without_exif.save(img_io, format=image_format)
            img_io.seek(0)
            
            # Convert to base64 for frontend display
            img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
            image_url = f"data:image/{image_format.lower()};base64,{img_base64}"
            
            metadata_after = "Metadata removed successfully with lossless compression."
            
            # Clean up temp file
            os.unlink(temp_input.name)

            return jsonify({
                "image_url": image_url,
                "metadata_after": metadata_after,
                "filename": f"cleaned_{uploaded_file.filename}"
            })
        except Exception as e:
            print(f"❌ Server error: {e}")
            return jsonify({"error": f"Server error: {str(e)}"}), 500

    return jsonify({"error": "No file uploaded!"}), 400


# Main entry point for Vercel
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=10000)
