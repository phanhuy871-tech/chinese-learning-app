from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database.repository import repository
from app.games.registry import list_game_metadata

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    # Route trang chủ: render file home.html và truyền dữ liệu ban đầu cho Jinja.
    # Các dữ liệu động sau đó như từ vựng/game sẽ được JavaScript gọi qua API.
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "lessons": repository.list_lessons(),
            "words_count": len(repository.list_words()),
            "sentences_count": len(repository.list_sentences()),
            "grammar_count": len(repository.list_grammar_points()),
            "game_types": list_game_metadata(),
        },
    )
