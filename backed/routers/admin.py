import base64
import os
from datetime import date, datetime
from tabnanny import check

from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from crud import get_student_by_id, check_admin, get_class_by_id, get_duty_record_by_id
from database import get_db
from models import DutyRecord, AdminScope, Class, Notification, Student
from schemas import AdminEvaluationRequest
from untils import decode_access_token

router=APIRouter(prefix="/admin", tags=["admin"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

#获取当前管理员信息
def get_current_admin(
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    if not authorization:
        raise HTTPException(status_code=401, detail="未提供token")

    # 从 "Bearer xxx" 中提取 token
    token = authorization.replace("Bearer ", "")

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效token")

    user_id = int(payload.get("sub"))
    student = db.query(Student).filter(Student.id == user_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 检查是否有管理员权限
    scope = db.query(AdminScope).filter(AdminScope.user_id == student.id).first()
    if not scope:
        raise HTTPException(status_code=403, detail="无管理员权限")

    return student



#实现管理员获取任务



@router.get("/get_admin_tasks")
def get_admin_tasks(current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    today = date.today()
    # 1. 获取当前管理员管辖的所有班级ID
    scopes = db.query(AdminScope.class_id).filter(AdminScope.user_id == current_admin.id).all()
    class_ids = [s[0] for s in scopes]
    if not class_ids:
        return {"tasks": []}

    # 2. 查询这些班级今天的值日记录（顺便 JOIN 班级表获取班级信息）
    stmt = select(DutyRecord, Class).join(Class, DutyRecord.class_id == Class.id).where(
        DutyRecord.class_id.in_(class_ids),
        DutyRecord.record_date == today
    )
    results = db.execute(stmt).all()  # 得到元组列表 [(record, class), ...]

    # 3. 构建返回结果
    task_list = []
    for record, class_ in results:
        if record.admin_id is None:
            status = "未评价"
        elif record.is_unqualified:
            status = "不合格"
        else:
            status = "合格"
        # 在循环里，添加记录时：
        photo_base64 = record.photo_base64  # 先取数据库里存的
        if not photo_base64 and record.photo_url:
            # 如果数据库没有 base64，但有图片 URL，尝试读取文件
            # 注意：这里的 photo_url 可能是 /upload/images/xxx.png 或 /static/uploads/xxx.png
            filename = record.photo_url.split("/")[-1]  # 取文件名
            file_path = os.path.join("static", "uploads", filename)
            if os.path.exists(file_path):
                with open(file_path, "rb") as f:
                    ext = filename.split(".")[-1] or "png"
                    photo_base64 = f"data:image/{ext};base64," + base64.b64encode(f.read()).decode("utf-8")
        task_list.append({
            "record_id": record.id,
            "class_name": class_.name,
            "location": class_.duty_location,
            "has_checked_in": record.student_id is not None,
            "photo_url": record.photo_url,
            "photo_base64":photo_base64,
            "is_evaluated": record.admin_id is not None,
            "status": status
        })
    return {"tasks": task_list}

#实现管理员评价接口
@router.post("/evaluate")
def evaluate(req: AdminEvaluationRequest, current_admin=Depends(get_current_admin), db: Session = Depends(get_db)):
    #查询班级记录
    record=get_duty_record_by_id(req.record_id, db)
    if not record:
        raise HTTPException(status_code=400, detail="值日记录不存在")
    #管理员是否有权限评价
    scope=check_admin(current_admin.id, record.class_id, db)
    if not scope:
        raise HTTPException(status_code=400, detail="无权限评价")
    #更新评价
    record.is_unqualified=req.is_unqualified
    record.admin_id=current_admin.id
    record.unqualified_reason=req.reason
    record.unqualified_photos=req.unqualified_photos
    record.last_edit_time=datetime.now()

    ## ========== 新增：不合格时生成通知 ==========
    if req.is_unqualified:
        notify_user_id = None
        title = ""
        content = ""
        #确定通知的学生
        if record.student_id:
        # 有打卡学生 → 通知该学生
            notify_user_id = record.student_id
            title = "值日不合格通知"
            content = f"您在 {record.record_date} 的值日被判定为不合格。原因：{req.reason}"
        else:
            # 无打卡学生 → 获取班级管理员
            # 无人打卡 → 通知该班级的第一个管理员（生活委员）
            admin_scope = db.query(AdminScope).filter(
                AdminScope.class_id == record.class_id
            ).first()
            if admin_scope:
                admin_student = db.query(Student).filter(
                    Student.id == admin_scope.user_id
                ).first()
                if admin_student:
                    notification = Notification(
                        user_id=admin_student.id,
                        record_id=record.id,
                        title="班级值日未打卡通知",
                        content=f"{record.record_date} 班级值日无人打卡，已被标记为不合格。",
                        is_read=False,
                        created_at=datetime.now()
                    )
                    db.add(notification)

            # 如果有通知对象，创建通知记录
        if record.student_id:
            notification = Notification(
                user_id=notify_user_id,
                record_id=record.id,
                title=title,
                content=content,
                is_read=False,
                created_at=datetime.now()
            )
            db.add(notification)

    db.commit()
    return {"message": "评价成功"}















