from pydantic import BaseModel
from typing import Optional

#创建学生用户的登录模型
class LoginRequest(BaseModel):
    name: str
    student_id: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    class_id: int
    is_admin: bool



#上传照片
class CheckInRequest(BaseModel):
    record_id: int
    watermark_url: str
    base64_data: Optional[str] = None

#管理员评价
class AdminEvaluationRequest(BaseModel):
    record_id: int
    is_unqualified: bool
    reason: Optional[str]=None
    unqualified_photos: Optional[str]=None