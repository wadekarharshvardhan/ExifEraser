Image Metadata Remover

A simple and efficient web application to remove metadata (EXIF) from images. It allows users to preview images, view and clean metadata, and download the cleaned image.

Live Website: https://image-meta-remover.onrender.com
Features

    Preview image immediately after selection

    Display original metadata before cleaning

    Remove all metadata from image files

    Display cleaned metadata for transparency

    Download the cleaned image with one click

Getting Started
Clone the Repository

git clone https://github.com/wadekarharshvardhan/image-meta-remover.git
cd image-meta-remover

Set Up Virtual Environment (Optional)

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate

Install Dependencies

pip install -r requirements.txt

Run the Application

python app.py

Visit http://127.0.0.1:5000 in your browser.
Technologies Used

    Flask – Lightweight web framework

    Pillow – Python Imaging Library

    piexif – EXIF metadata manipulation

    uuid – Unique filename generation

License

This project is licensed under the MIT License. See LICENSE for more information.
Author

Harshvardhan Wadekar
GitHub
