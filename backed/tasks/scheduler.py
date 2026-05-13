from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from database import SessionLocal
from datetime import date, timedelta
from models import Class, DutyRecord

# 每天凌晨生成所以班级的日任务记录
def generate_daily_records():
    db=SessionLocal ()
    try :

        today=date.today ()
        classes=db.query(Class).all()
        for cls in classes:
            existing=db.query(DutyRecord).filter(DutyRecord.class_id==cls.id,DutyRecord.record_date==today).first()
            if not existing:
                record=DutyRecord(class_id=cls.id,record_date=today,is_unqualified=False,is_fixed=False)
                db.add(record)
        db.commit()
        print(f"[定时任务] ✅ 已生成 {len(classes)} 个班级的 {today} 值日记录")
    except Exception as e:
        print(f"[定时任务] ❌ 生成  值日记录失败：{e}")
    finally:
        db.close()

# 固定前一天的值日记录
def fix_previous_day_records():
    db=SessionLocal ()
    try :
        yesterday=date.today()-timedelta(days=1)
        records=db.query(DutyRecord).filter(DutyRecord.record_date==yesterday).all()
        count=0
        for record in records:
            if not record.is_fixed:
                record.is_fixed=True
                count+=1
        db.commit()
        print(f"[定时任务] ✅ 已固定 {count} 个班级的 {yesterday} 值日记录")
    except Exception as e:
        print(f"[定时任务] ❌ 固定  值日记录失败：{e}")
    finally:
        db.close()

# 删除三天前的记录
def delete_three_days_ago_records():
    db=SessionLocal ()
    try :
        three_days_ago=date.today()-timedelta(days=3)
        records=db.query(DutyRecord).filter(DutyRecord.record_date<=three_days_ago).all()
        count=len( records)
        for record in records:
            db.delete(record)
            count-=1
        db.commit()
        print(f"[定时任务] ✅ 已删除 {count} 个班级的 {three_days_ago} 以前的值日记录")
    except Exception as e:
        print(f"[定时任务] ❌ 删除  值日记录失败：{e}")
    finally:
        db.close()

# 生成调度器
scheduler = BackgroundScheduler()
def start_scheduler():
   #     每天凌晨0点生成所有班级的日任务记录
    scheduler.add_job(generate_daily_records,CronTrigger(hour=0, minute=0), id="generate_daily_records", replace_existing=True )
    #     每天0点5分固定前一天的值日记录
    scheduler.add_job(fix_previous_day_records,CronTrigger(hour=0, minute=5), id="fix_previous_day_records", replace_existing=True )
    #     每天0点10分删除三天前的记录
    scheduler.add_job(delete_three_days_ago_records,CronTrigger(hour=0, minute=10), id="delete_three_days_ago_records", replace_existing=True )
    scheduler.start()
    print("[定时任务] ✅ 定时任务已启动")

# 关闭调度器
def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        print("[定时任务] ❌ 定时任务已关闭")







