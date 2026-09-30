from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse
)

from fastapi.templating import Jinja2Templates

from app.config import (
    EXPORTS_DIR,
    TEMPLATES_DIR,
    settings
)

from app.schemas import PromptRequest

from app.services.comic_service import create_comic
from app.services.image_generator import generate_image


templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)

router = APIRouter()


def _request_from_form(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> PromptRequest:

    try:
        return PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc)
        ) from exc


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    data = _request_from_form(
        story_prompt,
        character_name,
        setting,
        tone,
        art_style
    )

    try:

        comic = create_comic(data)

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "comic": comic,
                "mock_mode": settings.mock_mode
            }
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={
                "error": str(exc)
            },
            status_code=500
        )


@router.post("/generate-comic/json")
async def generate_comic_json(
    payload: PromptRequest
):

    try:

        comic = create_comic(payload)

        return {
            "comic_id": comic.comic_id,
            "title": comic.title,
            "layout": comic.layout,
            "pdf_url": comic.pdf_url
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


@router.get("/download/{filename}")
async def download_pdf(filename: str):

    safe = Path(filename).name

    if safe != filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid PDF filename."
        )

    if not safe.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    path = EXPORTS_DIR / safe

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF not found."
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=safe
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(
    request: Request,
    filename: str | None = None
):

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "filename": filename
        }
    )


@router.get("/test-image")
async def test_image(
    prompt: str = (
        "A friendly fox exploring an enchanted "
        "forest, comic book art"
    )
):

    try:

        image_url = generate_image(
            prompt,
            1
        )

        return {
            "image_url": image_url,
            "prompt": prompt
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc