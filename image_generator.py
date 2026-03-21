"""
Handles image generation using Google Gemini.

Uses gemini-2.0-flash-preview-image-generation which accepts both text and image
input, allowing the reference product photo to be composited into ad layouts.
"""

import re
import time
from typing import Optional

from google import genai
from google.genai import types


def analyze_product_image(client: genai.Client, image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Send the product image to Gemini Vision to get a detailed description.
    This description is used to enrich the ad prompt generation.
    """
    from prompt_generator import build_product_analysis_prompt

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=[build_product_analysis_prompt(), image_part],
    )
    return response.text.strip()


def generate_ad_concepts(client: genai.Client, image_bytes: bytes, product_description: str, mime_type: str = "image/jpeg") -> str:
    """
    Send the product image + requirements to Gemini to generate all 10 concept prompts.
    Returns the raw text containing all concepts.
    """
    from prompt_generator import build_prompt_generation_request

    image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    full_prompt = build_prompt_generation_request(product_description)
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=[full_prompt, image_part],
    )
    return response.text.strip()


def generate_ad_image(
    client: genai.Client,
    ad_prompt: str,
    reference_image_bytes: bytes,
    reference_mime_type: str = "image/jpeg",
    max_retries: int = 3,
) -> Optional[bytes]:
    """
    Generate a single ad image using Gemini's image generation model.
    Passes the reference product photo so it can be composited into the layout.

    Returns image bytes (PNG) or None if generation failed.
    """
    image_part = types.Part.from_bytes(data=reference_image_bytes, mime_type=reference_mime_type)

    full_prompt = (
        "Using the reference product photo provided, generate a professional advertisement image. "
        "The product photo must be composited into the design as specified — not just used as a background. "
        "Follow these exact specifications:\n\n"
        + ad_prompt
    )

    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=[full_prompt, image_part],
                config=types.GenerateContentConfig(
                    response_modalities=["image", "text"]
                ),
            )

            # Extract image from response parts
            for part in response.candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data

            print(f"    Warning: No image in response on attempt {attempt}")

        except Exception as e:
            wait = 2 ** attempt
            print(f"    Image gen error (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                print(f"    Retrying in {wait}s...")
                time.sleep(wait)

    return None


def parse_concepts(raw_concepts_text: str) -> dict:
    """
    Parse the raw Gemini output into a structured dict:
    {
        1: {
            "name": "Concept Name",
            "angle": "Angle Name",
            "formats": {
                "square": "prompt text...",
                "vertical": "prompt text...",
                "horizontal": "prompt text...",
            }
        },
        ...
    }
    """
    concepts = {}

    # Split by CONCEPT marker
    concept_blocks = re.split(r"CONCEPT\s+(\d+):", raw_concepts_text)

    # concept_blocks[0] is text before first CONCEPT (discard)
    # Then pairs: [index_str, block_content, ...]
    i = 1
    while i < len(concept_blocks) - 1:
        concept_num = int(concept_blocks[i].strip())
        block = concept_blocks[i + 1]
        i += 2

        # Extract name and angle from first line
        first_line_match = re.match(r"([^\n—–-]+)[—–-]+([^\n]+)", block)
        if first_line_match:
            name = first_line_match.group(1).strip()
            angle = first_line_match.group(2).strip()
        else:
            name = f"Concept {concept_num}"
            angle = ""

        # Extract format prompts
        formats = {}
        format_pattern = re.compile(
            r"▶\s*(SQUARE|VERTICAL|HORIZONTAL)[^\n]*\n(.*?)(?=▶\s*(?:SQUARE|VERTICAL|HORIZONTAL)|CONCEPT\s+\d+:|$)",
            re.DOTALL | re.IGNORECASE,
        )
        for match in format_pattern.finditer(block):
            fmt_key = match.group(1).lower()
            prompt_text = match.group(2).strip()
            formats[fmt_key] = prompt_text

        if formats:
            concepts[concept_num] = {
                "name": name,
                "angle": angle,
                "formats": formats,
            }

    print(f"Parsed {len(concepts)} concepts from Gemini output.")
    return concepts
