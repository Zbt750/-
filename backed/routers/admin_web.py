import io
from fastapi import APIRouter, HTTPException, Request, Depends, UploadFile
from fastapi.params import Form, File
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Class, Student, AdminScope
from jinja2 import Environment, FileSystemLoader

# ========== 创建 Jinja2 环境（完全绕过 Starlette 的模板缓存） ==========
env = Environment(
    loader=FileSystemLoader("templates"),
    auto_reload=False
)


def render(template_name: str, **context) -> HTMLResponse:
    """渲染模板为 HTML 字符串并返回"""
    template = env.get_template(template_name)
    html = template.render(**context)
    return HTMLResponse(html)


router = APIRouter(prefix="/admin/web", tags=["超级管理员后台"])

# ========== 辅助函数：简易认证 ==========
SUPER_ADMIN_PASSWORD = "admin123"


def check_super_admin(password: str):
    if password != SUPER_ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="密码错误")
    return True


# ========== 班级管理 ==========
@router.get("/classes", response_class=HTMLResponse)
def list_classes(request: Request, db: Session = Depends(get_db)):
    classes = db.query(Class).all()
    return render("classes.html", request=request, classes=classes)


@router.post("/classes/add")
def add_class(
        name: str = Form(...),
        duty_location: str = Form(...),
        duty_start_time: str = Form(...),
        duty_end_time: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db),
):
    check_super_admin(password)
    cls = Class(
        name=name,
        duty_location=duty_location,
        duty_start_time=duty_start_time,
        duty_end_time=duty_end_time
    )
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return RedirectResponse(url="/admin/web/classes", status_code=303)


@router.post("/classes/delete/{class_id}")
def delete_class(class_id: int, password: str = Form(...), db: Session = Depends(get_db)):
    check_super_admin(password)
    cls = db.query(Class).filter(Class.id == class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    db.delete(cls)
    db.commit()
    return RedirectResponse(url="/admin/web/classes", status_code=303)


# ========== 学生管理 ==========
@router.get("/students", response_class=HTMLResponse)
def list_students(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    classes = db.query(Class).all()
    return render("students.html", request=request, students=students, classes=classes)


@router.post("/students/import")
async def import_students(
        file: UploadFile = File(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    check_super_admin(password)

    contents = await file.read()
    import openpyxl
    workbook = openpyxl.load_workbook(io.BytesIO(contents))
    sheet = workbook.active

    success_count = 0
    error_count = 0
    errors = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        try:
            student_id, name, class_name = str(row[0]), str(row[1]), str(row[2])
            cls = db.query(Class).filter(Class.name == class_name).first()
            if not cls:
                errors.append(f"班级 {class_name} 不存在")
                error_count += 1
                continue
            student = Student(
                openid=f"import_{student_id}",
                student_id=student_id,
                name=name,
                class_id=cls.id
            )
            db.add(student)
            success_count += 1
        except Exception as e:
            errors.append(f"导入学生 {row[0]} 失败：{e}")
            error_count += 1

    db.commit()

    # 直接返回简单的 HTML 结果页（不用模板）
    result_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>导入结果</title></head>
    <body>
        <h1>📊 导入结果</h1>
        <p>成功：{success_count} 条</p>
        <p>失败：{error_count} 条</p>
        {"<h3>错误详情：</h3><ul>" + "".join(f"<li>{err}</li>" for err in errors) + "</ul>" if errors else ""}
        <a href="/admin/web/students">返回学生管理</a>
    </body>
    </html>
    """
    return HTMLResponse(result_html)


# ========== 管理员分配 ==========
@router.get("/admins", response_class=HTMLResponse)
def list_admins(request: Request, db: Session = Depends(get_db)):
    students = db.query(Student).all()
    classes = db.query(Class).all()
    admin_scopes = db.query(AdminScope).all()

    admin_list = []
    for scope in admin_scopes:
        student = db.query(Student).filter(Student.id == scope.user_id).first()
        cls = db.query(Class).filter(Class.id == scope.class_id).first()
        if student and cls:
            admin_list.append({
                "student_name": student.name,
                "id": scope.id,
                "class_name": cls.name,
                "student_id_num": student.student_id,
            })
    return render("admins.html", request=request, students=students, classes=classes, admins=admin_list)


@router.post("/admins/add")
def add_admin(
        student_id: int = Form(...),
        class_id: int = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    check_super_admin(password)
    existing = db.query(AdminScope).filter(
        AdminScope.user_id == student_id,
        AdminScope.class_id == class_id
    ).first()
    if existing:
        return RedirectResponse(url="/admin/web/admins?error=已存在", status_code=303)

    scope = AdminScope(user_id=student_id, class_id=class_id)
    db.add(scope)
    db.commit()
    return RedirectResponse(url="/admin/web/admins", status_code=303)


@router.post("/admins/delete/{scope_id}")
def delete_admin(scope_id: int, password: str = Form(...), db: Session = Depends(get_db)):
    check_super_admin(password)
    scope = db.query(AdminScope).filter(AdminScope.id == scope_id).first()
    if not scope:
        return RedirectResponse(url="/admin/web/admins?error=管理员不存在", status_code=303)
    db.delete(scope)
    db.commit()
    return RedirectResponse(url="/admin/web/admins", status_code=303)