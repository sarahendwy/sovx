from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.urls import reverse_lazy, reverse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views import generic

from .forms import *
from .tokens import account_activation_token, send_verification_email


class Login(LoginView):
    form_class = LoginForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        
        if self.request.user.is_staff or self.request.user.is_superuser:
            return reverse('admin_dashboard')

        else:
            return reverse('index')

    def form_valid(self, form):
        user = form.get_user()
        if user:
            login(self.request, user)
            return HttpResponseRedirect(self.get_default_redirect_url())
        else:
            return self.form_invalid(form)


class CreateAccount(generic.CreateView):
    model = User
    form_class = CreateUserForm
    success_url = reverse_lazy('success')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True # False
        user.save()
        send_verification_email(self.request, user)
        return redirect(self.success_url)


def success(request):
    return render(request, 'registration/success.html',
                  context={'title': "An account verification link has been sent to your email",
                           "message": 'Please Check your email for verification link and sign in again'})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'registration/success.html',
                      context={'title': "You email is now activated successfully",
                               "message": 'You may now login using your credentials'})
    else:
        return redirect(reverse('error'))


def resend_activation_mail(request, uname):
    user = User.objects.get(email=uname)
    send_verification_email(request, user)
    return redirect('success')


class ShowProfile(generic.TemplateView):
    template_name = 'auth/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_orders'] = self.request.user.orders.exclude(status__in=['Delivered', 'Cancelled'])
        context['previous_orders'] = self.request.user.orders.filter(status__in=['Delivered', 'Cancelled'])
        return context
    


def logout_view(request):
    logout(request)
    return redirect('index')


class EditAccount(generic.UpdateView):
    def get_object(self):
        return self.request.user

    model = User
    form_class = FullUserForm
    template_name = 'registration/edit.html'
    success_url = reverse_lazy('profile')
