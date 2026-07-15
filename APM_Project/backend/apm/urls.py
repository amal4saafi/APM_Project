from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_redirect, name='home'),

    # Dashboards
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/systeme/', views.dashboard_systeme, name='dashboard_systeme'),
    path('dashboard/systeme/ressources/', views.ressources_edit, name='ressources_edit'),
    path('dashboard/', views.dashboard_user, name='dashboard_user'),

    # Profil (commun aux 3 rôles)
    path('profil/', views.profil_view, name='profil'),
    path('profil/modifier/', views.profil_edit, name='profil_edit'),
    path('profil/reset-mdp/', views.profil_reset_mdp, name='profil_reset_mdp'),

    # Notifications
    path('notifications/lire/<int:pk>/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/lire-tout/', views.notifications_mark_all_read, name='notifications_mark_all_read'),

    # Utilisateurs
    path('users/', views.users_list, name='users_list'),
    path('users/nouveau/', views.user_create, name='user_create'),
    path('users/<int:pk>/modifier/', views.user_edit, name='user_edit'),
    path('users/<int:pk>/toggle/', views.user_toggle_active, name='user_toggle_active'),
    path('users/export/', views.users_export_excel, name='users_export_excel'),
    path('users/import/', views.users_import_excel, name='users_import_excel'),

    # Rôles
    path('roles/', views.roles_list, name='roles_list'),
    path('roles/nouveau/', views.role_create, name='role_create'),
    path('roles/<int:pk>/modifier/', views.role_edit, name='role_edit'),
    path('roles/<int:pk>/supprimer/', views.role_delete, name='role_delete'),

    # Applications
    path('applications/', views.applications_list, name='applications_list'),
    path('applications/nouveau/', views.application_create, name='application_create'),
    path('applications/<int:pk>/modifier/', views.application_edit, name='application_edit'),
    path('applications/<int:pk>/supprimer/', views.application_delete, name='application_delete'),
    path('applications/<int:pk>/restaurer/', views.application_restore, name='application_restore'),

    # Environnements
    path('environnements/', views.environnements_list, name='environnements_list'),
    path('environnements/nouveau/', views.environnement_create, name='environnement_create'),
    path('environnements/<int:pk>/modifier/', views.environnement_edit, name='environnement_edit'),
    path('environnements/<int:pk>/supprimer/', views.environnement_delete, name='environnement_delete'),
    path('environnements/<int:pk>/restaurer/', views.environnement_restore, name='environnement_restore'),

    # SSL
    path('ssl/', views.ssl_list, name='ssl_list'),
    path('ssl/nouveau/', views.ssl_create, name='ssl_create'),
    path('ssl/<int:pk>/modifier/', views.ssl_edit, name='ssl_edit'),
    path('ssl/<int:pk>/demande-renouvellement/', views.ssl_demande_renouvellement, name='ssl_demande_renouvellement'),
    path('ssl/<int:pk>/supprimer/', views.ssl_delete, name='ssl_delete'),
    path('ssl/<int:pk>/restaurer/', views.ssl_restore, name='ssl_restore'),

    # Domaines
    path('domaines/', views.noms_domaine_list, name='noms_domaine_list'),
    path('domaines/nouveau/', views.noms_domaine_create, name='noms_domaine_create'),
    path('domaines/<int:pk>/modifier/', views.noms_domaine_edit, name='noms_domaine_edit'),
    path('domaines/<int:pk>/supprimer/', views.noms_domaine_delete, name='noms_domaine_delete'),
    path('domaines/<int:pk>/restaurer/', views.noms_domaine_restore, name='noms_domaine_restore'),

    # Contrats
    path('contrats/', views.contrats_list, name='contrats_list'),
    path('contrats/nouveau/', views.contrats_create, name='contrats_create'),
    path('contrats/<int:pk>/modifier/', views.contrats_edit, name='contrats_edit'),
    path('contrats/<int:pk>/supprimer/', views.contrats_delete, name='contrats_delete'),
    path('contrats/<int:pk>/restaurer/', views.contrats_restore, name='contrats_restore'),

    # Documents + Upload fichiers
    path('documents/', views.documents_list, name='documents_list'),
    path('documents/nouveau/', views.documents_create, name='documents_create'),
    path('documents/<int:pk>/modifier/', views.documents_edit, name='documents_edit'),
    path('documents/<int:pk>/supprimer/', views.documents_delete, name='documents_delete'),
    path('documents/<int:pk>/restaurer/', views.documents_restore, name='documents_restore'),
    path('documents/<int:pk>/upload/', views.document_upload_fichier, name='document_upload_fichier'),
    path('documents/fichier/<int:pk>/supprimer/', views.document_fichier_delete, name='document_fichier_delete'),

    # Autres
    path('documentation/', views.documentation_page, name='documentation_page'),
    path('documentation/upload-rapide/', views.documentation_quick_upload, name='documentation_quick_upload'),
    path('rapports/', views.rapports_page, name='rapports_page'),
    path('historique/', views.historique_page, name='historique_page'),

    # API JSON
    path('api/notifs/', views.api_notifications, name='api_notifications'),
]
