from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth import authenticate
from .models import User
from .serializer import UserSerializer

class IsCompanyAdmin(BasePermission):
    """
    Permiso que solo da acceso a usuarios autenticados con role == 'admin'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )

class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return []
        return [IsAuthenticated()]

class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            return Response({
                "message": "Login exitoso",
                "name": user.name,
                "email": user.email,
                "role": user.role
            }, status=status.HTTP_200_OK)
        return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
