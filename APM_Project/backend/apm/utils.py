"""
utils.py — helpers transverses pour APM TOPNET
"""
import re

from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


# ---------------------------------------------------------------------------
# Validation email
# ---------------------------------------------------------------------------

def is_valid_email(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


# ---------------------------------------------------------------------------
# Journalisation HistoriqueAction
# ---------------------------------------------------------------------------

def journaliser(request, action: str, modele: str = '', objet=None, details: str = ''):
    """Enregistre une action dans HistoriqueAction et Log."""
    from .models import HistoriqueAction, Log

    user = getattr(request, 'user', None)
    if user and not user.is_authenticated:
        user = None

    ip = _get_client_ip(request)
    objet_id = getattr(objet, 'pk', None) if objet else None
    objet_repr = str(objet)[:255] if objet else ''

    HistoriqueAction.objects.create(
        utilisateur=user,
        action=action,
        modele=modele,
        objet_id=objet_id,
        objet_repr=objet_repr,
        details=details,
        ip_address=ip,
    )
    Log.objects.create(action=action, entite_name=objet_repr or modele, details=details)


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ---------------------------------------------------------------------------
# Notifications in-app
# ---------------------------------------------------------------------------

def notifier(destinataires, titre: str, message: str, type_notif: str = 'info', action_url: str = ''):
    """Crée une notification pour une liste d'utilisateurs."""
    from .models import Notification

    if not isinstance(destinataires, (list, tuple)):
        destinataires = [destinataires]

    notifs = []
    for user in destinataires:
        if user and getattr(user, 'pk', None):
            notifs.append(Notification(
                destinataire=user,
                type_notif=type_notif,
                titre=titre,
                message=message,
                action_url=action_url,
            ))
    if notifs:
        Notification.objects.bulk_create(notifs)


def notifier_tous_admins(titre, message, type_notif='info', action_url='', exclude_user=None):
    """Notifie tous les utilisateurs avec un rôle admin ou admin_systeme."""
    from .models import Role
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admins = User.objects.filter(
        role__type_role__in=[Role.TYPE_ADMIN, Role.TYPE_ADMIN_SYSTEME]
    ).distinct()
    if exclude_user:
        admins = admins.exclude(pk=exclude_user.pk)
    notifier(list(admins), titre, message, type_notif, action_url)


# ---------------------------------------------------------------------------
# Email — création de compte
# ---------------------------------------------------------------------------

def envoyer_email_creation_compte(user, mot_de_passe_temp: str, site_url: str = ''):
    """Envoie un email de bienvenue avec les identifiants au nouvel utilisateur."""
    if not user.email or not is_valid_email(user.email):
        return False, "Email invalide ou manquant."

    sujet = "Bienvenue sur APM TOPNET — Votre compte a été créé"
    corps = (
        f"Bonjour {user.get_full_name() or user.username},\n\n"
        f"Un compte a été créé pour vous sur la plateforme APM TOPNET.\n\n"
        f"Vos identifiants de connexion :\n"
        f"  Nom d'utilisateur : {user.username}\n"
        f"  Mot de passe temporaire : {mot_de_passe_temp}\n\n"
        f"Connectez-vous ici : {site_url or 'http://localhost:8000'}\n\n"
        f"⚠️ Changez votre mot de passe dès votre première connexion.\n\n"
        f"Cordialement,\n"
        f"L'équipe APM TOPNET"
    )
    try:
        send_mail(
            sujet, corps,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True, "Email envoyé."
    except Exception as e:
        return False, f"Échec d'envoi : {e}"


# ---------------------------------------------------------------------------
# Import/Export helpers — rapport d'opération
# ---------------------------------------------------------------------------

def build_import_report(created: list, updated: list, errors: list) -> dict:
    """Construit un rapport structuré après un import Excel."""
    total = len(created) + len(updated)
    if total == 0 and not errors:
        resume = "0 ajout — aucune modification effectuée."
    else:
        parts = []
        if created:
            parts.append(f"{len(created)} ajout(s)")
        if updated:
            parts.append(f"{len(updated)} mise(s) à jour")
        if errors:
            parts.append(f"{len(errors)} erreur(s)")
        resume = " | ".join(parts)

    return {
        'resume': resume,
        'total': total,
        'created': created,
        'updated': updated,
        'errors': errors,
        'success': total > 0,
    }


def get_profil_or_create(user):
    """Récupère ou crée le profil d'un utilisateur."""
    from .models import ProfilUtilisateur
    profil, _ = ProfilUtilisateur.objects.get_or_create(utilisateur=user)
    return profil


# ---------------------------------------------------------------------------
# Alertes — applications externes proches de leur fin de vie
# ---------------------------------------------------------------------------

SEUIL_JOURS_APP_EXTERNE = 30  # nombre de jours avant expiration pour déclencher l'alerte


def verifier_expirations_apps_externes():
    """Crée une notification (une seule fois par jour et par application) pour
    chaque application EXTERNE dont la date de fin de vie approche (<= 30 jours)
    ou est dépassée. Destinée aux utilisateurs Membre DSI.
    """
    from datetime import timedelta
    from django.utils import timezone
    from django.urls import reverse
    from .models import Application, Notification, Role
    from django.contrib.auth import get_user_model

    User = get_user_model()
    today = timezone.now().date()
    limite = today + timedelta(days=SEUIL_JOURS_APP_EXTERNE)

    apps = Application.objects.filter(
        archive=False, type_app=Application.TYPE_EXTERNE,
        date_fin_vie__isnull=False, date_fin_vie__lte=limite,
    )
    if not apps.exists():
        return

    dsi_users = list(User.objects.filter(role__type_role=Role.TYPE_MEMBRE_DSI))
    if not dsi_users:
        return

    for app in apps:
        url = reverse('application_edit', args=[app.pk])
        deja_notifie_aujourdhui = Notification.objects.filter(
            action_url=url, cree_le__date=today,
        ).exists()
        if deja_notifie_aujourdhui:
            continue
        jours = (app.date_fin_vie - today).days
        if jours < 0:
            titre = "Application externe expirée"
            message = f"L'application externe « {app.nom} » a dépassé sa date de fin de vie ({app.date_fin_vie:%d/%m/%Y})."
            type_notif = 'danger'
        else:
            titre = "Fin de vie proche — application externe"
            message = f"L'application externe « {app.nom} » arrive en fin de vie dans {jours} jour(s) ({app.date_fin_vie:%d/%m/%Y})."
            type_notif = 'warning'
        notifier(dsi_users, titre, message, type_notif=type_notif, action_url=url)
