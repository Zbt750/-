import os
from database import SessionLocal
from models import DutyRecord, Notification
from datetime import date
db = SessionLocal()
today = date.today()
print("=" * 40)
print("🧹 开始清理数据...")
# 1. 清空通知表
noti_count = db.query(Notification).delete()
print(f"✅ 已删除 {noti_count} 条通知记录")
# 2. 删除所有值日记录
record_count = db.query(DutyRecord).delete()
print(f"✅ 已删除 {record_count} 条值日记录")
db.commit()
# 3. 删除所有图片文件
upload_dir = "static/uploads"
if os.path.exists(upload_dir):
    file_count = 0
    for f in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
            file_count += 1
    print(f"✅ 已删除 {file_count} 个图片文件")
db.close()
print("=" * 40)
print("📋 正在重新生成今天的记录...")
# 4. 重新生成今天的记录
from tasks.scheduler import generate_daily_records
generate_daily_records()
print("=" * 40)
print("🎉 全部清理完成！现在可以重新打卡测试了")