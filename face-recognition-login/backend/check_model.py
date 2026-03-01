from ultralytics import YOLO
model = YOLO('best.pt')
print("\n🎯 รายชื่อสิ่งที่ AI ตัวนี้รู้จัก:", model.names)