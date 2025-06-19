FROM python:3.11-slim

# ตั้ง working directory ใน container
WORKDIR /app

# คัดลอก requirements.txt แล้วติดตั้ง dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโค้ดแอปเข้าไปใน container
COPY ./app ./app
COPY ./templates ./templates

# เปิดพอร์ต 8000 ให้ container รองรับการเชื่อมต่อจากภายนอก
EXPOSE 8000

# ปิด buffering เพื่อให้ log แสดงทันทีใน stdout
ENV PYTHONUNBUFFERED=1

# คำสั่งเริ่มต้นเมื่อ container ถูกรัน
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
