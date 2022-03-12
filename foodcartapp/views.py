import json

from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view


from .models import Product
from .models import Order
from .models import Position


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
    # order_data = json.loads(request.body.decode())
    order_data = request.data

    order = Order.objects.create (
        address=order_data['address'],
        first_name=order_data['firstname'],
        last_name=order_data['lastname'],
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
