from datetime import date, datetime
from fastapi import Request, Header
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from models import Notification
from crud import get_student_by_id, get_class_by_id, get_duty_record_by_class, get_duty_record_by_id, \
    submit_duty_record, get_notifications_by_student_id
from database import get_db
from routers.admin import oauth2_scheme
from untils import  decode_access_token
from schemas import CheckInRequest

#获取登录用户的值日任务
#先获取该学生的token，然后从token里面查找该学生的班级，以及班级对应的值日任务
router=APIRouter(prefix="/duty", tags=["duty"])
student_token=OAuth2PasswordBearer(tokenUrl="auth/login")
#查找token
def get_token(request: Request, db: Session = Depends(get_db)):
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供token或格式错误")
    token = authorization.split(" ")[1]
    print("手动获取到的token:", token)
    print("token类型:", type(token))
    check_token = decode_access_token(token)
    if not check_token:
        raise HTTPException(status_code=400, detail="token失效")
    user_id = int(check_token.get("sub"))
    student = get_student_by_id(user_id, db)
    if not student:
        raise HTTPException(status_code=400, detail="用户不存在")
    return student
#值日任务的路由：先查找学生班级，然后根据班级查找值日任务
@router.get("/duty_task")
def get_duty_task(student=Depends(get_token), db: Session = Depends(get_db)):
    try:
        today = date.today()
        class_ = get_class_by_id(student.class_id, db)
        if not class_:
            raise HTTPException(status_code=400, detail="班级不存在")

        # 打印查询参数
        print(f"查询班级 {class_.id} 日期 {today} 的值日记录")

        record = get_duty_record_by_class(class_.id, today, db)
        print(f"查询结果 record: {record}")

        if not record:
            return {
                "has_task": False,
                "start_time": class_.duty_start_time,
                "end_time": class_.duty_end_time,
                "location": class_.duty_location,
                "status": "未打卡",
                "is_checked_in": False,
                "record_id": None
            }

        is_checked = record.student_id is not None
        is_evaluated = record.admin_id is not None
        evaluation = None
        if is_evaluated:
            evaluation = "合格" if not record.is_unqualified else "不合格"
        else:
            evaluation = "未评价"

        return {
            "has_task": True,
            "start_time": class_.duty_start_time,
            "end_time": class_.duty_end_time,
            "location": class_.duty_location,
            "status": evaluation,
            "is_checked_in": is_checked,
            "record_id": record.id
        }
    except Exception as e:
        print("发生异常:", repr(e))
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))






#提交水印照片并且打卡
@router.post("/submit_watermark")
def submit_watermark(req: CheckInRequest, student=Depends(get_token), db: Session = Depends(get_db)):
    record = get_duty_record_by_id(req.record_id, db)
    if not record:
        raise HTTPException(status_code=400, detail="值日记录不存在")
    if record.student_id:
        raise HTTPException(status_code=400, detail="该值日任务已提交")

    # 保存打卡信息，同时保存 base64
    record.student_id = student.id
    record.photo_url = req.watermark_url
    record.photo_base64 = req.base64_data  # ← 新增：保存 base64
    record.upload_time = datetime.now()
    db.commit()

    return {"message": "提交成功"}

# ========== 学生获取自己的通知列表 ==========
@router.get("/notifications")
def get_notifications(authorization: str = Header(None),
    db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供token")

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效token")

    user_id = int(payload.get("sub"))
    student = get_student_by_id(user_id, db)
    if not student:
        raise HTTPException(status_code=404, detail="用户不存在")
    notifications=get_notifications_by_student_id(student.id, db)
    return {
        "notifications": [
            {
                "id": n.id,
                "record_id": n.record_id,
                "title": n.title,
                "content": n.content,
                "is_read": n.is_read,
                "created_at": n.created_at.strftime("%Y-%m-%d %H:%M")
            }
            for n in notifications
        ]
    }
# ========== 标记通知已读 ==========
@router.post("/notifications/read")
def mark_notification_as_read(notification_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供token")

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效token")
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == int(payload.get("sub"))
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="通知不存在")
    notification.is_read = True
    db.commit()
    return {"message": "标记成功"}




