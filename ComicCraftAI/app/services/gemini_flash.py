import time

from app.config import settings
from app.schemas import (
    ComicOutline,
    PanelOutline,
    PromptRequest
)


def _client():

    from google import genai

    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _prompt(request: PromptRequest) -> str:

    return f"""
Create a cohesive {settings.panel_count}-panel comic outline.

Story idea:
{request.story_prompt}

Main character:
{request.character_name}

Setting:
{request.setting}

Tone:
{request.tone}

Art style:
{request.art_style}

Requirements:

- Exactly {settings.panel_count} panels.
- Every panel must have a short title.
- Every panel must have a scene description.
- Every panel must have an image-generation prompt.
- Maintain the same character appearance throughout.
- Create a clear beginning, middle and ending.
- Make the story visually interesting.
- Do not put dialogue inside the image prompts.
- Include composition, lighting, camera framing and visual style.
"""


def generate_outline(
    request: PromptRequest
) -> list[PanelOutline]:

    from google.genai import types

    client = _client()

    max_retries = 4

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=settings.gemini_outline_model,
                contents=_prompt(request),
                config=types.GenerateContentConfig(
                    temperature=0.9,
                    response_mime_type="application/json",
                    response_schema=ComicOutline
                )
            )

            outline = ComicOutline.model_validate_json(
                response.text
            )

            if len(outline.panels) != settings.panel_count:

                raise ValueError(
                    f"Gemini returned "
                    f"{len(outline.panels)} panels; "
                    f"expected "
                    f"{settings.panel_count}."
                )

            return [
                panel.model_copy(
                    update={
                        "panel_number": index
                    }
                )
                for index, panel
                in enumerate(
                    outline.panels,
                    start=1
                )
            ]

        except Exception as exc:

            error_text = str(exc)

            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "429" in error_text
            )

            if (
                is_temporary_error
                and attempt < max_retries - 1
            ):

                wait_seconds = 2 ** attempt

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

                continue

            raise