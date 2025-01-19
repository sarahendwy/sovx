from typing import Any
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from .models import Order, OrderEntry
from accessories.models import Product
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import OrderForm
from django.urls import reverse_lazy


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart = request.user.cart or ""
    else:
        cart = request.session.get('cart') or ""

    cart = cart.strip("-").strip("")
    if cart:
        product_ids = list(map(int, cart.split("-")))
        if product_ids:
            if product_id in product_ids:
                product_ids.remove(product_id)
            if "" in product_ids:
                product_ids.remove("")

            cart = "-".join(map(str, product_ids))
        
        if request.user.is_authenticated:
            request.user.cart = cart
            request.user.save()

        request.session['cart'] = cart

    return JsonResponse({"status": "ok"}, status=200)


class CartView(TemplateView):
    template_name = 'cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = cart.strip("-")
        if cart:
            product_ids = list(map(int, cart.split("-")))
            products = Product.objects.filter(id__in=product_ids)
        else:
            products = []

        context['products'] = products
        return context


class CreateOrder(LoginRequiredMixin, CreateView):
    template_name = 'create_order.html'
    form_class = OrderForm
    # success_url = reverse_lazy("payment")

    def get_shipping_fees(self, governorate: str = "") -> int:
        return 50

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        products = Product.objects.filter(id__in=self.request.user.products_in_cart)
        stocks = {product.id: product.stock for product in products}

        context['products'] = products
        context['stocks'] = stocks
        context['shipping_cost'] = self.get_shipping_fees()
        
        return context
    
    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        user = self.request.user

        initial['name'] = user.full_name
        initial['email'] = user.email
        initial['phone'] = user.phone
        initial['address'] = user.address
        initial['governorate'] = user.governorate
        initial['city'] = user.city

        return initial


    def form_valid(self, form):
        user = self.request.user
        form.instance.user = user
        form.instance.status = "Pending Confirmation"
        shipping_fees = self.get_shipping_fees()
        form.instance.order_total = shipping_fees + sum(
            product.discounted_price * form.cleaned_data['quanitites'][str(product.id)]
            for product in form.instance.products
        )

        order = form.save()

        for field_name in form["data"]:
            if not field_name.startswith("quantity_"):
                continue
            
            quanity = int(form["data"][field_name])
            product_id = field_name.split("-")[-1]
            product = Product.objects.get(id=product_id)

            product.stock -= quanity
            product.save()

            entry = OrderEntry.objects.create(
                order=order,
                product=product,
                quantity=quanity,
                price=product.discounted_price * quanity
            )
            entry.save()

        return HttpResponseRedirect(self.get_success_url())



    