# clean_and_reset.py
import os
from database import SessionLocal
from models import DutyRecord, Notification
from datetime import date, timedelta

db = SessionLocal()
today = date.today()

# ===== 1. 删除物理图片文件 =====
upload_dir = "static/uploads"
if os.path.exists(upload_dir):
    count = 0
    for f in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
            count += 1
    print(f"✅ 已删除 {count} 个物理图片文件")

# ===== 2. 清空通知表 =====
noti_count = db.query(Notification).delete()
print(f"✅ 已删除 {noti_count} 条通知记录")

# ===== 3. 删除今天的旧记录（重新生成） =====
old_today = db.query(DutyRecord).filter(DutyRecord.record_date == today).all()
for r in old_today:
    db.delete(r)
print(f"✅ 已删除 {len(old_today)} 条今天的旧记录")

# ===== 4. 为今天生成干净的新记录 =====
from models import Class
classes = db.query(Class).all()
for cls in classes:
    record = DutyRecord(
        class_id=cls.id,
        record_date=today,
        is_unqualified=False,
        is_fixed=False
    )
    db.add(record)
print(f"✅ 已为 {len(classes)} 个班级生成今天的记录")

db.commit()
db.close()
print("🎉 全部清理完成！")