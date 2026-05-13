import uvicorn
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from database import engine
from models import Base
from routers import auth, duty, upload, admin, admin_web
from tasks.scheduler import start_scheduler, stop_scheduler

app = FastAPI()


Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(duty.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(upload.router)
app.include_router(admin.router)
app.include_router(admin_web.router)

# 启动和关闭定时任务
@app.on_event("startup")
def on_startup():
    start_scheduler()
    print("启动定时任务")
@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()
    print("关闭定时任务")
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
