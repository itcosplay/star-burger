from rest_framework.serializers import ModelSerializer

from .models import Order
from .models import Position
from .models import Product


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
            'id', 'address',
            'first_name', 'last_name',
            'phonenumber', 'products'
        ]

        read_only_fields = ['id']

    def create(self, validated_data):
        order = Order.objects.create (
            address=validated_data['address'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phonenumber=validated_data['phonenumber']
        )
        0/0
        for single_product_data in validated_data['products']:
            product = Product.objects.get(pk=single_product_data['product'].id)

            Position.objects.create (
                order=order,
                product=product,
                quantity=single_product_data['quantity']
            )

        return order