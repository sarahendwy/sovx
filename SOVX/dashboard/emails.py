"""Admin-notification emails: order created, order status changed, Contact
Us and Sell With Us submissions - see Setting's notify_on_* toggles.

Sent synchronously, fail-silently: a broken SMTP connection or missing
admin email must never break the customer-facing request that triggered it
(order placement, form submission, status change), so every send is wrapped
so it can only ever log, never raise.
"""
import logging

from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import strip_tags

from .models import Setting

logger = logging.getLogger(__name__)


def _send_admin_notification(*, toggle, subject, template_name, context, request=None):
    """Renders `template_name` with `context` and emails it to the site's
    admin email, provided `toggle` (a Setting boolean field name) is on and
    an admin email is configured. Never raises - logs and returns on any
    failure, so callers can fire-and-forget this from a form_valid/view.
    """
    setting = Setting.objects.first()
    if not setting or not setting.email:
        return
    if not getattr(setting, toggle, False):
        return

    context = {**context, "site_name": "SOVX Products"}
    try:
        html_message = render_to_string(template_name, context, request=request)
        send_mail(
            subject=subject,
            message=strip_tags(html_message),
            html_message=html_message,
            from_email=None,  # falls back to DEFAULT_FROM_EMAIL
            recipient_list=[setting.email],
            fail_silently=True,
        )
    except Exception:
        # render_to_string can raise (bad template context, etc.) - send_mail
        # itself won't, since fail_silently=True. Catch both here so a
        # notification email can never take the triggering request down.
        logger.exception("Failed to send admin notification email (%s)", template_name)


def _absolute_url(request, url_name, *args):
    path = reverse(url_name, args=args)
    if request is not None:
        return request.build_absolute_uri(path)
    return path


def notify_order_created(order, request=None):
    _send_admin_notification(
        toggle="notify_on_order",
        subject=f"طلب جديد #{order.id}",
        template_name="emails/order_created.html",
        context={
            "order": order,
            "dashboard_url": _absolute_url(request, "order_details", order.id),
        },
        request=request,
    )


def notify_order_status_changed(order, old_status, new_status, old_status_label, new_status_label, request=None):
    _send_admin_notification(
        toggle="notify_on_order_status_change",
        subject=f"تغيّرت حالة الطلب #{order.id}: {old_status_label} → {new_status_label}",
        template_name="emails/order_status_changed.html",
        context={
            "order": order,
            "old_status_label": old_status_label,
            "new_status_label": new_status_label,
            "dashboard_url": _absolute_url(request, "order_details", order.id),
        },
        request=request,
    )


def notify_contact_us(contact_request, request=None):
    _send_admin_notification(
        toggle="notify_on_contact_us",
        subject="رسالة جديدة من تواصل معنا",
        template_name="emails/contact_us.html",
        context={
            "contact_request": contact_request,
            "dashboard_url": _absolute_url(request, "admin_contact_requests"),
        },
        request=request,
    )


def notify_sell_with_us(sell_request, request=None):
    _send_admin_notification(
        toggle="notify_on_sell_with_us",
        subject="طلب جديد من بيع معنا",
        template_name="emails/sell_with_us.html",
        context={
            "sell_request": sell_request,
            "dashboard_url": _absolute_url(request, "admin_sell_with_us_requests"),
        },
        request=request,
    )
