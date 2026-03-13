from datetime import datetime, timezone
from typing import Any
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView, FormView
from django.utils import timezone as django_timezone
from django.db.models import Sum, Count

from orders.models import Order, OrderEntry
from .forms import CategoryForm, ProductForm, SettingsForm
from .models import Setting
from accessories.models import Category, Product, ProductImage

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

class CategoriesView(ListView):
    template_name = 'dashboard/category/categories.html'
    model = Category
    paginate_by = 24
    context_object_name = "categories"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get('query') or "Search categories..."
        return context


    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = self.model.objects.all()
        if query:
            queryset = queryset.filter(name__icontains=query)
        return queryset.order_by('display_order', 'name')

class AddCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/category/add_category.html'
    success_url = reverse_lazy('admin_categories')

class EditCategoryView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/category/add_category.html'
    success_url = reverse_lazy('admin_categories')

class DeleteCategoryView(DeleteView):
    model = Category
    success_url = reverse_lazy('admin_categories')
    template_name = "dashboard/confirm_delete.html"

def category_discount(request, pk):
    category = Category.objects.get(pk=pk)
    if request.method == 'POST':
        discount = request.POST.get('discount')
        if discount:
            category.products.update(discount=discount)
    return redirect('edit_category', pk=pk)

class ProductsView(CategoriesView):
    template_name = 'dashboard/product/products.html'
    model = Product
    context_object_name = "products"
    
    def get_queryset(self):
        query = self.request.GET.get('query')
        queryset = self.model.objects.all()
        if query:
            queryset = queryset.filter(title__icontains=query)
        return queryset.order_by('-created_at')

class AddProductView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/product/add_product.html'
    success_url = reverse_lazy('admin_products')

    def form_valid(self, form):
        self.object = form.save()

        files = self.request.FILES.getlist('images')
        if files:
            for f in files:
                ProductImage.objects.create(product=self.object, image=f)

        image_urls_value = form.cleaned_data.get("image_urls") or ""
        if image_urls_value:
            for raw_url in image_urls_value.splitlines():
                url = raw_url.strip()
                if url:
                    ProductImage.objects.create(product=self.object, image_url=url)

        return super().form_valid(form)

class EditProductView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'dashboard/product/edit_product.html'
    success_url = reverse_lazy('admin_products')

    def form_valid(self, form):
        clear_old_images = form.cleaned_data.get("clear_old_images")
        if clear_old_images:
            for image in self.object.images.all():
                image.delete()

        files = self.request.FILES.getlist('images')
        if files:
            for f in files:
                ProductImage.objects.create(product=self.object, image=f)

        image_urls_value = form.cleaned_data.get("image_urls") or ""
        if image_urls_value:
            for raw_url in image_urls_value.splitlines():
                url = raw_url.strip()
                if url:
                    ProductImage.objects.create(product=self.object, image_url=url)

        return super().form_valid(form)

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

class OrdersView(TemplateView):
    template_name = 'dashboard/orders/orders.html'

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('query')
        if query:
            all_orders = Order.objects.filter(name__icontains=query)
        else:
            all_orders = Order.objects.all()

        context["query"] = query or "Search categories..."
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
