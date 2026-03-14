"""
HTML Exporter — wraps raw Tailwind HTML slides into a full page
with Tailwind CDN, Google Fonts, CSS animations, and JS slideshow navigation.
"""


def render_tailwind_html(slides_html: str) -> str:
    """
    Wrap raw Tailwind HTML slides into a self-contained HTML page
    with a proper slideshow viewer (one slide at a time, arrow key navigation).
    """
    # Split slides for the JS slideshow
    slides = [s.strip() for s in slides_html.split("<!-- SLIDE_BREAK -->") if s.strip()]
    num_slides = len(slides)

    # Build a JS array of slide HTML strings
    slides_js_array = "const slidesData = [\n"
    for slide in slides:
        # Escape backticks and backslashes for JS template literal
        escaped = slide.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
        slides_js_array += f"  `{escaped}`,\n"
    slides_js_array += "];\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Briefing Deck — Fullscreen</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #050505;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
        }}
        .slide {{
            box-shadow: 0 0 60px rgba(229, 9, 20, 0.15), 0 25px 50px -12px rgba(0, 0, 0, 0.8);
        }}

        /* Navigation */
        .nav-bar {{
            position: fixed;
            bottom: 20px;
            display: flex;
            gap: 12px;
            align-items: center;
            z-index: 100;
            background: rgba(10, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(229, 9, 20, 0.3);
            padding: 8px 20px;
            border-radius: 999px;
        }}
        .nav-btn {{
            background: transparent;
            color: #ccc;
            border: 1px solid rgba(255,255,255,0.2);
            padding: 6px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-family: 'Share Tech Mono', monospace;
            font-size: 14px;
            transition: all 0.2s;
        }}
        .nav-btn:hover {{
            background: rgba(229, 9, 20, 0.3);
            border-color: rgba(229, 9, 20, 0.6);
            color: white;
        }}
        .nav-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
        }}
        .slide-counter {{
            color: rgba(255,255,255,0.6);
            font-size: 14px;
            font-family: 'Share Tech Mono', monospace;
            min-width: 60px;
            text-align: center;
        }}

        /* ─── Animation Keyframes ─── */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        @keyframes fadeUp {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeDown {{
            from {{ opacity: 0; transform: translateY(-30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes fadeLeft {{
            from {{ opacity: 0; transform: translateX(-40px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        @keyframes fadeRight {{
            from {{ opacity: 0; transform: translateX(40px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}
        @keyframes zoomIn {{
            from {{ opacity: 0; transform: scale(0.85); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        @keyframes slideIn {{
            from {{ opacity: 0; transform: translateX(60px); }}
            to {{ opacity: 1; transform: translateX(0); }}
        }}

        .anim-fade-in {{ animation: fadeIn 0.6s ease-out both; }}
        .anim-fade-up {{ animation: fadeUp 0.6s ease-out both; }}
        .anim-fade-down {{ animation: fadeDown 0.6s ease-out both; }}
        .anim-fade-left {{ animation: fadeLeft 0.6s ease-out both; }}
        .anim-fade-right {{ animation: fadeRight 0.6s ease-out both; }}
        .anim-zoom-in {{ animation: zoomIn 0.6s ease-out both; }}
        .anim-slide-in {{ animation: slideIn 0.6s ease-out both; }}
    </style>
</head>
<body>
    <div id="slide-viewport" style="display: flex; align-items: center; justify-content: center; width: 100vw; height: 100vh;"></div>

    <div class="nav-bar">
        <button class="nav-btn" id="prevBtn" onclick="goSlide(-1)">◀ PREV</button>
        <span class="slide-counter" id="counter">1 / {num_slides}</span>
        <button class="nav-btn" id="nextBtn" onclick="goSlide(1)">NEXT ▶</button>
    </div>

    <script>
        {slides_js_array}
        let currentSlide = 0;

        function renderSlide() {{
            const viewport = document.getElementById('slide-viewport');
            // Clear and re-inject to restart all CSS animations
            viewport.innerHTML = '';
            requestAnimationFrame(() => {{
                viewport.innerHTML = slidesData[currentSlide];
                document.getElementById('counter').textContent = (currentSlide + 1) + ' / ' + slidesData.length;
                document.getElementById('prevBtn').disabled = currentSlide === 0;
                document.getElementById('nextBtn').disabled = currentSlide >= slidesData.length - 1;
            }});
        }}

        function goSlide(dir) {{
            const next = currentSlide + dir;
            if (next >= 0 && next < slidesData.length) {{
                currentSlide = next;
                renderSlide();
            }}
        }}

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'ArrowRight' || e.key === ' ') goSlide(1);
            if (e.key === 'ArrowLeft') goSlide(-1);
        }});

        // Initial render
        renderSlide();
    </script>
</body>
</html>"""
    return html
