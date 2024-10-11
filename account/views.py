import logging
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class RoleBasedRedirectAPIView(APIView):
   """
   API view to redirect users based on their role.

   Returns:
      role (str): User's role.
      redirect_url (str): URL for redirecting based on the role.
   """

   permission_classes = [IsAuthenticated]

   def get(self, request):
      role = request.user.role

      if role == 'customer':
         redirect_url = reverse_lazy('customer-home')
      else:
         redirect_url = reverse_lazy('cafeadmin-home')

      logger.info(f"User {request.user.name} with role {role} was redirected  to {redirect_url}")
          
      response = {
         "role":role,
         "redirect_url":redirect_url
      }

      return Response(response, status=status.HTTP_200_OK)


