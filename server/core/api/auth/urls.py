from django.urls import path
from .views import SignUpView, VerifyOtpView

urlpatterns = [
    path(
        "signup/",
        SignUpView.as_view(),
        name="signup",
    ),
    path("verify-otp/", VerifyOtpView.as_view(), name="verify-otp"),
]
