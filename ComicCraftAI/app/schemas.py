from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        min_length=5,
        max_length=2000
    )

    character_name: str = Field(
        min_length=1,
        max_length=80
    )

    setting: str = Field(
        min_length=1,
        max_length=120
    )

    tone: str = Field(
        min_length=1,
        max_length=60
    )

    art_style: str = Field(
        min_length=1,
        max_length=80
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style"
    )
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = " ".join(value.strip().split())

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=120)
    scene_description: str = Field(
        min_length=1,
        max_length=1000
    )
    image_prompt: str = Field(
        min_length=1,
        max_length=1500
    )


class ComicOutline(BaseModel):
    panels: list[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int = Field(ge=1)

    caption: str = Field(
        default="",
        max_length=500
    )

    narration: str = Field(
        default="",
        max_length=1200
    )

    dialogue: list[str] = Field(
        default_factory=list,
        max_length=6
    )


class ComicStory(BaseModel):
    panels: list[PanelStory]


class ComicResult(BaseModel):
    comic_id: str
    title: str
    layout: list[dict]
    pdf_url: str