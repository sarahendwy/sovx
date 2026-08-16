from datetime import datetime, timezone
from typing import Any
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView
from django.utils import timezone as django_timezone
from django.db.models import Sum

from orders.models import Order, OrderEntry
from .forms import (
    ProductForm, ProductBuyingOptionFormSet, SettingsForm, ProductListForm, SectionForm, SellWithUsCardForm,
    ShippingFeeForm, ProductNutritionsValueFormSet
)
from .models import Setting, ProductList, Section, SellWithUsCard, City, ShippingFee
from products.models import Product

class DashboardView(TemplateView):
    template_name = 'dashboard/main.html'
    
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        
        # Get time periods
        now = django_timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate statistics for MONTH
        month_orders_created = Order.objects.filter(created_at__gte=month_start).count()
        month_orders_completed = Order.objects.filter(
            status='Delivered',
            delivered_at__gte=month_start
        ).count()
        month_order_value = Order.objects.filter(created_at__gte=month_start).aggregate(
            total=Sum('order_total')
        )['total'] or 0
        month_items_sold = OrderEntry.objects.filter(
            order__status='Delivered',
            order__delivered_at__gte=month_start
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate statistics for YEAR
        year_orders_created = Order.objects.filter(created_at__gte=year_start).count()
        year_orders_completed = Order.objects.filter(
            status='Delivered',
            delivered_at__gte=year_start
        ).count()
        year_order_value = Order.objects.filter(created_at__gte=year_start).aggregate(
            total=Sum('order_total')
        )['total'] or 0
        year_items_sold = OrderEntry.objects.filter(
            order__status='Delivered',
            order__delivered_at__gte=year_start
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Calculate statistics for ALL TIME
        all_time_orders_created = Order.objects.count()
        all_time_orders_completed = Order.objects.filter(status='Delivered').count()
        all_time_order_value = Order.objects.aggregate(
            total=Sum('order_total')
        )['total'] or 0
        all_time_items_sold = OrderEntry.objects.filter(
            order__status='Delivered'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # Pending orders (same for all periods)
        pending_orders = Order.objects.filter(status='Pending Confirmation').count()
        
        # Get latest completed orders (limit to 10)
        latest_completed_orders = Order.objects.filter(
            status='Delivered'
        ).order_by('-delivered_at')[:10]
        
        context.update({
            # Month statistics
            'month_orders_created': month_orders_created,
            'month_orders_completed': month_orders_completed,
            'month_order_value': month_order_value,
            'month_items_sold': month_items_sold,
            
            # Year statistics
            'year_orders_created': year_orders_created,
            'year_orders_completed': year_orders_completed,
            'year_order_value': year_order_value,
            'year_items_sold': year_items_sold,
            
            # All time statistics
            'all_time_orders_created': all_time_orders_created,
            'all_time_orders_completed': all_time_orders_completed,
            'all_time_order_value': all_time_order_value,
            'all_time_items_sold': all_time_items_sold,
            
            # Common
            'pending_orders': pending_orders,
            'latest_completed_orders': latest_completed_orders,
        })
        
        return context

class ProductsView(ListView):
    template_name = 'dashboard/product/products.html'
    model = Product
    context_object_name = "products"
    paginate_by = 24
    
    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = self.model.objects.all()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset.order_by('-created_at')


    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get('query') or "Search..."
        return context

class ProductBuyingOptionsFormsetMixin:
    """Adds the ProductBuyingOption inline formset to the product add/edit views
    and requires at least one buying option before the product can be saved."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault(
            'buying_options_formset',
            ProductBuyingOptionFormSet(self.request.POST or None, instance=self.object),
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        buying_options_formset = context['buying_options_formset']

        if not buying_options_formset.is_valid():
            return self.form_invalid(form)

        self.object = form.save()
        buying_options_formset.instance = self.object
        buying_options_formset.save()

        return redirect(self.get_success_url())

class ProductNutritionsValueFormsetMixin:
    """Adds the ProductBuyingOption inline formset to the product add/edit views
    and requires at least one buying option before the product can be saved."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault(
            'nutrition_values_formset',
            ProductNutritionsValueFormSet(self.request.POST or None, instance=self.object),
        )
        return context

    def form_valid(self, form):
        context = self.get_context_data(form=form)
        nutrition_values_formset = context['nutrition_values_formset']

        if not nutrition_values_formset.is_valid():
            return self.form_invalid(form)

        self.object = form.save()
        nutrition_values_formset.instance = self.object
        nutrition_values_formset.save()

        return redirect(self.get_success_url())

class AddProductView(ProductBuyingOptionsFormsetMixin, ProductNutritionsValueFormsetMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/product/add_product.html'
    success_url = reverse_lazy('admin_products')

class EditProductView(ProductBuyingOptionsFormsetMixin, ProductNutritionsValueFormsetMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/product/edit_product.html'
    success_url = reverse_lazy('admin_products')

class DeleteProductView(DeleteView):
    model = Product
    success_url = reverse_lazy('admin_products')
    template_name = "dashboard/confirm_delete.html"

class SettingsView(UpdateView):
    template_name = 'dashboard/settings.html'
    form_class = SettingsForm
    success_url = reverse_lazy('admin_settings')

    def get_object(self, queryset=None):
        return Setting.objects.first()

class ProductListsView(ListView):
    template_name = 'dashboard/product_list/product_lists.html'
    model = ProductList
    context_object_name = "product_lists"

class AddProductListView(CreateView):
    model = ProductList
    form_class = ProductListForm
    template_name = 'dashboard/product_list/add_product_list.html'
    success_url = reverse_lazy('admin_product_lists')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('select_all_products'):
            self.object.product_ids.clear()
        return response

class EditProductListView(UpdateView):
    model = ProductList
    form_class = ProductListForm
    template_name = 'dashboard/product_list/edit_product_list.html'
    success_url = reverse_lazy('admin_product_lists')

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get('select_all_products'):
            self.object.product_ids.clear()
        return response

class DeleteProductListView(DeleteView):
    model = ProductList
    success_url = reverse_lazy('admin_product_lists')
    template_name = "dashboard/confirm_delete.html"

class SectionsView(ListView):
    template_name = 'dashboard/section/sections.html'
    model = Section
    context_object_name = "sections"

class AddSectionView(CreateView):
    model = Section
    form_class = SectionForm
    template_name = 'dashboard/section/add_section.html'
    success_url = reverse_lazy('admin_sections')

class EditSectionView(UpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'dashboard/section/edit_section.html'
    success_url = reverse_lazy('admin_sections')

class DeleteSectionView(DeleteView):
    model = Section
    success_url = reverse_lazy('admin_sections')
    template_name = "dashboard/confirm_delete.html"

class SellWithUsCardsView(ListView):
    template_name = 'dashboard/sell_with_us_card/sell_with_us_cards.html'
    model = SellWithUsCard
    context_object_name = "sell_with_us_cards"

class AddSellWithUsCardView(CreateView):
    model = SellWithUsCard
    form_class = SellWithUsCardForm
    template_name = 'dashboard/sell_with_us_card/add_sell_with_us_card.html'
    success_url = reverse_lazy('admin_sell_with_us_cards')

class EditSellWithUsCardView(UpdateView):
    model = SellWithUsCard
    form_class = SellWithUsCardForm
    template_name = 'dashboard/sell_with_us_card/edit_sell_with_us_card.html'
    success_url = reverse_lazy('admin_sell_with_us_cards')

class DeleteSellWithUsCardView(DeleteView):
    model = SellWithUsCard
    success_url = reverse_lazy('admin_sell_with_us_cards')
    template_name = "dashboard/confirm_delete.html"

class ShippingFeesView(ListView):
    template_name = 'dashboard/shipping_fee/shipping_fees.html'
    model = ShippingFee
    context_object_name = "shipping_fees"

    def get_queryset(self):
        return super().get_queryset().select_related('governorate', 'city')

class AddShippingFeeView(CreateView):
    model = ShippingFee
    form_class = ShippingFeeForm
    template_name = 'dashboard/shipping_fee/add_shipping_fee.html'
    success_url = reverse_lazy('admin_shipping_fees')

class EditShippingFeeView(UpdateView):
    model = ShippingFee
    form_class = ShippingFeeForm
    template_name = 'dashboard/shipping_fee/edit_shipping_fee.html'
    success_url = reverse_lazy('admin_shipping_fees')

class DeleteShippingFeeView(DeleteView):
    model = ShippingFee
    success_url = reverse_lazy('admin_shipping_fees')
    template_name = "dashboard/confirm_delete.html"


def _parse_id(value):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def get_cities(request):
    """Cities belonging to `?governorate=<id>`, for the cascading
    governorate -> city selects (see static/js/locations.js)."""
    governorate_id = _parse_id(request.GET.get('governorate'))
    if governorate_id is None:
        return JsonResponse({"error": "A valid governorate id is required."}, status=400)

    cities = City.objects.filter(governorate_id=governorate_id).order_by('name_en').values('id', 'name_ar', 'name_en')
    return JsonResponse({"cities": list(cities)})


def get_shipping_fee(request):
    """Shipping cost for `?governorate=<id>&city=<id>` (city optional),
    used by the calculateShippingFee() JS helper (static/js/locations.js).
    `fee` is null when no fee has been configured for that governorate."""
    governorate_id = _parse_id(request.GET.get('governorate'))
    if governorate_id is None:
        return JsonResponse({"error": "A valid governorate id is required."}, status=400)

    city_param = request.GET.get('city')
    city_id = _parse_id(city_param) if city_param else None

    return JsonResponse({"fee": ShippingFee.get_fee(governorate_id, city_id)})

class OrdersView(TemplateView):
    template_name = 'dashboard/orders/orders.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        if query:
            all_orders = Order.objects.filter(name__icontains=query)
        else:
            all_orders = Order.objects.all()

        context["query"] = query or "Search..."
        context["pending_orders"] = all_orders.filter(status="Pending Confirmation")[:50]
        context["confirmed_orders"] = all_orders.filter(status="Confirmed")[:50]
        context["in_delivery_orders"] = all_orders.filter(status="In Delivery")[:50]

        return context
    

def confirm_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Confirmed"
    order.save()
    return redirect('admin_orders')

def reject_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Cancelled"
    order.save()

    for entry in order.entries.all():
        entry.product.stock += entry.quantity
        entry.product.save()

    return redirect('admin_orders')

def deliver_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "In Delivery"
    order.save()
    return redirect('admin_orders')

def complete_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order.status = "Delivered"
    order.delivered_at = datetime.now(timezone.utc)
    order.save()
    return redirect('admin_orders')
