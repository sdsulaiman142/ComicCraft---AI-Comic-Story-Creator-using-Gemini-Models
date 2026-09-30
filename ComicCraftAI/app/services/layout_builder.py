from app.schemas import (
    PanelOutline,
    PanelStory
)


def build_comic_layout(
    outline: list[PanelOutline],
    story: list[PanelStory],
    image_paths: list[str]
) -> list[dict]:

    if not (
        len(outline)
        == len(story)
        == len(image_paths)
    ):
        raise ValueError(
            "Outline, story and image lists "
            "must contain the same number of panels."
        )

    layout = []

    for panel, narrative, image_path in zip(
        outline,
        story,
        image_paths
    ):

        layout.append(
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "image_path": image_path,
                "scene_description": (
                    panel.scene_description
                ),
                "image_prompt": (
                    panel.image_prompt
                ),
                "caption": narrative.caption,
                "narration": narrative.narration,
                "dialogue": narrative.dialogue
            }
        )

    return layout