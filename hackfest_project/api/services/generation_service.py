"""
Generation Engine — Layer 3
Takes a slide_schema JSON and renders it into a Reveal.js HTML presentation.
"""


def render_revealjs_html(slide_schema: dict) -> str:
    """
    Render a SlideDeck schema into a self-contained Reveal.js HTML string.
    Animations are mapped to Reveal.js fragment + data-fragment attributes.
    """
    deck = slide_schema
    theme = deck.get("theme", "dark")
    title = deck.get("title", "Presentation")
    subtitle = deck.get("subtitle", "")

    slides_html = ""

    for slide in deck.get("slides", []):
        bg_color = slide.get("background_color", "")
        transition = slide.get("transition", "slide")
        bg_attr = f' data-background-color="{bg_color}"' if bg_color else ""
        trans_attr = f' data-transition="{transition}"'

        slide_content = f'<section{bg_attr}{trans_attr}>\n'
        slide_content += f'  <h2>{slide.get("title", "")}</h2>\n'

        for i, elem in enumerate(slide.get("elements", [])):
            elem_type = elem.get("type", "text")
            content = elem.get("content", "")
            animation = elem.get("animation", "fade-in")
            delay = elem.get("animation_delay", 0)

            # Map animation types to Reveal.js fragment classes
            anim_class = _map_animation(animation)
            delay_style = f' style="animation-delay: {delay}s;"' if delay > 0 else ""
            fragment_idx = f' data-fragment-index="{i}"' if animation != "none" else ""
            fragment_class = f' class="fragment {anim_class}"' if animation != "none" else ""

            if elem_type == "heading":
                slide_content += f'  <h3{fragment_class}{fragment_idx}{delay_style}>{content}</h3>\n'
            elif elem_type == "bullet":
                slide_content += f'  <p{fragment_class}{fragment_idx}{delay_style}>• {content}</p>\n'
            elif elem_type == "quote":
                slide_content += f'  <blockquote{fragment_class}{fragment_idx}{delay_style}>{content}</blockquote>\n'
            elif elem_type == "image_placeholder":
                slide_content += f'  <div{fragment_class}{fragment_idx}{delay_style} class="image-placeholder" style="border: 2px dashed #555; padding: 2rem; text-align: center; margin: 1rem auto; max-width: 60%;">📷 {content}</div>\n'
            else:  # text
                slide_content += f'  <p{fragment_class}{fragment_idx}{delay_style}>{content}</p>\n'

        slide_content += '</section>\n'
        slides_html += slide_content

    # Build full HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reset.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/theme/{_map_theme(theme)}.css">
    <style>
        .reveal .slides section {{
            text-align: left;
            padding: 40px;
        }}
        .reveal .slides section h2 {{
            color: #e50914;
            text-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
            margin-bottom: 30px;
            font-family: 'Georgia', serif;
        }}
        .reveal .slides section h3 {{
            color: #ff6b6b;
            margin-bottom: 15px;
        }}
        .reveal .slides section p {{
            font-size: 0.9em;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        .reveal .slides section blockquote {{
            border-left: 4px solid #e50914;
            padding-left: 20px;
            font-style: italic;
            color: #ccc;
        }}
        .image-placeholder {{
            border: 2px dashed #555 !important;
            padding: 2rem !important;
            text-align: center !important;
            margin: 1rem auto !important;
            max-width: 60% !important;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
{slides_html}
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.js"></script>
    <script>
        Reveal.initialize({{
            hash: true,
            slideNumber: true,
            transition: 'slide',
            backgroundTransition: 'fade',
            autoAnimateDuration: 0.7,
        }});
    </script>
</body>
</html>"""

    return html


def _map_animation(animation: str) -> str:
    """Map our schema animation types to Reveal.js CSS fragment classes."""
    mapping = {
        "fade-in": "fade-in",
        "fade-up": "fade-up",
        "fade-down": "fade-down",
        "fade-left": "fade-left",
        "fade-right": "fade-right",
        "zoom-in": "zoom-in",
        "slide-in": "fade-right",
        "none": "",
    }
    return mapping.get(animation, "fade-in")


def _map_theme(theme: str) -> str:
    """Map our schema themes to Reveal.js theme file names."""
    mapping = {
        "dark": "black",
        "light": "white",
        "night": "night",
        "moon": "moon",
        "blood": "blood",
    }
    return mapping.get(theme, "black")
