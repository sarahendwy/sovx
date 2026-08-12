from collections import defaultdict
from typing import Any
from django.shortcuts import redirect, render
from django.http import JsonResponse
from .models import Order, OrderEntry, OrderLog
from products.models import Product
from django.views.generic import CreateView, DetailView
from .forms import OrderForm, SellWithUsForm, ContactUsForm
from dashboard.models import Setting

def order_success(request, order_id):
    return render(request, 'orders/order_success.html', context={'order_id': order_id})

class CreateOrder(CreateView):
    template_name = 'orders/create_order.html'
    form_class = OrderForm
    success_url = "/orders/success"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = cart.strip("-")
        if cart:
            cart_set = set(cart.split("-"))
            cart_products = []
            for pr in cart_set:
                if pr:  # Skip empty strings
                    try:
                        product_id = int(pr.split("#")[0])
                        cart_products.append(product_id)
                    except (ValueError, IndexError):
                        continue
            products = Product.objects.filter(id__in=cart_products)
            stocks = {product.id: product.stock for product in products}
        else:
            products = Product.objects.none()
            stocks = {}

        setting = Setting.objects.first()

        context['products'] = products
        context['stocks'] = stocks
        return context
    
    def form_valid(self, form):
        user = self.request.user
        
        # Check for undelivered orders limit (max 2)
        # Undelivered orders are those not "Delivered" or "Cancelled"
        undelivered_statuses = ['Pending Confirmation', 'Confirmed', 'In Delivery']
        
        if user.is_authenticated:
            # Check by authenticated user
            undelivered_count = Order.objects.filter(
                user=user,
                status__in=undelivered_statuses
            ).count()
        else:
            # Check by phone number for non-authenticated users
            phone = form.cleaned_data.get('phone') or form.data.get('phone')
            if phone:
                undelivered_count = Order.objects.filter(
                    phone=phone,
                    status__in=undelivered_statuses
                ).count()
            else:
                undelivered_count = 0
        
        if undelivered_count >= 2:
            form.add_error(
                None, 
                "You cannot have more than 2 undelivered orders at the same time. Please wait for your existing orders to be delivered before placing a new order."
            )
            return self.form_invalid(form)
        
        if user.is_authenticated:
            form.instance.user = user
        form.instance.status = "Pending Confirmation"
        form.instance.payment_account = form.data.get("payment_account")

        payment_proof = form.files.get('payment_proof')
        if payment_proof:
            form.instance.payment_proof = payment_proof

        # Get cart items
        if self.request.user.is_authenticated:
            cart = self.request.user.cart or ""
        else:
            cart = self.request.session.get('cart') or ""

        cart = cart.strip("-")
        if cart:
            cart_set = set(cart.split("-"))
            for pr in cart_set:
                if pr:  # Skip empty strings
                    try:
                        product_id = int(pr.split("#")[0])
                    except (ValueError, IndexError):
                        continue

        # Collect all quantity fields and validate
        order_items = []
        errors = []
        
        for field_name in form.data:
            if not field_name.startswith("quantity"):
                continue

            try:
                quantity = int(form.data[field_name])
            except (ValueError, TypeError):
                continue
            
            # Skip items with zero quantity
            if quantity <= 0:
                continue
            
            product_id = int(field_name.split("-")[-1])
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                errors.append(f"Product with ID {product_id} not found.")
                continue
            
            # Validate stock availability
            if product.stock == 0:
                errors.append(f"'{product.title}' is out of stock.")
                continue
            
            if quantity > product.stock:
                errors.append(f"Requested quantity for '{product.title}' ({quantity}) exceeds available stock ({product.stock}).")
                continue
            
            order_items.append({
                'product': product,
                'quantity': quantity
            })
        
        # Check if order has any items
        if not order_items:
            errors.append("Your order must contain at least one item.")
        
        # If there are errors, return form invalid with error messages
        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)
        
        # All validations passed, create the order
        order = form.save()
        order.payment_method = form.data.get("payment_method")
        order.order_total = order.shipping_fees
        
        # Clear cart
        if self.request.user.is_authenticated:
            self.request.user.cart = ""
            self.request.user.save()
        else:
            self.request.session['cart'] = ""
        
        # Create order entries and update stock
        for item in order_items:
            product = item['product']
            quantity = item['quantity']
            variant = item['variant']
            
            # Update product stock
            product.stock -= quantity
            product.save()
            
            # Create order entry
            entry = OrderEntry.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                variant=variant,
                price=product.price * quantity
            )
            order.order_total += entry.price
        
        if order.payment_method == "Cash on Delivery":
            order.status = "Confirmed"

        OrderLog.objects.create(
            order=order,
            content="Order Created"
        )

        order.save()
        return redirect(f"/order/success/{order.id}")


class SellWithUs(CreateView):
    template_name = 'sell_with_us.html'
    form_class = SellWithUsForm
    success_url = "/orders/success"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['slides'] = CONTACT_SLIDES
        return context

class ContactUs(CreateView):
    template_name = 'contact_us.html'
    form_class = ContactUsForm
    success_url = "/orders/success"


class OrderDetails(DetailView):
    model = Order
    template_name = 'orders/order_details.html'


CONTACT_SLIDES = [
    {
        "title": "اطلب من أي مكان",
        "text": "اطلب منتجاتك أونلاين من أي مكان وبأي كمية تناسب شغلك، بدون تعقيد أو التزام بحد أدنى.",
        "image_path": "images/sections/sell-with-us/order-anywhere.png",
    },
    {
        "title": "مراجعة وجودة مضمونة", 
        "text": "كل أوردر بيتم مراجعته بعناية، ومنتجات مختارة بجودة عالية تضمن رضاك ورضا عملاءك.",
        "image_path": "images/sections/sell-with-us/quality-review.png",
    },
    {
        "title": "استلم وزوّد مبيعاتك",  
        "text": "الأوردر بيوصلك لحد مكانك بسرعة، ويساعدك تزود مبيعاتك وتكسب ثقة عملاء أكتر.",
        "image_path": "images/sections/sell-with-us/grow-sales.png"
    },
]