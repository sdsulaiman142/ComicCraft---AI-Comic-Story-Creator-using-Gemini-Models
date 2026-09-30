import uuid
from pathlib import Path

from fpdf import FPDF

from app.config import (
    BASE_DIR,
    EXPORTS_DIR
)


def _ascii(text: str) -> str:

    text = text or ""

    replacements = {
        "—": "-",
        "–": "-",
        "“": '"',
        "”": '"',
        "’": "'",
        "…": "...",
        "•": "-"
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new
        )

    return (
        text
        .encode(
            "latin-1",
            errors="replace"
        )
        .decode("latin-1")
    )


def _local_image(
    url_path: str
) -> Path:

    if not url_path.startswith(
        "/static/"
    ):
        raise ValueError(
            "Invalid image path."
        )

    return (
        BASE_DIR
        / url_path.lstrip("/")
    )


def save_pdf(
    layout: list[dict],
    title: str = "ComicCraft Comic"
) -> str:

    filename = (
        f"comic_"
        f"{uuid.uuid4().hex[:12]}"
        f".pdf"
    )

    output = EXPORTS_DIR / filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in layout:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            20
        )

        pdf.multi_cell(
            170,
            10,
            _ascii(
                f"Panel "
                f"{panel['panel_number']}: "
                f"{panel['title']}"
            ),
            align="C"
        )

        image = _local_image(
            panel["image_path"]
        )

        if image.exists():

            pdf.image(
                str(image),
                x=20,
                y=38,
                w=170,
                h=105
            )

        pdf.set_y(150)

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            170,
            6,
            _ascii(
                panel.get(
                    "scene_description",
                    ""
                )
            )
        )

        pdf.ln(3)

        pdf.set_font(
            "Helvetica",
            "B",
            11
        )

        if panel.get("caption"):

            pdf.multi_cell(
                170,
                6,
                _ascii(
                    f"CAPTION: "
                    f"{panel['caption']}"
                )
            )

        pdf.set_font(
            "Helvetica",
            "",
            11
        )

        if panel.get("narration"):

            pdf.multi_cell(
                170,
                6,
                _ascii(
                    f"NARRATION: "
                    f"{panel['narration']}"
                )
            )

        for line in panel.get(
            "dialogue",
            []
        ):

            pdf.multi_cell(
                170,
                6,
                _ascii(
                    f"DIALOGUE: {line}"
                )
            )

    pdf.set_title(
        _ascii(title)
    )

    pdf.output(
        str(output)
    )

    return (
        f"/static/exports/"
        f"{filename}"
    )