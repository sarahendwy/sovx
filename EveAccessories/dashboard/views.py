from typing import Any
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView, CreateView, DeleteView, UpdateView
from accessories.models import Category, Product, ProductImage
from .forms import CategoryForm, ProductForm
from django.urls import reverse_lazy

class DashboardView(TemplateView):
    template_name = 'dashboard/main.html'


class OrdersView(TemplateView):
    template_name = 'dashboard/orders.html'

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
    

class SettingsView(TemplateView):
    template_name = 'dashboard/settings.html'
