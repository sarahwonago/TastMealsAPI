from rest_framework import serializers
from .models import Category, DiningTable


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

