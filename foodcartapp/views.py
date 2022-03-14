from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


from .models import Product
from .models import Order
from .models import Position

from .serializers import OrderSerializer
from .serializers import PositionSerializer


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    order_data = request.data
    # positions_data = order_data['products']
    # print('===')
    # print(positions_data)
    serializer = OrderSerializer(data=order_data)

    # serializer = ProductSerializer(data=positions_data)
    # for position in positions_data:
    #     serializer = PositionSerializer(data=position)
    #     serializer.is_valid(raise_exception=True)

    serializer.is_valid(raise_exception=True)

    order = Order.objects.create (
        address=order_data['address'],
        first_name=order_data['first_name'],
        last_name=order_data['last_name'],
        phonenumber=order_data['phonenumber']
    )

    for single_product_data in order_data['products']:
        product = Product.objects.get(pk=single_product_data['product'])

        Position.objects.create (
            order=order,
            product=product,
            quantity=single_product_data['quantity']
        )

    return JsonResponse({})


# {"products": [{"product": 1, "quantity": 1}], "first_name": "Петров", "last_name": "Петров", "phonenumber": "+79291000000", "address": "Москва"}