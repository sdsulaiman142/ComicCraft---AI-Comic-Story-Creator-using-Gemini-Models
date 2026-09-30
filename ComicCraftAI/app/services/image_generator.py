import re
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.config import PANELS_DIR, settings


def _safe_name(value: str) -> str:
    """Create a safe filename from the image prompt."""

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value
    )

    value = value.strip("_")

    return value[:80] or "panel"


def _mock_image(
    prompt: str,
    path: Path,
    panel_number: int
) -> None:
    """Create a local placeholder image."""

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height
        ),
        (247, 242, 228)
    )

    draw = ImageDraw.Draw(image)

    margin = 40

    draw.rounded_rectangle(
        (
            margin,
            margin,
            settings.image_width - margin,
            settings.image_height - margin
        ),
        radius=28,
        outline=(30, 30, 30),
        width=6,
        fill=(255, 251, 240)
    )

    title = (
        f"COMICCRAFT\n"
        f"PANEL {panel_number}"
    )

    try:
        font = ImageFont.truetype(
            "DejaVuSans-Bold.ttf",
            48
        )

        small = ImageFont.truetype(
            "DejaVuSans.ttf",
            22
        )

    except OSError:
        font = ImageFont.load_default()
        small = font

    draw.multiline_text(
        (
            margin + 45,
            margin + 55
        ),
        title,
        font=font,
        fill=(20, 20, 20),
        spacing=8
    )

    wrapped = " ".join(prompt.split())[:360]

    draw.multiline_text(
        (
            margin + 45,
            270
        ),
        wrapped,
        font=small,
        fill=(70, 70, 70),
        spacing=8
    )

    draw.ellipse(
        (
            settings.image_width - 240,
            settings.image_height - 260,
            settings.image_width - 90,
            settings.image_height - 110
        ),
        outline=(20, 20, 20),
        width=5
    )

    image.save(
        path,
        format="PNG"
    )


def _hf_image(
    prompt: str,
    path: Path
) -> None:
    """Generate a real image using Hugging Face."""

    token = (
        settings.hf_token
        or settings.hf_api_key
    )

    if not token:
        raise RuntimeError(
            "Hugging Face token is missing. "
            "Set HF_TOKEN in your .env file."
        )

    try:
        from huggingface_hub import InferenceClient
    except ImportError as exc:
        raise RuntimeError(
            "huggingface_hub is not installed. "
            "Run: pip install -U huggingface_hub"
        ) from exc

    try:
        client = InferenceClient(
            provider=settings.hf_provider,
            api_key=token,
        )

        print(
            f"Generating image with "
            f"{settings.hf_image_model}..."
        )

        image = client.text_to_image(
            prompt=prompt,
            model=settings.hf_image_model,
            width=settings.image_width,
            height=settings.image_height,
            num_inference_steps=settings.image_steps,
            guidance_scale=settings.image_guidance,
        )

    except Exception as exc:
        raise RuntimeError(
            "Hugging Face image generation failed. "
            f"Model: {settings.hf_image_model}. "
            f"Provider: {settings.hf_provider}. "
            f"Original error: {exc}"
        ) from exc

    if not isinstance(image, Image.Image):
        raise RuntimeError(
            "Hugging Face returned an unexpected "
            "response instead of an image."
        )

    try:
        image.save(
            path,
            format="PNG"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Could not save generated image: {exc}"
        ) from exc


def generate_image(
    prompt: str,
    panel_number: int
) -> str:
    """Generate one comic panel image."""

    if not prompt or not prompt.strip():
        raise ValueError(
            "Image prompt cannot be empty."
        )

    filename = (
        f"{panel_number:02d}_"
        f"{_safe_name(prompt)}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )

    path = PANELS_DIR / filename

    if settings.mock_mode:

        print(
            f"Creating mock image for panel "
            f"{panel_number}..."
        )

        _mock_image(
            prompt,
            path,
            panel_number
        )

    else:

        print(
            f"Creating AI image for panel "
            f"{panel_number}..."
        )

        _hf_image(
            prompt,
            path
        )

    return f"/static/panels/{filename}"