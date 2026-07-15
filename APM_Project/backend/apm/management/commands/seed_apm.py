from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from apm.models import ProfilUtilisateur, RessourcesGlobales, Role

Utilisateur = get_user_model()


class Command(BaseCommand):
    help = (
        "Initialise les 3 rôles métier (admin / admin_systeme / membre_dsi), "
        "les comptes de démonstration et la capacité CPU/RAM par défaut."
    )

    def handle(self, *args, **options):
        # ------------------------------------------------------------------ #
        # 1. Rôle ADMIN : gestion des utilisateurs & rôles uniquement          #
        # ------------------------------------------------------------------ #
        admin_role, _ = Role.objects.update_or_create(
            nom='Admin',
            defaults={
                'description': "Gestion des utilisateurs et des rôles uniquement.",
                'type_role': Role.TYPE_ADMIN,
                'peut_gerer_users': True,
                'peut_gerer_apps': False,
                'peut_voir_dashboard_admin': True,
                'peut_gerer_ressources': False,
            }
        )
        self.stdout.write(f"  ✓ Rôle «Admin» (type={Role.TYPE_ADMIN})")

        # ------------------------------------------------------------------ #
        # 2. Rôle ADMIN_SYSTEME : consultation du patrimoine + gestion CPU/RAM #
        # ------------------------------------------------------------------ #
        systeme_role, _ = Role.objects.update_or_create(
            nom='Administrateur Système',
            defaults={
                'description': "Consultation des actifs (apps/env/SSL) + gestion de la capacité CPU/RAM.",
                'type_role': Role.TYPE_ADMIN_SYSTEME,
                'peut_gerer_users': False,
                'peut_gerer_apps': False,
                'peut_voir_dashboard_admin': False,
                'peut_gerer_ressources': True,
            }
        )
        self.stdout.write(f"  ✓ Rôle «Administrateur Système» (type={Role.TYPE_ADMIN_SYSTEME})")

        # ------------------------------------------------------------------ #
        # 3. Rôle MEMBRE_DSI : gestion complète du patrimoine applicatif       #
        # ------------------------------------------------------------------ #
        dsi_role, _ = Role.objects.update_or_create(
            nom='Membre DSI',
            defaults={
                'description': "Gestion complète du patrimoine applicatif (apps/env/SSL/domaines/contrats/docs).",
                'type_role': Role.TYPE_MEMBRE_DSI,
                'peut_gerer_users': False,
                'peut_gerer_apps': True,
                'peut_voir_dashboard_admin': False,
                'peut_gerer_ressources': False,
            }
        )
        self.stdout.write(f"  ✓ Rôle «Membre DSI» (type={Role.TYPE_MEMBRE_DSI})")

        # ------------------------------------------------------------------ #
        # 4. Capacité globale CPU/RAM par défaut                               #
        # ------------------------------------------------------------------ #
        ressources = RessourcesGlobales.get_solo()
        if ressources.cpu_total == 0 and ressources.ram_total == 0:
            ressources.cpu_total = 256
            ressources.ram_total = 1024
            ressources.save()
            self.stdout.write("  ✓ Capacité par défaut : 256 vCPU / 1 024 Go RAM")

        # ------------------------------------------------------------------ #
        # 5. Comptes de démonstration                                          #
        # ------------------------------------------------------------------ #
        accounts = [
            ('admin',        'Admin123!',   'admin@topnet.tn',    admin_role,   True),
            ('sys_admin',    'Sys123!',     'sys@topnet.tn',      systeme_role, False),
            ('dsi_membre',   'Dsi123!',     'dsi@topnet.tn',      dsi_role,     False),
        ]
        for username, password, email, role, is_su in accounts:
            if not Utilisateur.objects.filter(username=username).exists():
                if is_su:
                    u = Utilisateur.objects.create_superuser(username=username, email=email, password=password)
                else:
                    u = Utilisateur.objects.create_user(username=username, email=email, password=password)
                u.role = role
                u.save()
                ProfilUtilisateur.objects.get_or_create(utilisateur=u)
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Compte «{username}» créé (mdp: {password}, rôle: {role.nom})"
                ))
            else:
                self.stdout.write(f"  – Compte «{username}» déjà existant.")

        self.stdout.write(self.style.SUCCESS("\n✅ Seed terminé avec succès."))
