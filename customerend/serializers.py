
from rest_framework import serializers
from .models import CartItem, Order, Review, CustomerLoyaltyPoint
from django.utils import timezone


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


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """
    class Meta:
        model = Review
        fields = ['id', 'user', 'order', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'order']
    


class CustomerLoyaltyPointSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomerLoyaltyPoint model
    """
    class Meta:
        model = CustomerLoyaltyPoint
        fields = ['points']
        


