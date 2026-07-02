from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.exceptions import DataSyncError
from app.data_sources.bootstrap import load_sample_data
from app.data_sources.google_sheets.sync_service import sync_google_sheet
from app.data_sources.local_snapshot import load_local_snapshot
from app.web.routes import router as web_router


def create_app() -> FastAPI:
    """Tạo ứng dụng FastAPI chính.

    File này là điểm bắt đầu của backend. Uvicorn chạy `app.main:app`, rồi FastAPI
    gắn static file, API JSON và trang HTML vào cùng một ứng dụng web.
    """
    # Tạo đối tượng FastAPI chính. Mọi route/API của app sẽ được gắn vào đây.
    app = FastAPI(title=settings.app_name)

    # Cho phép trình duyệt đọc file CSS/JS trong thư mục static.
    app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

    # api_router: các API trả JSON cho frontend.
    # web_router: các trang HTML người dùng nhìn thấy.
    app.include_router(api_router)
    app.include_router(web_router)

    @app.on_event("startup")
    def startup() -> None:
        # Khi app khởi động, nếu tắt sync thì nạp dữ liệu mẫu để app vẫn chạy được.
        if not settings.sync_on_startup:
            load_sample_data()
            return

        # Thứ tự nạp dữ liệu:
        # 1. Đọc Google Sheet online.
        # 2. Nếu Google Sheet riêng tư/không đọc được, dùng snapshot local trong data/local.
        # 3. Nếu không có snapshot local, dùng dữ liệu mẫu trong code.
        try:
            sync_google_sheet()
        except DataSyncError:
            if not load_local_snapshot():
                load_sample_data()

    return app


app = create_app()
