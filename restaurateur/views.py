from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Order, Product, Restaurant


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
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append (
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


def get_order_data(order):

    return {
        'id': order.id,
        'status': order.get_status_display(),
        'total_price': order.cost,
        'payment_method': order.get_payment_method_display(),
        'first_name': order.first_name,
        'last_name': order.last_name,
        'address': order.address,
        'restaurants': order.restaurants_executors,
        'phonenumber': order.phonenumber,
        'comment': order.comment
    }


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.filter (
        status=Order.NEW
    ).all_cost()

    restaurants = Restaurant.objects.all().prefetch_related('menu_items')

    restaurants_with_actual_positions = []
    for restaurant in restaurants:
        actual_products = restaurant.menu_items.filter(availability=True)
        actual_products_ids = [product.product.id for product in actual_products]
        restaurants_with_actual_positions.append (
            {
                'restaurant_id': restaurant.id,
                'adress': restaurant.address,
                'actual_positions_ids': actual_products_ids
            }
        )

    for order in orders:
        order.restaurants_executors = []
        order_positions = order.positions.all()
        order_products_ids = [position.product.id for position in order_positions]

        for restaurant in restaurants_with_actual_positions:
            if set(order_products_ids).issubset(restaurant['actual_positions_ids']):
                order.restaurants_executors.append(restaurant)
        
    context = {
        "order_items": [get_order_data(order) for order in orders],
    }

    return render(request, template_name='order_items.html', context=context)