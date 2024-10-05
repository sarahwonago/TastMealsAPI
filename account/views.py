
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.urls import reverse_lazy


class RoleBasedRedirectAPIView(APIView):
    """
    Endpoint for redirecting user based on their role.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
       if request.user.role == 'customer':
          role = request.user.role
          redirect_url = reverse_lazy('customer-home')
       else:
          role = request.user.role
          redirect_url = reverse_lazy('cafeadmin-home')
          
       response = {
          "role":role,
          "redirect_url":redirect_url
       }

       return Response(response, status=status.HTTP_200_OK)
