from django.db import models
import uuid


class Project(models.Model):
    """Represents a user's briefing/presentation project."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, default="Untitled Briefing")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # The slide schema JSON produced by the LLM
    slide_schema = models.JSONField(null=True, blank=True)

    # The user query that generated this presentation
    query = models.TextField(blank=True, default="")

    def __str__(self):
        return self.name


class Document(models.Model):
    """An uploaded source document (PDF/TXT)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='uploads/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Whether it has been chunked and embedded
    is_processed = models.BooleanField(default=False)

    def __str__(self):
        return self.filename
