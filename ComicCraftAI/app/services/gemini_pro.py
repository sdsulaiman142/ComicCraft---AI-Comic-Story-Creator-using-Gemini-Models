import time

from app.config import settings

from app.schemas import (
    ComicOutline,
    ComicStory,
    PanelStory,
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


def generate_story(
    request: PromptRequest,
    outline
) -> list[PanelStory]:

    if not outline:
        raise ValueError(
            "The comic outline is empty."
        )

    if isinstance(outline[0], dict):

        normalized = ComicOutline(
            panels=outline
        ).model_dump()

    else:

        normalized = {
            "panels": [
                panel.model_dump()
                for panel in outline
            ]
        }

    prompt = f"""
Write the finished narration and dialogue
for a {settings.panel_count}-panel comic.

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

Panel outline:
{normalized}

Requirements:

- Return exactly one story object for every panel.
- Keep panels in the same order.
- Create a short caption.
- Create concise narration.
- Create natural dialogue.
- Keep dialogue short enough for speech bubbles.
- Maintain story continuity.
- Maintain character consistency.
- Do not create additional panels.
"""

    from google.genai import types

    client = _client()

    max_retries = 4

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=settings.gemini_story_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.85,
                    response_mime_type="application/json",
                    response_schema=ComicStory
                )
            )

            story = ComicStory.model_validate_json(
                response.text
            )

            if len(story.panels) != len(outline):

                raise ValueError(
                    "Gemini story response does not "
                    "match the outline panel count."
                )

            return [
                panel.model_copy(
                    update={
                        "panel_number": index
                    }
                )
                for index, panel
                in enumerate(
                    story.panels,
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
                    f"Retrying story generation in "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

                continue

            raise