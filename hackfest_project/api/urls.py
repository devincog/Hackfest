from django.urls import path
from api import views

urlpatterns = [
    path("upload/", views.upload_documents, name="upload_documents"),
    path("generate/", views.generate_presentation, name="generate_presentation"),
    path("update/", views.update_presentation, name="update_presentation"),
    path("render/<uuid:project_id>/", views.render_presentation, name="render_presentation"),
    path("project/<uuid:project_id>/", views.get_project, name="get_project"),
]
