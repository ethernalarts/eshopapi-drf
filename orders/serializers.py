from rest_framework import serializers
from .models import Orders, OrderItems


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = '__all__'


class OrdersSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField(method_name="get_order_items", read_only=True)

    class Meta:
        model = Orders
        fields = '__all__'

    def get_order_items(self, obj):
        order_items = obj.order_items.all()
        serializer = OrderItemsSerializer(order_items, many=True)
        return serializer.data