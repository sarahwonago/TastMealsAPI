
from rest_framework import serializers
from .models import CustomerLoyaltyPoint



class CustomerLoyaltyPointSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomerLoyaltyPoint model
    """
    class Meta:
        model = CustomerLoyaltyPoint
        fields = ['points']
        
