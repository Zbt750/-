from datetime import datetime

from sqlalchemy import select

from models import Student, Class, DutyRecord, AdminScope, Notification


#创建处理登录学生的信息查验
def check_student_info(student_id, name, db):
    stm=select(Student).where(Student.student_id==student_id, Student.name==name)
    result=db.execute(stm)
    return result.scalar_one_or_none()
#创建处理是否是管理员
def check_admin(student_id,class_id, db):
    try:
        stm=select(AdminScope).where( AdminScope.user_id==student_id)
        result=db.execute(stm)
        admin_record=result.scalar_one_or_none()
        return admin_record is not None
    except Exception:
        return False

#根据学生id查找学生
def get_student_by_id(student_id, db):
    stm=select(Student).where(Student.id==student_id)
    result=db.execute(stm)
    return result.scalar_one_or_none()

#根据class_id去查找class
def get_class_by_id(class_id, db):
    stm=select(Class).where(Class.id==class_id)
    result=db.execute(stm)
    return result.scalar_one_or_none()

#根据class去查找对应的班级值日任务记录
def get_duty_records_by_class(class_id, date, db):
    stmt = select(DutyRecord).where(DutyRecord.class_id == class_id, DutyRecord.record_date == date)
    result = db.execute(stmt)
    return result.scalars().all()   # 返回列表

def get_duty_record_by_class(class_id, date, db):
    stm = select(DutyRecord).where(DutyRecord.class_id == class_id, DutyRecord.record_date == date)
    result = db.execute(stm)
    return result.scalar_one_or_none()   # 返回单个对象或 None




#根据请求题record_id去找值日记录
def get_duty_record_by_id(record_id, db):
    stm=select(DutyRecord).where(DutyRecord.id==record_id)
    result=db.execute(stm)
    return result.scalar_one_or_none()


#添加值日记录
def submit_duty_record(
   record, student_id, watermark_url, db
):
    record.student_id = student_id
    record.photo_url = watermark_url
    record.upload_time = datetime.now()
    db.commit()
    return  record

#通过管理员去查询其管理的所有班级id
def get_admin_class_id(class_ids,today, db):
    stm=select(DutyRecord, Class).join(Class, DutyRecord.class_id==Class.id).where(
        DutyRecord.class_id.in_(class_ids),
        DutyRecord.record_date==today
    )
    result=db.execute(stm).all()
    return [record[1] for record in result]

#根据学生id查找通知
def get_notifications_by_student_id(student_id, db):
    stm=select(Notification).where(Notification.user_id==student_id).order_by(Notification.created_at.desc())
    result=db.execute(stm)
    return result.scalars().all()

