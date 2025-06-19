import os
from PIL import Image
import uuid
import io
import csv

def save_and_compress_image(file, folder="app/static/uploads"):
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(file.filename)[1].lower()
    unique_name = f"{uuid.uuid4().hex}{ext}"
    #filename = file.filename
    #filepath = os.path.join(folder, filename)
    filepath = os.path.join(folder, unique_name)
    with open(filepath, "wb") as buffer:
        buffer.write(file.file.read())
    # ลดขนาดภาพด้วย Pillow
    img = Image.open(filepath)
    img.save(filepath, optimize=True, quality=60)
    return f"uploads/{unique_name}"


def generate_csv(rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["League", "Match","Match Date", "URL", "Status", "Ticket Owner" , "Create Date", "Update By"])
    for row in rows:
        writer.writerow(row)
    yield output.getvalue()