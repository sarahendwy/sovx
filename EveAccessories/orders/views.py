from collections import defaultdict
from typing import Any
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import Order, OrderEntry, OrderLog
from accessories.models import Product
from django.views.generic import CreateView, TemplateView, DetailView
from .forms import OrderForm
from dashboard.models import Setting
from django.forms.models import model_to_dict


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart = request.user.cart or ""
    else:
        cart = request.session.get('cart') or ""

    cart = set(cart.strip("-").split("-"))

    for pr in list(cart):
        pr_id = pr.split("#")[0]
        if str(product_id) == pr_id:
            cart.remove(pr)

    cart = "-".join(list(cart))

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
            product_ids = [int(pr.split("#")[0]) for pr in cart.split("-")]
            products = Product.objects.filter(id__in=product_ids)
        else:
            products = []

        context['products'] = products
        return context

def order_success(request, order_id):
    return render(request, 'orders/order_success.html', context={'order_id': order_id})

class CreateOrder(CreateView):
    template_name = 'orders/create_order.html'
    form_class = OrderForm
    success_url = "/order/success"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = set(cart.strip("-").split("-"))
        cart_products = [int(pr.split("#")[0]) for pr in cart]
        products = Product.objects.filter(id__in=cart_products)
        stocks = {product.id: product.stock for product in products}
        variants = defaultdict(lambda: 1)
        for pr in cart:
            variants[int(pr.split("#")[0])] = pr.split("#")[1]

        context['payment_proof'] = Setting.objects.first().payment_image.url
        context['products'] = products
        context['stocks'] = stocks
        context['variants'] = variants
        context['shipping_costs'] = model_to_dict(Setting.objects.first())
        context['shipping_costs'].pop("payment_image")
        context['shipping_costs'].pop("hero_image")
        return context
    
    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated:
            form.instance.user = user
        form.instance.status = "Pending Confirmation"
        form.instance.payment_account = form.data.get("payment_account")

        payment_proof = form.files.get('payment_proof')
        if payment_proof:
            form.instance.payment_proof = payment_proof

        order = form.save()
        order.payment_method = form.data.get("payment_method")
        order.order_total = order.shipping_fees
        variants = defaultdict(lambda: 1)
        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
            self.request.user.cart = ""
        else:
            cart = self.request.session.get('cart') or ""
            self.request.session['cart'] = ""

        cart = set(cart.strip("-").split("-"))
        for pr in cart:
            variants[int(pr.split("#")[0])] = pr.split("#")[1]
        for field_name in form.data:
            if not field_name.startswith("quantity"):
                continue

            quantity = int(form.data[field_name])
            
            product_id = int(field_name.split("-")[-1])
            product = Product.objects.get(id=product_id)
            if quantity > product.stock:
                return self.form_invalid(form)
            
            product.stock -= quantity
            product.save()

            entry = OrderEntry.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                variant=variants.get(product.id, 1),
                price=product.discounted_price * quantity
            )
            order.order_total += entry.price
            if order.payment_method == "Cash on Delivery":
                order.status = "Confirmed"

            entry.save()

        OrderLog.objects.create(
            order=order,
            content="Order Created"
        )

        order.save()
        return redirect(f"/order/success/{order.id}")



class OrderDetails(DetailView):
    model = Order
    template_name = 'orders/order_details.html'
    