Image Metadata Remover

Image Metadata Remover is a simple yet powerful web application that allows users to remove metadata (EXIF) from image files. The application provides a seamless interface to preview, clean, and download images free of any sensitive or identifying metadata.

Live Demo: https://image-meta-remover.onrender.com
Features

    Preview the selected image immediately

    Display all metadata before cleaning

    Remove EXIF metadata with a single click

    Show sanitized metadata after processing

    Download the cleaned image directly

Installation

Follow the steps below to set up and run the application locally:
1. Clone the Repository

git clone https://github.com/wadekarharshvardhan/image-meta-remover.git
cd image-meta-remover

2. Create a Virtual Environment (Optional)

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

4. Run the Application

python app.py

Visit http://127.0.0.1:5000 in your browser to use the application.
Dependencies

The project uses the following Python libraries:
Library	Purpose
Flask	Web framework
Pillow	Image processing
piexif	EXIF metadata manipulation
uuid	Unique file naming
License

This project is licensed under the MIT License. See the LICENSE file for more details.
Author

Harshvardhan Wadekar
GitHub Profile
