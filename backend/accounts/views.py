from django.contrib.auth import authenticate, login
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers as s, tokens


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = s.AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return models.Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        first = not self.get_queryset().exists()
        serializer.save(user=self.request.user, **({'is_default': True} if first else {}))


def auth_response(user):
    return Response({'token': tokens.create(user), 'user': s.UserSerializer(user).data})


class Register(APIView):
    def post(self, request):
        ser = s.RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        return auth_response(ser.save())


class Login(APIView):
    def post(self, request):
        user = authenticate(request, username=str(request.data.get('email', '')).lower(),
                            password=request.data.get('password', ''))
        if not user:
            return Response({'detail': 'Wrong email or password.'}, status=status.HTTP_400_BAD_REQUEST)
        return auth_response(user)


class Me(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(s.UserSerializer(request.user).data)

    def delete(self, request):  # logout
        tokens.revoke(request.auth)
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminSession(APIView):
    """Signs a staff user into the Django admin (session cookie) using their shop login token."""
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        login(request._request, request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
