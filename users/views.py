from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from users.serializers import UserSerializer
from regular_user.serializers import UserProfileSerializer
from users.models import User
from users.utils import get_user_email, create_user_without_password

from rest_framework.authtoken.models import Token

class RecepcionOauthView(APIView):
    def post(self, request):
        data = request.data
        if "accessToken" not in data:
            return Response(
                {"error": _("accessToken is required")}, status=status.HTTP_400_BAD_REQUEST
            )
        access_token = data["accessToken"]
        email = get_user_email(access_token)
        print("email", email)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
        else:
            user = create_user_without_password(email)

        # login
        token, created = Token.objects.get_or_create(user=user)  # access token
        return Response({"token": str(token.key)}, status=status.HTTP_200_OK)


class UserProfileMe(APIView):
    """
    View to get user and user profile data from the current user
    get: return user and user profile data
    patch: update user and user profile data
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile_serializer = UserProfileSerializer(request.user.user_profile)
        user_serializer = UserSerializer(request.user)
        return Response(
            {"user": user_serializer.data, "user_profile": profile_serializer.data}
        )

    def patch(self, request):
        user_serializer = UserSerializer(
            data=request.data, instance=request.user, partial=True
        )
        if user_serializer.is_valid():
            profile_serializer = UserProfileSerializer(
                data=request.data, instance=request.user.user_profile, partial=True
            )
            if profile_serializer.is_valid():
                user_serializer.save()
                profile_serializer.save()

                return Response(
                    {
                        "user": user_serializer.data,
                        "user_profile": profile_serializer.data,
                    }
                )

            else:
                return Response(profile_serializer.errors)
        else:
            return Response(user_serializer.errors)
