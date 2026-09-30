import uuid
from dataclasses import dataclass

from app.config import settings

from app.schemas import (
    PanelOutline,
    PanelStory,
    PromptRequest
)

from app.services.exporters import save_pdf
from app.services.gemini_flash import generate_outline
from app.services.gemini_pro import generate_story
from app.services.image_generator import generate_image
from app.services.layout_builder import build_comic_layout


@dataclass
class GeneratedComic:

    comic_id: str
    title: str
    layout: list[dict]
    pdf_url: str


def _mock_outline(
    request: PromptRequest
) -> list[PanelOutline]:

    beats = [
        (
            "The Beginning",
            "The hero arrives and notices something unusual.",
            "wide establishing shot"
        ),
        (
            "The Discovery",
            "A surprising clue changes the direction of the adventure.",
            "medium character shot"
        ),
        (
            "The Challenge",
            "The hero faces the central obstacle with courage.",
            "dynamic action shot"
        ),
        (
            "The Turning Point",
            "A clever idea or act of kindness unlocks a solution.",
            "dramatic close-up"
        ),
        (
            "A New Chapter",
            "The adventure ends with a satisfying glimpse of what comes next.",
            "warm cinematic ending shot"
        )
    ]

    return [
        PanelOutline(
            panel_number=index,

            title=title,

            scene_description=(
                f"{description} "
                f"Setting: {request.setting}."
            ),

            image_prompt=(
                f"{request.art_style}, "
                f"{shot}, "
                f"{request.character_name} "
                f"in {request.setting}; "
                f"story beat: {description}; "
                f"consistent character design, "
                f"expressive faces, "
                f"polished comic illustration"
            )
        )

        for index, (
            title,
            description,
            shot
        ) in enumerate(
            beats,
            start=1
        )
    ]


def _mock_story(
    request: PromptRequest,
    outline: list[PanelOutline]
) -> list[PanelStory]:

    captions = [
        "A curious beginning.",
        "Something is waiting.",
        "The moment arrives.",
        "A bright idea.",
        "The journey continues."
    ]

    dialogues = [
        [
            "I wonder what is happening here!",
            "Let's find out."
        ],
        [
            "That clue has to mean something.",
            "I knew this adventure would be unusual."
        ],
        [
            "Stay calm. I can do this!",
            "Here goes!"
        ],
        [
            "Wait... I have an idea.",
            "Sometimes the answer is simpler than it looks."
        ],
        [
            "We did it!",
            "And this is only the beginning."
        ]
    ]

    result = []

    for panel in outline:

        index = panel.panel_number - 1

        result.append(
            PanelStory(
                panel_number=panel.panel_number,

                caption=captions[index],

                narration=(
                    f"{request.character_name} "
                    f"moves through "
                    f"{request.setting}, "
                    f"following the mystery "
                    f"from the previous panel. "
                    f"The {request.tone} mood grows "
                    f"as the adventure unfolds."
                ),

                dialogue=dialogues[index]
            )
        )

    return result


def create_comic(
    request: PromptRequest
) -> GeneratedComic:

    if settings.mock_mode:

        outline = _mock_outline(
            request
        )

        story = _mock_story(
            request,
            outline
        )

    else:

        outline = generate_outline(
            request
        )

        story = generate_story(
            request,
            outline
        )

    images = [
        generate_image(
            panel.image_prompt,
            panel.panel_number
        )
        for panel in outline
    ]

    layout = build_comic_layout(
        outline,
        story,
        images
    )

    title = (
        f"{request.character_name}'s "
        f"{request.setting.title()} Adventure"
    )

    pdf_url = save_pdf(
        layout,
        title=title
    )

    return GeneratedComic(
        comic_id=uuid.uuid4().hex,
        title=title,
        layout=layout,
        pdf_url=pdf_url
    )