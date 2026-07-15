from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def admin_required(view_func):
    """Autorise uniquement les superusers ou les rôles marqués 'peut_voir_dashboard_admin'."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('login')
        if not user.is_admin_role:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped
