
from rest_framework import serializers
from .models import CartItem

class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for CartItem model.

    """
    
    fooditem_name = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'fooditem_name', 'quantity', 'price', 'total_price', 'created_at']
        read_only_fields = ['id', 'price', 'total_price', 'created_at']

    def validate_quantity(self, value):
        """Ensure that the quantity is a positive integer."""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value
    
    def get_fooditem_name(self, obj):
        """
        Gets the fooditem name
        """
        return obj.fooditem.name
