from datetime import datetime, timezone
from typing import Any
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView, FormView

from orders.models import Order
from .forms import CategoryForm, ProductForm, SettingsForm
from .models import Setting
from accessories.models import Category, Product, ProductImage

class DashboardView(TemplateView):
    template_name = 'dashboard/main.html'

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
        if query:
            return self.model.objects.filter(name__icontains=query)
        else:
            return super().get_queryset()

class AddCategoryView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/category/add_category.html'
    success_url = reverse_lazy('admin_categories')

class DeleteCategoryView(DeleteView):
    model = Category
    success_url = reverse_lazy('admin_categories')
    template_name = "dashboard/confirm_delete.html"

class ProductsView(CategoriesView):
    template_name = 'dashboard/product/products.html'
    model = Product
    context_object_name = "products"

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
                ProductImage.objects.create(product=self.object,image=f)

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
                ProductImage.objects.create(product=self.object,image=f)

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
