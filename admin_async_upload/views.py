from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import View

from admin_async_upload.files import ResumableFile


class UploadView(View):
    @cached_property
    def request_data(self):
        return getattr(self.request, self.request.method)

    @cached_property
    def model_upload_field(self):
        content_type = ContentType.objects.get_for_id(
            self.request_data["content_type_id"]
        )

        return content_type.model_class()._meta.get_field(
            self.request_data["field_name"]
        )

    def post(self, request, *args, **kwargs):
        chunk = request.FILES.get("file")
        resumable_file = ResumableFile(
            self.model_upload_field,
            user=request.user,
            params=request.POST,
        )

        if not resumable_file.chunk_exists:
            resumable_file.process_chunk(chunk)

        if resumable_file.is_complete:
            return HttpResponse(resumable_file.collect())
        return HttpResponse("chunk uploaded")

    def get(self, request, *args, **kwargs):
        resumable_file = ResumableFile(
            self.model_upload_field,
            user=request.user,
            params=request.GET,
        )

        if not resumable_file.chunk_exists:
            return HttpResponse("chunk not found", status=204)

        if resumable_file.is_complete:
            return HttpResponse(resumable_file.collect())
        return HttpResponse("chunk exists")


upload_view = login_required(UploadView.as_view())
