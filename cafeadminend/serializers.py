from rest_framework import serializers
from .models import Category, DiningTable, FoodItem, SpecialOffer, Notification, RedemptionOption, RedemptionTransaction


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
    #category_name = serializers.SerializerMethodField()

    class Meta:
        model = FoodItem
        fields = [
            'id', 'category', 'name', 'price', 'image', 'description',
            'created_at', 'updated_at', 'is_available'
        ]
        read_only_fields = [
            'id', 'category','created_at', 'updated_at'
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


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


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

