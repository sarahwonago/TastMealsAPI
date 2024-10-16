from rest_framework import serializers
from .models import RedemptionOption, RedemptionTransaction


class RedemptionOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for RedemptionOption.
    """
    fooditem_name = serializers.CharField(source="fooditem.name", read_only=True)
    
    class Meta:
        model = RedemptionOption
        fields = ['id', 'fooditem_name', 'points_required', 'description']

class RedemptionTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for RedemptionTransaction.
    """
    customer_username = serializers.CharField(source="customer.username", read_only=True)
    redemption_fooditem_name = serializers.CharField(source="redemption_option.fooditem.name", read_only=True)
    
    class Meta:
        model = RedemptionTransaction
        fields = ['id', 'customer_username','redemption_fooditem_name', 'points_redeemed', 'status', 'created_at']

