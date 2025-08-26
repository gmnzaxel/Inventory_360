from rest_framework import viewsets, status, generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializer import AdminRegistrationSerializer, UserCreateByAdminSerializer, UserSerializer
from .permissions import IsAdminUserCustom
from rest_framework_simplejwt.tokens import RefreshToken

class RegisterAdminView(generics.CreateAPIView):
    serializer_class = AdminRegistrationSerializer

class CreateUserByAdminView(generics.CreateAPIView):
    serializer_class = UserCreateByAdminSerializer
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_queryset(self):
        return User.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

class UserView(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.filter(business=user.business)
        return User.objects.filter(id=user.id)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Sesión cerrada correctamente"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Token inválido o ya expirado"}, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    """
    Vista para obtener los datos del usuario actualmente autenticado.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# --- NUEVA VISTA AÑADIDA ---
class DeleteUserView(APIView):
    """
    Vista para que un usuario elimine su propia cuenta.
    Si es el último administrador, elimina toda la empresa.
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        user = request.user

        if user.role == 'admin':
            other_admins_count = User.objects.filter(
                business=user.business, 
                role='admin'
            ).exclude(pk=user.pk).count()

            if other_admins_count == 0:
                user.business.delete()
                return Response({"message": "Empresa y cuenta eliminadas con éxito."}, status=status.HTTP_204_NO_CONTENT)
        
        user.delete()
        return Response({"message": "Cuenta eliminada con éxito."}, status=status.HTTP_204_NO_CONTENT)