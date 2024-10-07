from rest_framework import serializers
from .models import Category, DiningTable, FoodItem, SpecialOffer


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.

    Serializes the Category model fields to JSON format.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class DiningTableSerializer(serializers.ModelSerializer):
    """
    Serializer for the DiningTable model.
    Serializes the DinningTable model fields to JSON format.
    """
    class Meta:
        model = DiningTable
        fields = ['id', 'table_number', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FoodItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the FoodItem model.
    """

    category = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'id', 'category', 'name', 'price', 'image', 'description',
            'created_at', 'updated_at', 'is_available'
        ]
        read_only_fields = [
            'id', 'category','created_at', 'updated_at'
        ]

    
        
