from rest_framework import serializers
from .models import Category, DiningTable, FoodItem, SpecialOffer
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.

    Serializes the Category model fields to JSON format.

    Meta:
        model (Category): The model to be serialized.
        fields (list): Fields to be included in the serialization.
    """

    class Meta:
        model = Category
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']


class DiningTableSerializer(serializers.ModelSerializer):
    """
    Serializer for the DiningTable model.
    Serializes the DinningTable model fields to JSON format.
    """
    class Meta:
        model = DiningTable
        fields = ['id', 'table_number']
        read_only_fields = ['id']


class FoodItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the FoodItem model.
    """

    category = serializers.CharField(source='category.name', read_only=True)

    #category_name = serializers.SerializerMethodField()


    class Meta:
        model = FoodItem
        fields = [
            'id', 'category', 'name', 'price', 'description'
        ]
        read_only_fields = [
            'id', 'category'
        ]


    # def get_category_name(self, obj):
    #     """
    #     Returns the name of the category the food item belongs to.
    #     """
    #     return obj.category.name



# class SpecialOfferSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the SpecialOffer model.

#     Only the food item name is returned instead of the entire food item details.
#     """
#     # if fooditem has __str__ method that returns the fooditem name, then we
#     # can fetch it using StringRelatedField
#     fooditem = serializers.StringRelatedField()

#     class Meta:
#         model = SpecialOffer
#         fields = '__all__'


class SpecialOfferSerializer(serializers.ModelSerializer):
    """
    Serializer for the SpecialOffer model.

    Uses SerializerMethodField to return only the food item name.
    """
    fooditem_name = serializers.SerializerMethodField()

    class Meta:
        model = SpecialOffer
        fields = ['id', 'name', 'fooditem_name', 'discount_percentage', 'start_date', 'end_date', 'description', 'is_active', 'price']
        

    def get_fooditem_name(self, obj):
        """
        Returns the name of the food item the special offer applies to.
        """
        return obj.fooditem.name

