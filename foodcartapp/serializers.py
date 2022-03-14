from turtle import position
from rest_framework.serializers import ModelSerializer

from .models import Order
from .models import Position


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = PositionSerializer (
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'address',
            'first_name',
            'last_name',
            'phonenumber',
            'products'
        ]