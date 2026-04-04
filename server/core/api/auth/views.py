from django.contrib.messages import success
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.api.auth.serializers import SignUpSerializer
from core.models import Otp


class SignUpView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # TODO
            plain_otp = Otp.generate_for_user(user)
            print(f"--------------------------------")
            print(f"OTP for {user.email}: {plain_otp}")
            print(f"--------------------------------")
            return Response(
                {
                    "message": "User created successfully. Kindly check your email for TOTP which is valid for 5 minutes.",
                    "success": True,
                    "user": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"messages": serializer.errors, "success": False},
            status=status.HTTP_400_BAD_REQUEST,
        )
