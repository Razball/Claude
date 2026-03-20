"""
Generates 10 ad concept prompts (3 formats each) using Gemini Vision.
Each concept targets a different DTC angle for the EzLift adjustable sleep system.
"""

SYSTEM_INSTRUCTIONS = """
You are an expert DTC performance ad copywriter and art director for a premium adjustable
sleep-to-stand system called EzLift Deluxe — a $2,700 product that helps seniors and mobility-limited
individuals stand up independently. It is a high-end medical device meets luxury furniture.

CRITICAL RULES:
- NEVER use the word "bed" or "beds" anywhere. Substitute with: sleep system, frame, Deluxe, unit,
  adjustable frame, EzLift, sleep-to-stand system.
- Every prompt must be self-contained — ready to paste directly into an image generation tool.
- The reference photo must be composited INTO the layout as a design element, not just placed behind text.
- Write EXACT copy that appears on the ad. Never say "add a headline about X" — say the exact words.
- Colors must use hex codes. Fonts must be described (e.g., "large white serif headline").
- Each of the 3 format prompts must be meaningfully different layouts — not the same design cropped.
- Make ads feel premium and emotionally resonant — luxury medical meets high-end furniture.
"""

PROMPT_REQUIREMENTS = """
Based on the reference product photo provided, generate 10 ad concepts for the EzLift Deluxe
adjustable sleep-to-stand system. Each concept must cover all 3 formats.

AD ANGLES TO COVER (hit at least 6 of these):
1. Emotional Independence — "Stand on your own" / dignity / staying home
2. Caregiver Relief — adult child buying for parent, "Mom can get up on her own again"
3. Feature Spotlight — zero-gravity recline, sleep-to-stand lift, knee/foot support
4. Social Proof / Testimonial — reviews, star ratings, "5,000+ families"
5. Problem → Solution — struggling vs. standing, fear of assisted living
6. Trust / Risk Reversal — 6-year warranty, free shipping, in-home install
7. Urgency / Offer — free install promo, limited-time savings
8. Before / After — life without vs. life with the Deluxe
9. Editorial / Magazine — premium, story-driven, elevated brand feel
10. Aspirational Lifestyle — aging at home beautifully, comfort + design

STYLE DIRECTION — vary across concepts:
- Dark + gold (#1A1A1A bg, #C9A84C accents) — luxury/premium
- Warm cream/linen (#F5F0E8 bg, #2C2C2C text) — editorial/magazine
- Navy + teal (#0D1B2A bg, #2EC4B6 accents) — trust/medical authority
- Red-to-green gradient (#C0392B to #27AE60) — problem/solution
- Deep purple + lavender (#1E0A3C bg, #B8A9D9 accents) — comfort/zero-gravity
- Clean white + green (#FFFFFF bg, #2ECC71 accents) — fresh/health

OUTPUT FORMAT — for each concept, output EXACTLY:

CONCEPT [1-10]: [Name] — [Angle]

▶ SQUARE (1080×1080):
[Full image generation prompt]

▶ VERTICAL (1080×1350):
[Full image generation prompt]

▶ HORIZONTAL (1200×628):
[Full image generation prompt]

PROMPT REQUIREMENTS — every prompt must include:
- Exact placement of the reference photo (full-bleed background, left half, right half, etc.)
- Every piece of text with exact wording, font style, size description, color, and position
- Hex color codes for all colors used
- Gradient overlays, badge shapes, divider lines, graphic elements
- Layout description spatial enough that a designer could recreate it exactly
- The reference photo composited as a design element (not just a background)

REMEMBER: ZERO use of "bed" or "beds". Use: sleep system, frame, Deluxe, unit, adjustable frame, EzLift, sleep-to-stand system.
"""

def build_prompt_generation_request(product_description: str) -> str:
    """Build the full prompt to send to Gemini for concept generation."""
    return f"""
{PROMPT_REQUIREMENTS}

Product context from the reference photo:
{product_description}

Generate all 10 concepts now with all 3 formats each.
"""


def build_product_analysis_prompt() -> str:
    """Prompt to analyze the product image before generating ad concepts."""
    return """
Analyze this product photo in detail. Describe:
1. What the product looks like (colors, materials, style, shape)
2. The setting/environment it's shown in
3. Key visual features that should be preserved in ads
4. The overall mood and aesthetic of the photo
5. Any text, branding, or labels visible

Be specific about colors using approximate hex codes where possible.
Keep your description to 150 words max.
"""
