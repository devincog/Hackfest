"""
Quick test script for the backend API endpoints.
Run this while the Django server is running on port 8000.
"""
import sys
import os

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ['DJANGO_SETTINGS_MODULE'] = 'hackfest_project.settings'

import django
django.setup()

from api.models import Project, Document
from api.services.ingest_service import ingest_documents, extract_text

TEST_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data', 'hawkins_research_notes.txt')

print("=" * 60)
print("TEST 1: Text extraction")
print("=" * 60)
try:
    text = extract_text(TEST_FILE)
    print(f"Extracted {len(text)} characters from test file")
    print(f"Preview: {text[:100]}...")
    print("PASS")
except Exception as e:
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("TEST 2: Create Project + Document via Django ORM")
print("=" * 60)
try:
    project = Project.objects.create(name="Test Briefing")
    print(f"Created project: {project.id}")

    from django.core.files.uploadedfile import SimpleUploadedFile
    with open(TEST_FILE, 'rb') as f:
        uploaded = SimpleUploadedFile("hawkins_research_notes.txt", f.read(), content_type="text/plain")
    doc = Document.objects.create(
        project=project,
        file=uploaded,
        filename="hawkins_research_notes.txt",
    )
    print(f"Created document: {doc.id}, path: {doc.file.path}")
    print("PASS")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAIL: {e}")
    sys.exit(1)

print()
print("=" * 60)
print("TEST 3: Ingest pipeline (chunk + embed + MongoDB)")
print("=" * 60)
try:
    result = ingest_documents([doc.file.path], str(project.id))
    print(f"Result: {result}")
    print("PASS")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("TEST 4: RAG + LLM Generation")
print("=" * 60)
try:
    from api.services.rag_service import generate_slide_schema
    schema = generate_slide_schema("Explain wireless signal interference in the Upside Down", str(project.id))
    print(f"Generated {len(schema.get('slides', []))} slides")
    print(f"Title: {schema.get('title')}")
    for slide in schema.get("slides", []):
        print(f"  Slide {slide['slide_number']}: {slide['title']}")
    print("PASS")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("TEST 5: Reveal.js HTML Rendering")
print("=" * 60)
try:
    from api.services.generation_service import render_revealjs_html
    if schema:
        html = render_revealjs_html(schema)
        print(f"Generated HTML: {len(html)} characters")
        print(f"Contains Reveal.js: {'reveal.js' in html}")
        # Save to file for inspection
        output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_data', 'test_output.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Saved to: {output_path}")
        print("PASS")
    else:
        print("SKIP: No schema from previous test")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"FAIL: {e}")

print()
print("=" * 60)
print("ALL TESTS COMPLETE")
print(f"Project ID for further testing: {project.id}")
print("=" * 60)
