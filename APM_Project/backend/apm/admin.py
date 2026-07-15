from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (Application, CertificatSSL, Contrat, Document,
                      DocumentFichier, Environnement, Fournisseur,
                      HistoriqueAction, Incident, Log, NomDomaine,
                      Notification, PasswordResetToken, ProfilUtilisateur,
                      RessourcesGlobales, Role, Serveur, Utilisateur)


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations APM', {'fields': ('telephone', 'departement', 'role')}),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_role', 'peut_gerer_users', 'peut_gerer_apps', 'peut_voir_dashboard_admin', 'peut_gerer_ressources')
    list_filter = ('type_role',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'direction_metier', 'statut', 'critere', 'id_user')
    list_filter = ('statut', 'critere', 'direction_metier')
    search_fields = ('nom',)


admin.site.register(Fournisseur)
admin.site.register(Serveur)
admin.site.register(Incident)
admin.site.register(Document)
admin.site.register(Contrat)
admin.site.register(Environnement)
admin.site.register(NomDomaine)
admin.site.register(CertificatSSL)
admin.site.register(Log)
admin.site.register(DocumentFichier)
admin.site.register(RessourcesGlobales)
admin.site.register(PasswordResetToken)
admin.site.register(ProfilUtilisateur)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('titre', 'destinataire', 'type_notif', 'lu', 'cree_le')
    list_filter = ('type_notif', 'lu')


@admin.register(HistoriqueAction)
class HistoriqueActionAdmin(admin.ModelAdmin):
    list_display = ('action', 'utilisateur', 'modele', 'date_action')
    list_filter = ('modele',)
    search_fields = ('action', 'objet_repr')
