from django.urls import path

from . import views

urlpatterns = [
    path("upload/", views.upload_view, name="admin_async_upload"),
]
