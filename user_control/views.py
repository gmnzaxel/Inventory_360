from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import BasePermission, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from .models import User
from .serializer import UserSerializer
from rest_framework import generics, permissions

class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()



class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
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
        logout(request)
        return Response({"message": "Logout exitoso"}, status=status.HTTP_200_OK)
