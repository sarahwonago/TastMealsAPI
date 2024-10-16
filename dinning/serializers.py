from rest_framework import serializers
from .models import DiningTable

class DiningTableSerializer(serializers.ModelSerializer):
    """
    Serializer for the DiningTable model.
    Serializes the DinningTable model fields to JSON format.
    """
    class Meta:
        model = DiningTable
        fields = ['id', 'table_number']
        read_only_fields = ['id']
