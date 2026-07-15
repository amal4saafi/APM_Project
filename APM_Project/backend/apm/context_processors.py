def can_manage_patrimoine(request):
    user = getattr(request, 'user', None)
    can_manage = False
    can_view = False
    notifs_count = 0
    notifs_list = []
    if user and user.is_authenticated:
        can_manage = bool(getattr(user, 'is_dsi_role', False))
        can_view = can_manage or bool(getattr(user, 'is_systeme_role', False))
        try:
            from .models import Notification
            qs = Notification.objects.filter(destinataire=user, lu=False).order_by('-cree_le')
            notifs_count = qs.count()
            notifs_list = list(qs[:5])
        except Exception:
            pass
    return {
        'can_manage_patrimoine': can_manage,
        'can_view_patrimoine': can_view,
        'notifs_count': notifs_count,
        'notifs_list': notifs_list,
    }
