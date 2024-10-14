
from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    """
    class Meta:
        model = Review
        fields = ['id', 'user', 'order', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at', 'order']
    

