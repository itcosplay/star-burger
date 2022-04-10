import operator

from geopy import distance

from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Order, Product, Restaurant
from geocoder.models import Coordinates


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{
                item.restaurant_id:
                item.availability for item in product.menu_items.all()
            },
        }
        orderer_availability = [
            availability[restaurant.id] for restaurant in restaurants
        ]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def get_order_data(order, coordinates):
    # order_coordinates = Coordinates.objects.get(address=order.address)
    order_address = [
        coordinate for coordinate in coordinates if
        coordinate['address'] == order.address
    ][0]

    restaurants_with_distances = []
    for restaurant in order.restaurants_executors:
        restaurant_address = [
            coordinate for coordinate in coordinates
            if coordinate['address'] == restaurant['address']
        ][0]
        distance_restaurant_client = distance.distance(
            (order_address['lat'], order_address['lon']),
            (restaurant_address['lat'], restaurant_address['lon'])
        ).km

        restaurants_with_distances.append(
            {
                'restaurant': restaurant['address'],
                'distance_to_client': distance_restaurant_client
            }
        )

    restaurants_with_distances.sort(
        key=operator.itemgetter('distance_to_client')
    )

    return {
        'id': order.id,
        'status': order.get_status_display(),
        'total_price': order.cost,
        'payment_method': order.get_payment_method_display(),
        'first_name': order.first_name,
        'last_name': order.last_name,
        'address': order.address,
        'restaurants': restaurants_with_distances,
        'phonenumber': order.phonenumber,
        'comment': order.comment
    }


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.filter(
        status=Order.NEW
    ).get_total_cost().get_restaurants_executors()

    restaurants = Restaurant.objects.values('pk', 'address', 'name')
    orders_addresses = [order.address for order in orders]
    all_used_addresses = orders_addresses + [
        restaurant['address'] for restaurant in restaurants
    ]

    all_coordinates = Coordinates.objects.filter(
        address__in=all_used_addresses
    ).values('address', 'lat', 'lon')

    context = {
        "order_items": [
            get_order_data(order, all_coordinates) for order in orders
        ],
    }

    return render(request, template_name='order_items.html', context=context)
