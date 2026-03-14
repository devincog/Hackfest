"""
API Views for the Automated Briefing Generator.
"""
import os
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import Project, Document
from api.serializers import UploadSerializer, GenerateSerializer, UpdateSerializer
from api.services.ingest_service import ingest_documents
from api.services.rag_service import generate_slides_html
from api.exporters.html_exporter import render_tailwind_html


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_documents(request):
    """
    POST /api/upload/
    Upload PDF/TXT files to a project. Creates a new project if none specified.
    """
    project_id = request.data.get("project_id")
    files = request.FILES.getlist("files")

    if not files:
        return Response({"error": "No files provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Create or get project
    if project_id:
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        project = Project.objects.create(name="New Briefing")

    # Save files to disk and track in DB
    saved_paths = []
    for f in files:
        doc = Document.objects.create(
            project=project,
            file=f,
            filename=f.name,
        )
        saved_paths.append(doc.file.path)

    # Run ingestion pipeline (parse, chunk, embed, store in MongoDB Atlas)
    try:
        result = ingest_documents(saved_paths, str(project.id))
        # Mark documents as processed
        Document.objects.filter(project=project, is_processed=False).update(is_processed=True)
    except Exception as e:
        return Response(
            {"error": f"Ingestion failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response({
        "project_id": str(project.id),
        "project_name": project.name,
        **result,
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def generate_presentation(request):
    """
    POST /api/generate/
    Generate a new presentation from uploaded documents + user query.
    Returns raw Tailwind HTML slides.
    """
    serializer = GenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data["query"]
    project_id = str(serializer.validated_data["project_id"])

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    # Generate Tailwind HTML slides via RAG + LLM
    try:
        slides_html = generate_slides_html(query, project_id)
    except Exception as e:
        return Response(
            {"error": f"Generation failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Save the raw HTML and query to project
    # We store the raw HTML string in slide_schema (reusing the field)
    project.slide_schema = {"raw_html": slides_html}
    project.query = query
    project.save()

    return Response({
        "project_id": project_id,
        "slides_html": slides_html,
    })


@api_view(["POST"])
def update_presentation(request):
    """
    POST /api/update/
    Update an existing presentation. Layout is preserved while content changes.
    """
    serializer = UpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    query = serializer.validated_data["query"]
    project_id = str(serializer.validated_data["project_id"])

    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    if not project.slide_schema:
        return Response(
            {"error": "No existing presentation to update. Use /api/generate/ first."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    existing_html = project.slide_schema.get("raw_html", "")

    # Generate updated slides with layout preservation
    try:
        slides_html = generate_slides_html(query, project_id, existing_html=existing_html)
    except Exception as e:
        return Response(
            {"error": f"Update failed: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    project.slide_schema = {"raw_html": slides_html}
    project.query = query
    project.save()

    return Response({
        "project_id": project_id,
        "slides_html": slides_html,
    })


@api_view(["GET"])
def render_presentation(request, project_id):
    """
    GET /api/render/<project_id>/
    Render the presentation as a standalone Tailwind HTML page.
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    if not project.slide_schema:
        return Response(
            {"error": "No presentation generated yet."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    raw_html = project.slide_schema.get("raw_html", "")
    html = render_tailwind_html(raw_html)
    return HttpResponse(html, content_type="text/html")


@api_view(["GET"])
def get_project(request, project_id):
    """
    GET /api/project/<project_id>/
    Get project details including the slides HTML.
    """
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)

    docs = Document.objects.filter(project=project).values("id", "filename", "is_processed", "uploaded_at")

    # Return slides as an array split by SLIDE_BREAK
    raw_html = ""
    slides = []
    if project.slide_schema:
        raw_html = project.slide_schema.get("raw_html", "")
        slides = [s.strip() for s in raw_html.split("<!-- SLIDE_BREAK -->") if s.strip()]

    return Response({
        "project_id": str(project.id),
        "name": project.name,
        "query": project.query,
        "slides": slides,
        "slides_count": len(slides),
        "documents": list(docs),
        "created_at": project.created_at,
        "updated_at": project.updated_at,
    })
