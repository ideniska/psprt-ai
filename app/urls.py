from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing_page"),
    # path("service/", views.ServiceView.as_view(), name="service_page"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("choose/", views.ChooseView.as_view(), name="choose"),
    path("prepare/", views.PrepareView.as_view(), name="prepare"),
    path("status/<str:task_id>", views.task_status, name="status"),
]
