from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, ListView
from django.contrib.admin.views.decorators import staff_member_required
from accessories.models import Category

class DashboardView(TemplateView):
    template_name = 'dashboard/main.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class OrdersView(TemplateView):
    template_name = 'dashboard/orders.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CategoriesView(ListView):
    template_name = 'dashboard/categories.html'
    model = Category
    paginate_by = 24
    context_object_name = "categories"

    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            return self.model.objects.filter(name__icontains=query)
        else:
            return super().get_queryset()

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ProductsView(TemplateView):
    template_name = 'dashboard/products.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SettingsView(TemplateView):
    template_name = 'dashboard/settings.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
