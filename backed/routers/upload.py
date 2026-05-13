import base64
import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException
from starlette.responses import FileResponse

router=APIRouter(prefix="/upload",tags=["upload"])

UP_LOAD_DIR = "static/uploads"

os.makedirs(UP_LOAD_DIR, exist_ok=True)


#上传水印照片到数据库
@router.post("/upload_watermark")
def upload_watermark(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="请上传文件")
    try:
        # 获取文件扩展名
        ext = file.filename.split(".")[-1]
        # 生成唯一文件名
        filename = f"{uuid.uuid4().hex}.{ext}"
        # 文件保存路径
        filepath = os.path.join(UP_LOAD_DIR, filename)
        # 保存文件
        with open(filepath, "wb") as f:
            shutil.copyfileobj(file.file, f)
        # 读取文件并转为 Base64
        with open(filepath, "rb") as f:
            base64_str = base64.b64encode(f.read()).decode("utf-8")
        # 返回 URL（给浏览器用）和 Base64（给小程序用）
        return {
            "url": f"/upload/images/{filename}",
            "base64": f"data:image/{ext};base64,{base64_str}"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail="文件上传失败")
# 获取上传的图片（自定义接口，给浏览器用）
@router.get("/images/{filename}")
def get_uploaded_image(filename: str):
    file_path = os.path.join(UP_LOAD_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(file_path)