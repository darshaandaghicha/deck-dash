from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.utils.timezone import now
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.auth.serializers import SignUpSerializer
from core.models import Otp
from utils.email_service import EmailService

User = get_user_model()


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # TODO
            plain_otp = Otp.generate_for_user(user)

            email_sent = EmailService.send_email(
                [user.email],
                "Sign Up OTP - DeckDash",
                "registration_otp",
                {"otp": plain_otp, "user": user.display_name},
            )
            if email_sent == 1:
                return Response(
                    {
                        "message": "User created successfully. Kindly check your email for TOTP which is valid for 5 minutes.",
                        "success": True,
                        "user": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {
                        "message": "Unable to send email to the user!",
                        "success": False,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {"messages": serializer.errors, "success": False},
            status=status.HTTP_400_BAD_REQUEST,
        )


class VerifyOtpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request) -> Response:
        user_id = request.data.get("user_id")
        otp = request.data.get("otp")
        intent = request.data.get("intent")

        if not all([user_id, otp, intent]):
            return Response(
                {"message": "Missing Required Fields", "success": False},
                status=status.HTTP_206_PARTIAL_CONTENT,
            )

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response(
                {"message": "User Not Found", "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active:
            return Response(
                {"message": "User Account Activated", "success": True},
                status=status.HTTP_400_BAD_REQUEST,
            )

        last_otp = Otp.objects.filter(user_id=user_id, intent=intent).last()
        if not last_otp:
            return Response(
                {"message": "No active OTP found", "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if last_otp.issued_at < (now() - timedelta(minutes=5)):
            last_otp.delete()
            return Response(
                {
                    "message": "Entered OTP is expired. Kindly use resend OTP to generate new one!",
                    "success": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_matches = check_password(otp, last_otp.otp_hash)

        if not otp_matches:
            return Response(
                {"message": "Invalid OTP", "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if intent == "registration":
            user.is_active = True
            user.verified_at = now()
            user.updated_at = now()
            user.save()

        last_otp.delete()
        return Response(
            {"message": "OTP verified", "success": True}, status=status.HTTP_200_OK
        )
