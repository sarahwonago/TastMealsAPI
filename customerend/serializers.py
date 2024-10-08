
from rest_framework import serializers
from .models import CartItem, Order

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



class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """
    order_items = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CartItem.objects.all()
    )
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'order_items', 'total_price', 'is_paid', 'estimated_time', 'status', 'dining_table', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'order_items', 'total_price', 'is_paid', 'estimated_time', 'status', 'dining_table', 'created_at', 'updated_at']

   