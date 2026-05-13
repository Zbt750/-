# reset_data.py
from database import SessionLocal
from models import DutyRecord, Notification
from datetime import date, datetime

today = date.today()
db = SessionLocal()

# 1. 清空通知表（旧通知没用了）
db.query(Notification).delete()

# 2. 重置值日记录
records = db.query(DutyRecord).all()
for r in records:
    r.record_date = today
    r.student_id = None           # 清空打卡学生
    r.photo_url = None            # 清空照片
    r.upload_time = None          # 清空上传时间
    r.is_unqualified = False      # 重置为合格
    r.unqualified_reason = None   # 清空不合格原因
    r.unqualified_photos = None   # 清空证据照片
    r.admin_id = None             # 清空评价管理员
    r.last_edit_time = None       # 清空评价时间
    r.is_fixed = False            # 解锁记录

db.commit()
db.close()

print(f"✅ 已重置 {len(records)} 条值日记录，日期改为 {today}")
print("✅ 已清空所有通知记录")
print("现在所有记录都是「未打卡、未评价」的初始状态")