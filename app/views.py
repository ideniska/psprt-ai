from django.views.generic import TemplateView
from django.views.generic import FormView
from django.views import View
from django.shortcuts import render, redirect
from django.views import View
from .forms import DocumentTypeForm, FileForm
from .models import UserFile
from faker import Faker
from .service import PhotoPreparation
import json
from django.http import JsonResponse
from app.task import process_photos
from celery.result import AsyncResult
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .stripe import StripeCreatePayment

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
        if UserFile.objects.filter(session=session_key).exists():
            UserFile.objects.filter(session=session_key).delete()

        files = self.request.FILES.getlist("file")
        for f in files:
            user_file = UserFile(file=f, session=session_key)
            user_file.save()

        return super().form_valid(form)


class PrepareBackend(View):
    def post(self, request):
        session_key = self.request.session.session_key
        uploaded_files = UserFile.objects.filter(session=session_key).filter(
            edited=False
        )
        photo_size_country = request.POST.get("document_type")
        # task = go_to_sleep.delay(session_key)
        UserFile.objects.filter(session=session_key).filter(edited=False).update(
            prepared_for=photo_size_country
        )
        uploaded_files = list(
            UserFile.objects.filter(session=session_key)
            .filter(edited=False)
            .values_list("id", flat=True)
        )
        print(uploaded_files)
        task = process_photos.delay(session_key, uploaded_files)

        # user_files = UserFile.objects.filter(id__in=uploaded_files)
        # for file in user_files:
        #     print(f"{file.prepared_for=}")
        #     print(f"{file.file.path=}")
        #     print(f"{file.file.name=}")
        #     print(f"{session_key=}")
        #     print(f"{file.id=}")
        #     service = PhotoPreparation(
        #         file.prepared_for,
        #         file.file.path,
        #         file.file.name,
        #         session_key,
        #         file.id,
        #     )
        #     service.make()

        return JsonResponse({"success": True})


class ChooseView(View):
    template_name = "choose.html"
    form_class = DocumentTypeForm

    # TODO Move business logic to services
    def get(self, request):
        session_key = self.request.session.session_key
        form = self.form_class()
        uploaded_files = UserFile.objects.filter(session=session_key).filter(
            edited=False
        )
        context = {"form": form, "uploaded_files": uploaded_files}
        return render(request, self.template_name, context)

    # def post(self, request):
    #     form = self.form_class(request.POST)
    #     if form.is_valid():
    #         session_key = self.request.session.session_key
    #         uploaded_files = UserFile.objects.filter(session=session_key).filter(
    #             edited=False
    #         )
    #         for uploaded_file in uploaded_files:
    #             file_path = uploaded_file.file.path
    #             file_name = uploaded_file.file.name
    #             photo_size_country = form.cleaned_data["document_type"]
    #             uploaded_file.prepared_for = photo_size_country
    #             uploaded_file.save()
    #             # service = PhotoPreparation(
    #             #     photo_size_country,
    #             #     file_path,
    #             #     file_name,
    #             #     session_key,
    #             #     uploaded_file.id,
    #             # )
    #             # service.make()
    #             # process_photos.apply_async(
    #             #     (
    #             #         photo_size_country,
    #             #         file_path,
    #             #         file_name,
    #             #         session_key,
    #             #         uploaded_file.id,
    #             #     )
    #             # )
    #         # return redirect("/prepare/")
    #         task = go_to_sleep.delay(5)
    #         # go_to_sleep()
    #         return render(request, self.template_name, {"task_id": task.task_id})
    #     else:
    #         context = {"form": form, "uploaded_files": uploaded_files}
    #         return render(request, self.template_name, context)


# def check_task_status(request):
#     task_id = request.GET.get("task_id")
#     task = AsyncResult(task_id)
#     return JsonResponse({"status": task.status})


class PrepareView(TemplateView):
    template_name = "prepared.html"

    def get_context_data(self, **kwargs):
        session_key = self.request.session.session_key
        context = super().get_context_data(**kwargs)

        prepared_images = UserFile.objects.filter(session=session_key).filter(
            edited=True
        )
        # Check if user made a payment
        paid_prepared_images = prepared_images.filter(paid=True)

        if paid_prepared_images.exists():
            show_prepared_images = prepared_images.filter(watermarked=False)
        else:
            show_prepared_images = prepared_images.filter(watermarked=True)

        context["prepared_images"] = show_prepared_images
        context["size"] = {
            "australia_passport": {
                "size": "413 x 531",
                "display_name": "Australia Passport",
            },
            "china_visa": {
                "size": "600 x600",
                "display_name": "China Visa",
            },
            "european_union_passport": {
                "size": "413 x 531",
                "display_name": "European Union Passport",
            },
            "schengen_visa": {
                "size": "413 x 531",
                "display_name": "Schengen Visa",
            },
            "us_passport": {
                "size": "600 x 600",
                "display_name": "US Passport",
            },
            "india_visa": {
                "size": "600 x 600",
                "display_name": "India Visa",
            },
            "japan_visa": {
                "size": "531 x 531",
                "display_name": "Japan Visa",
            },
            "us_visa": {
                "size": "600 x 600",
                "display_name": "US Visa",
            },
            "canada_visa": {
                "size": "413 x 531",
                "display_name": "Canada Visa",
            },
            "canada_passport": {
                "size": "590 x 826",
                "display_name": "Canada Passport",
            },
        }
        return context


class StripeAPI(APIView):
    def post(self, request, *args, **kwargs):
        service = StripeCreatePayment()
        intent = service.create_payment(request)
        print(intent)
        return Response({"clientSecret": intent["client_secret"]})
