from fastapi import APIRouter, Depends,HTTPException
from sqlalchemy.orm import Session

from crud import check_student_info, check_admin
from database import get_db
from schemas import LoginRequest, LoginResponse
from untils import create_access_token

router=APIRouter(prefix="/auth", tags=["auth"])

#创建登录接口
@router.post("/login")
def login(info: LoginRequest,db:Session = Depends(get_db)):
    student=check_student_info(info.student_id, info.name, db)
    if not student:
        raise HTTPException(status_code=400, detail="用户不存在")
    is_admin=check_admin(student.id, student.class_id, db)
    token=create_access_token(student.id)
    return LoginResponse(access_token=token,
                         token_type="bearer",
                         user_id=student.id,
                         class_id=student.class_id,
                         is_admin=is_admin
                         )


