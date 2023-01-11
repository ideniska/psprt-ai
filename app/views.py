from django.views.generic import TemplateView, DetailView
from django.views.generic import FormView
from django.views import View
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from .forms import EmailAuthenticationForm, DocumentTypeForm, FileForm
from .models import UserFile
from users.models import CustomUser
from faker import Faker
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from .service import PhotoPreparation
from rembg import remove
from PIL import Image
from django.shortcuts import get_object_or_404


fake_data = Faker()


class LandingPageView(TemplateView):
    template_name = "landing_page.html"


class UploadView(FormView):
    template_name = "upload.html"
    form_class = FileForm
    success_url = "/choose/"

    def form_valid(self, form):
        self.request.session.save()
        session_key = self.request.session.session_key

        # Delete old files assosiated with this session
        if UserFile.objects.all():
            UserFile.objects.filter(session=session_key).delete()

        # user_file = File(
        #     file=self.get_form_kwargs().get("files")["file"], session=session_key
        # )
        # user_file.save()

        files = self.request.FILES.getlist("file")
        for f in files:
            print(f)
            user_file = UserFile(file=f, session=session_key)
            user_file.save()

        return super().form_valid(form)


class ChooseView(View):
    template_name = "choose.html"
    form_class = DocumentTypeForm

    def get(self, request):
        session_key = self.request.session.session_key
        form = self.form_class()
        uploaded_files = UserFile.objects.filter(session=session_key).filter(
            edited=False
        )
        context = {"form": form, "uploaded_files": uploaded_files}
        return render(request, self.template_name, context)

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            session_key = self.request.session.session_key
            uploaded_files = UserFile.objects.filter(session=session_key).filter(
                edited=False
            )
            for uploaded_file in uploaded_files:
                file_path = uploaded_file.file.path
                file_name = uploaded_file.file.name
                photo_size = form.cleaned_data["document_type"]
                uploaded_file.prepared_for = photo_size
                uploaded_file.save()
                service = PhotoPreparation(
                    photo_size, file_path, file_name, session_key, uploaded_file.id
                )
                service.make()
            # context = {"choice": photo_size}
            return redirect("/prepare/")
        else:
            # uploaded_files = File.objects.filter(session=session_key).latest(
            #     "uploaded_at"
            # )
            context = {"form": form, "uploaded_files": uploaded_files}
            return render(request, self.template_name, context)


class PrepareView(TemplateView):
    template_name = "prepare.html"

    def get_context_data(self, **kwargs):
        session_key = self.request.session.session_key
        context = super().get_context_data(**kwargs)
        # image = File.objects.filter(session=session_key).latest("uploaded_at")
        prepared_images = UserFile.objects.filter(session=session_key).filter(
            edited=True
        )
        context["prepared_images"] = prepared_images
        prepared_for = prepared_images.first().get_prepared_for_display()
        context["prepared_for"] = prepared_for
        size_requirements_for_display = {
            "australia_passport": {
                "size": (413, 531),
                "head": 55,
            },
            "china_visa": {
                "size": (600, 600),
                "head": 55,
            },
            "european_union_passport": {
                "size": (413, 531),
                "head": 55,
            },
            "schengen_visa": {
                "size": (413, 531),
                "head": 55,
            },
            "us_passport": {
                "size": (600, 600),
                "head": 55,
            },
            "india_visa": {
                "size": (600, 600),
                "head": 55,
            },
            "japan_visa": {
                "size": (531, 531),
                "head": 55,
            },
            "us_visa": {
                "size": (600, 600),
                "head": 55,
            },
            "canada_visa": {
                "size": (413, 531),
                "head": 55,
            },
            "canada_passport": {
                "size": (590, 826),
                "head": 55,
            },
        }
        context["size"] = size_requirements_for_display[
            prepared_images.first().prepared_for
        ]["size"]
        return context
