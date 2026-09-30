from pathlib import Path

from app.config import PANELS_DIR

from app.schemas import (
    PanelOutline,
    PanelStory,
    PromptRequest
)

from app.services.exporters import save_pdf
from app.services.layout_builder import (
    build_comic_layout
)


def test_prompt_validation():

    request = PromptRequest(
        story_prompt=(
            "A fox explores "
            "a magical forest."
        ),

        character_name="Fenn",

        setting="forest",

        tone="funny",

        art_style="comic book"
    )

    assert request.character_name == "Fenn"


def test_layout_builder():

    outline = [
        PanelOutline(
            panel_number=1,
            title="Start",
            scene_description="A start",
            image_prompt="A fox"
        )
    ]

    story = [
        PanelStory(
            panel_number=1,
            caption="Go!",
            narration="Fenn walks.",
            dialogue=["Hello!"]
        )
    ]

    layout = build_comic_layout(
        outline,
        story,
        [
            "/static/panels/one.png"
        ]
    )

    assert layout[0]["title"] == "Start"

    assert layout[0]["dialogue"] == [
        "Hello!"
    ]


def test_pdf_export():

    from PIL import Image

    image = (
        PANELS_DIR /
        "test_export.png"
    )

    Image.new(
        "RGB",
        (100, 100),
        "white"
    ).save(image)


    layout = [
        {
            "panel_number": 1,
            "title": "Test",
            "image_path": (
                "/static/panels/"
                "test_export.png"
            ),
            "scene_description": (
                "A test scene."
            ),
            "caption": "Test caption",
            "narration": "Test narration",
            "dialogue": ["Hello!"]
        }
    ]


    result = save_pdf(
        layout,
        "Test Comic"
    )


    path = (
        Path(__file__).resolve().parents[1]
        / result.lstrip("/")
    )


    assert path.exists()

    assert path.stat().st_size > 0


    path.unlink(
        missing_ok=True
    )

    image.unlink(
        missing_ok=True
    )