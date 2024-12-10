from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User

class UserView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email,
            'role': user.role
        })
