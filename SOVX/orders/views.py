from typing import Any
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import Order, OrderEntry, OrderLog
from products.models import ProductBuyingOption
from django.views.generic import CreateView, TemplateView
from .forms import OrderForm, SellWithUsForm, ContactUsForm

class CreateOrder(CreateView):
    template_name = 'orders/create.html'
    form_class = OrderForm
    success_url = reverse_lazy('thank_you')

    def form_valid(self, form):
        cart_items = form.cleaned_data.get('user_cart') or []

        order_entries = []
        errors = []

        for raw_item in cart_items:
            try:
                option_id = int(raw_item.get('id'))
                quantity = int(raw_item.get('quantity'))
            except (TypeError, ValueError, AttributeError):
                continue

            if quantity <= 0:
                continue

            try:
                option = ProductBuyingOption.objects.select_related('product').get(id=option_id)
            except ProductBuyingOption.DoesNotExist:
                errors.append("أحد المنتجات في سلتك لم يعد متاحًا.")
                continue

            # Stock is re-checked here against the DB, not trusted from the
            # client - the cart's snapshot can be stale by submit time.
            if option.stock <= 0:
                errors.append(f"'{option.product.title} - {option.name}' غير متوفر حاليًا.")
                continue

            if quantity > option.stock:
                errors.append(
                    f"الكمية المطلوبة من '{option.product.title} - {option.name}' "
                    f"({quantity}) أكبر من المتاح ({option.stock})."
                )
                continue

            order_entries.append({'option': option, 'quantity': quantity})

        if not order_entries:
            errors.append("سلتك فارغة. من فضلك أضف منتجات قبل إرسال الطلب.")

        if errors:
            for error in errors:
                form.add_error(None, error)
            return self.form_invalid(form)

        # All validations passed - create the order and its entries.
        order = form.save()

        order_total = 0
        for entry_data in order_entries:
            option = entry_data['option']
            quantity = entry_data['quantity']

            option.stock -= quantity
            option.save()

            entry = OrderEntry.objects.create(
                order=order,
                product_option=option,
                quantity=quantity,
                price=option.price * quantity,
            )
            order_total += entry.price

        order.order_total = order_total + order.shipping_fees
        order.save()

        OrderLog.objects.create(order=order, content="Order Created")

        return redirect('thank_you')


class SellWithUs(CreateView):
    template_name = 'sell_with_us.html'
    form_class = SellWithUsForm
    success_url = reverse_lazy('thank_you')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['slides'] = CONTACT_SLIDES
        return context

class ContactUs(CreateView):
    template_name = 'contact_us.html'
    form_class = ContactUsForm
    success_url = reverse_lazy('thank_you')

class ThankYou(TemplateView):
    template_name = 'orders/thank_you.html'


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