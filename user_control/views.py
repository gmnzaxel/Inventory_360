from rest_framework import viewsets
from .models import User
from .serializer import UserSerializer

class UserView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
