from rest_framework.serializers import ModelSerializer

from geocoder.models import Coordinates
from geocoder.utils import add_coordinates
from .models import Order
from .models import Position
from .models import Product


class PositionSerializer(ModelSerializer):
    class Meta:
        model = Position
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = PositionSerializer(
        many=True,
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'address',
            'first_name', 'last_name',
            'phonenumber', 'products'
        ]

        read_only_fields = ['id']

    def create(self, validated_data):
        address = validated_data['address']

        if not Coordinates.objects.filter(address=address).exists():
            add_coordinates(address)

        order = Order.objects.create(
            address=address,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phonenumber=validated_data['phonenumber']
        )

        for single_product_data in validated_data['products']:
            product = Product.objects.get(pk=single_product_data['product'].id)

            Position.objects.create(
                order=order,
                product=product,
                quantity=single_product_data['quantity'],
                cost=product.price * single_product_data['quantity']
            )

        return order
