
from rest_framework import serializers
from .models import  Order

class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    """
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'is_paid', 'estimated_time', 'status', 'dining_table', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'order_items', 'total_price', 'is_paid', 'estimated_time', 'status', 'dining_table', 'created_at', 'updated_at']


