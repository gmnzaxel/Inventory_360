from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializer import AdminRegistrationSerializer, UserCreateSerializer, UserSerializer
from .permissions import IsAdminUserCustom
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action

class RegisterAdminView(generics.CreateAPIView):
    serializer_class = AdminRegistrationSerializer

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.filter(business=self.request.user.business)

    def perform_create(self, serializer):
        serializer.save(business=self.request.user.business)

    @action(detail=True, methods=['post'], url_path='set-password')
    def set_password(self, request, pk=None):
        """Admin-only: set a new password for a user in the same business."""
        user = self.get_object()
        password = request.data.get('password') or ''
        password2 = request.data.get('password2') or ''
        if password != password2:
            return Response({"password": "Las contraseÃ±as no coinciden."}, status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 8:
            return Response({"password": "La contraseÃ±a debe tener al menos 8 caracteres."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)
        user.save()
        return Response({"detail": "ContraseÃ±a actualizada."}, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "SesiÃ³n cerrada correctamente"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Token invÃ¡lido o ya expirado"}, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        """Change own password: expects old_password, new_password, new_password2."""
        old = request.data.get('old_password') or ''
        new = request.data.get('new_password') or ''
        new2 = request.data.get('new_password2') or ''
        if not request.user.check_password(old):
            return Response({"old_password": "La contraseÃ±a actual es incorrecta."}, status=status.HTTP_400_BAD_REQUEST)
        if new != new2:
            return Response({"new_password": "Las contraseÃ±as no coinciden."}, status=status.HTTP_400_BAD_REQUEST)
        if len(new) < 8:
            return Response({"new_password": "La contraseÃ±a debe tener al menos 8 caracteres."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(new)
        request.user.save()
        return Response({"detail": "ContraseÃ±a actualizada."}, status=status.HTTP_200_OK)

class DeleteUserView(APIView):
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
                return Response({"message": "Empresa y cuenta eliminadas con Ã©xito."}, status=status.HTTP_204_NO_CONTENT)
        
        user.delete()
        return Response({"message": "Cuenta eliminada con Ã©xito."}, status=status.HTTP_204_NO_CONTENT)


