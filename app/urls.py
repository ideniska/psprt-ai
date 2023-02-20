from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.LandingPageView.as_view(), name="landing_page"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("choose/", views.ChooseView.as_view(), name="choose"),
    path("prepared/", views.PrepareView.as_view(), name="prepare"),
    # path("payment/", views.PrepareView.as_view(), name="payment"),
    path("prepare-backend/", views.PrepareBackend.as_view(), name="prepare_backend"),
    path(
        "create-payment-intent/",
        views.StripeAPI.as_view(),
        name="create_payment",
    ),
]
