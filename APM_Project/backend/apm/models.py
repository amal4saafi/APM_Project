from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                     RegexValidator)
from django.db import models

NOM_VALIDATOR = RegexValidator(
    regex=r'^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 _\-\.]{0,149}$',
    message="Utilisez uniquement lettres, chiffres, espaces, '-', '_' ou '.' (1 à 150 caractères)."
)
DOMAINE_VALIDATOR = RegexValidator(
    regex=r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})+$',
    message="Format de domaine invalide (ex: exemple.tn)."
)
TELEPHONE_VALIDATOR = RegexValidator(
    regex=r'^\+?[0-9 ]{6,20}$',
    message="Numéro de téléphone invalide."
)


class Role(models.Model):
    """Table Role - ajoutée au diagramme ERD.

    Trois profils métier pilotent l'application :
    - Admin : gestion des utilisateurs et des rôles uniquement.
    - Administrateur Système : consultation des applications / environnements /
      certificats SSL / domaines, et gestion de la capacité totale CPU/RAM.
    - Membre DSI : gestion complète du patrimoine applicatif (applications,
      environnements, SSL, domaines, contrats, documents).
    """
    TYPE_ADMIN = 'admin'
    TYPE_ADMIN_SYSTEME = 'admin_systeme'
    TYPE_MEMBRE_DSI = 'membre_dsi'
    TYPE_AUTRE = 'autre'
    TYPE_CHOICES = [
        (TYPE_ADMIN, 'Administrateur (users & rôles)'),
        (TYPE_ADMIN_SYSTEME, 'Administrateur Système'),
        (TYPE_MEMBRE_DSI, 'Membre DSI'),
        (TYPE_AUTRE, 'Autre'),
    ]

    id_role = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, default='')
    type_role = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default=TYPE_AUTRE, blank=True,
        help_text="Catégorie du rôle : pilote les accès de l'application."
    )

    # Droits simples portés par le rôle (utilisés pour l'affichage/permissions)
    peut_gerer_users = models.BooleanField(default=False, help_text="Peut gérer les utilisateurs")
    peut_gerer_apps = models.BooleanField(default=False, help_text="Peut gérer les applications")
    peut_voir_dashboard_admin = models.BooleanField(default=False, help_text="Peut voir le dashboard admin")
    peut_gerer_ressources = models.BooleanField(
        default=False,
        help_text="Peut gérer la capacité totale CPU/RAM (Administrateur Système)"
    )

    class Meta:
        verbose_name = "Rôle"
        verbose_name_plural = "Rôles"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Utilisateur(AbstractUser):
    """Utilisateur = auth user Django étendu avec les champs métier du diagramme."""
    telephone = models.CharField(max_length=30, blank=True, default='', validators=[TELEPHONE_VALIDATOR])
    departement = models.CharField(max_length=100, blank=True, default='')
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='utilisateurs'
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        """Admin = gestion des utilisateurs et des rôles uniquement."""
        return bool(self.is_superuser or (
            self.role and (self.role.type_role == Role.TYPE_ADMIN or self.role.peut_voir_dashboard_admin)
        ))

    @property
    def is_systeme_role(self):
        """Administrateur Système = consultation du patrimoine + gestion CPU/RAM total."""
        return bool(self.role and (
            self.role.type_role == Role.TYPE_ADMIN_SYSTEME or self.role.peut_gerer_ressources
        ))

    @property
    def is_dsi_role(self):
        """Membre DSI = gestion complète du patrimoine applicatif."""
        return bool(self.role and (
            self.role.type_role == Role.TYPE_MEMBRE_DSI or self.role.peut_gerer_apps
        ))


class Fournisseur(models.Model):
    id_fournisseur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150)
    contact = models.CharField(max_length=150, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    telephone = models.CharField(max_length=30, blank=True, default='')

    class Meta:
        verbose_name = "Fournisseur"
        verbose_name_plural = "Fournisseurs"

    def __str__(self):
        return self.nom


class Serveur(models.Model):
    id_serveur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150)

    class Meta:
        verbose_name = "Serveur"
        verbose_name_plural = "Serveurs"

    def __str__(self):
        return self.nom


class Application(models.Model):
    id_application = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=150, validators=[NOM_VALIDATOR])
    description = models.TextField(blank=True, default='')
    CRITERE_NORMAL = 'normal'
    CRITERE_FAIBLE = 'faible'
    CRITERE_ELEVE = 'eleve'
    CRITERE_CHOICES = [
        (CRITERE_NORMAL, 'Normal'),
        (CRITERE_FAIBLE, 'Faible'),
        (CRITERE_ELEVE, 'Élevé'),
    ]
    critere = models.CharField(
        max_length=10, choices=CRITERE_CHOICES, default=CRITERE_NORMAL,
        help_text="Niveau de criticité de l'application"
    )
    statut = models.BooleanField(default=True, help_text="Actif / Inactif")
    date_mise_prod = models.DateField(null=True, blank=True)
    date_fin_vie = models.DateField(null=True, blank=True)
    nombre_utilisateurs = models.PositiveIntegerField(default=0)
    direction_metier = models.CharField(max_length=150, blank=True, default='')
    id_user = models.ForeignKey(
        Utilisateur, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='applications', verbose_name="Propriétaire"
    )
    exige_ssl = models.BooleanField(default=False, help_text="Indique si l'application nécessite un certificat SSL")
    TYPE_INTERNE = 'interne'
    TYPE_EXTERNE = 'externe'
    TYPE_APP_CHOICES = [
        (TYPE_INTERNE, 'Interne'),
        (TYPE_EXTERNE, 'Externe'),
    ]
    type_app = models.CharField(
        max_length=10, choices=TYPE_APP_CHOICES, default=TYPE_INTERNE,
        help_text="Application interne (développée/hébergée en interne) ou externe (fournisseur tiers)"
    )
    archive = models.BooleanField(default=False, help_text="Application archivée (masquée des listes actives)")

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    @property
    def jours_avant_expiration(self):
        """Nombre de jours restants avant date_fin_vie (utile pour les apps externes)."""
        if not self.date_fin_vie:
            return None
        from django.utils import timezone
        return (self.date_fin_vie - timezone.now().date()).days


class Incident(models.Model):
    id_incident = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    date_incident = models.DateField(null=True, blank=True)
    impact = models.CharField(max_length=100, blank=True, default='')
    cause_racine = models.TextField(blank=True, default='')
    solution = models.TextField(blank=True, default='')
    statut = models.CharField(max_length=50, blank=True, default='Ouvert')
    id_application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='incidents'
    )

    class Meta:
        verbose_name = "Incident"
        verbose_name_plural = "Incidents"

    def __str__(self):
        return self.titre


class Document(models.Model):
    id_document = models.AutoField(primary_key=True)
    nom_fichier = models.CharField(max_length=200)
    type_fichier = models.CharField(max_length=50, blank=True, default='')
    categorie = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(blank=True, default='')
    date_upload = models.DateField(auto_now_add=True)
    id_application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='documents'
    )
    archive = models.BooleanField(default=False, help_text="Document archivé")

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return self.nom_fichier


class Contrat(models.Model):
    id_contrat = models.AutoField(primary_key=True)
    numero_contrat = models.CharField(max_length=100)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    cout_annuel = models.FloatField(default=0)
    sla = models.CharField(max_length=100, blank=True, default='')
    statut = models.CharField(max_length=50, blank=True, default='')
    id_application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='contrats'
    )
    id_fournisseur = models.ForeignKey(
        Fournisseur, on_delete=models.SET_NULL, null=True, blank=True, related_name='contrats'
    )
    archive = models.BooleanField(default=False, help_text="Contrat archivé")

    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"

    def __str__(self):
        return self.numero_contrat


class Environnement(models.Model):
    id_environnement = models.AutoField(primary_key=True)
    nom = models.CharField(
        max_length=50,
        help_text="Ex: DEV, RECETTE, PREPROD, PROD",
        validators=[RegexValidator(
            regex=r'^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 _\-]{0,49}$',
            message="Utilisez uniquement lettres, chiffres, espaces, '-' ou '_' (1 à 50 caractères)."
        )]
    )
    url = models.CharField(max_length=255, blank=True, default='')
    adresse_ip = models.CharField(
        max_length=50, blank=True, default='',
        validators=[RegexValidator(
            regex=r'^$|^(\d{1,3}\.){3}\d{1,3}$',
            message="Adresse IP invalide (ex: 192.168.1.10)."
        )]
    )
    os = models.CharField(max_length=100, blank=True, default='')
    cpu = models.PositiveIntegerField(
        default=0, help_text="Nombre de vCPU alloués à cet environnement",
        validators=[MaxValueValidator(1024)]
    )
    ram = models.PositiveIntegerField(
        default=0, help_text="RAM allouée à cet environnement, en Go",
        validators=[MaxValueValidator(4096)]
    )
    hebergeur = models.CharField(max_length=100, blank=True, default='')
    type_hebergement = models.CharField(max_length=100, blank=True, default='')
    docker = models.BooleanField(default=False)
    kubernetes = models.BooleanField(default=False)
    exige_ssl = models.BooleanField(default=False, help_text="Cet environnement exige un certificat SSL")
    id_application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='environnements',
        null=True, blank=True,
        help_text="Peut être laissée vide à la création puis liée à une application ensuite."
    )
    id_serveur = models.ForeignKey(
        Serveur, on_delete=models.SET_NULL, null=True, blank=True, related_name='environnements'
    )
    archive = models.BooleanField(default=False, help_text="Environnement archivé")

    class Meta:
        verbose_name = "Environnement"
        verbose_name_plural = "Environnements"

    def __str__(self):
        app_nom = self.id_application.nom if self.id_application_id else "Sans application"
        return f"{self.nom} - {app_nom}"


class NomDomaine(models.Model):
    id_nom_domaine = models.AutoField(primary_key=True)
    nom_domaine = models.CharField(max_length=200, validators=[DOMAINE_VALIDATOR])
    registrar = models.CharField(max_length=150, blank=True, default='')
    dns = models.CharField(max_length=200, blank=True, default='')
    date_achat = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)
    renouvellement_auto = models.BooleanField(default=False)
    id_application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='noms_domaine'
    )
    archive = models.BooleanField(default=False, help_text="Nom de domaine archivé")

    class Meta:
        verbose_name = "Nom de domaine"
        verbose_name_plural = "Noms de domaine"

    def __str__(self):
        return self.nom_domaine


class CertificatSSL(models.Model):
    id_certificat_ssl = models.AutoField(primary_key=True)
    domaine = models.CharField(max_length=200, validators=[DOMAINE_VALIDATOR])
    fournisseur_ssl = models.CharField(max_length=150, blank=True, default='')
    date_debut = models.DateField(null=True, blank=True)
    date_expiration = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=50, blank=True, default='')
    id_environnement = models.ForeignKey(
        Environnement, on_delete=models.CASCADE, related_name='certificats_ssl'
    )
    archive = models.BooleanField(default=False, help_text="Certificat archivé")

    class Meta:
        verbose_name = "Certificat SSL"
        verbose_name_plural = "Certificats SSL"

    def __str__(self):
        return self.domaine

    @property
    def jours_restants(self):
        """Jours restants avant expiration (négatif si déjà expiré, None si pas de date)."""
        if not self.date_expiration:
            return None
        from django.utils import timezone
        return (self.date_expiration - timezone.now().date()).days

    @property
    def est_expire(self):
        jours = self.jours_restants
        return jours is not None and jours < 0


class Log(models.Model):
    id_log = models.AutoField(primary_key=True)
    action = models.CharField(max_length=100)
    entite_name = models.CharField(max_length=100, blank=True, default='')
    date_action = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, default='')
    id_incident = models.ForeignKey(
        Incident, on_delete=models.CASCADE, null=True, blank=True, related_name='logs'
    )

    class Meta:
        verbose_name = "Log"
        verbose_name_plural = "Logs"
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.action} ({self.date_action:%Y-%m-%d %H:%M})"


class RessourcesGlobales(models.Model):
    """Capacité totale CPU/RAM du parc, gérée par l'Administrateur Système.

    Ligne unique (singleton). La capacité restante est calculée dynamiquement
    en soustrayant la somme des CPU/RAM déjà alloués aux environnements.
    """
    cpu_total = models.PositiveIntegerField(
        default=0, help_text="Capacité totale en vCPU", validators=[MaxValueValidator(100000)]
    )
    ram_total = models.PositiveIntegerField(
        default=0, help_text="Capacité totale de RAM, en Go", validators=[MaxValueValidator(100000)]
    )
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ressources globales"
        verbose_name_plural = "Ressources globales"

    def __str__(self):
        return f"CPU {self.cpu_total} vCPU / RAM {self.ram_total} Go"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @property
    def cpu_utilise(self):
        return Environnement.objects.filter(archive=False).aggregate(total=models.Sum('cpu'))['total'] or 0

    @property
    def ram_utilise(self):
        return Environnement.objects.filter(archive=False).aggregate(total=models.Sum('ram'))['total'] or 0

    @property
    def cpu_restant(self):
        return self.cpu_total - self.cpu_utilise

    @property
    def ram_restant(self):
        return self.ram_total - self.ram_utilise

    @property
    def cpu_pourcentage(self):
        return min(100, round((self.cpu_utilise / self.cpu_total) * 100)) if self.cpu_total else 0

    @property
    def ram_pourcentage(self):
        return min(100, round((self.ram_utilise / self.ram_total) * 100)) if self.ram_total else 0


class PasswordResetToken(models.Model):
    """Token à usage unique pour la réinitialisation du mot de passe.

    Deux flux possibles :
    1. L'utilisateur saisit son email → un token lui est envoyé par mail.
    2. L'administrateur génère un lien de reset depuis la liste des utilisateurs
       (utile quand l'email n'est pas configuré / boîte inaccessible).
    """
    user = models.ForeignKey(
        'Utilisateur', on_delete=models.CASCADE, related_name='reset_tokens'
    )
    token = models.CharField(max_length=64, unique=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    expire_le = models.DateTimeField()
    utilise = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Token de réinitialisation"
        verbose_name_plural = "Tokens de réinitialisation"

    def __str__(self):
        return f"Reset {self.user.username} ({self.expire_le:%Y-%m-%d %H:%M})"

    @classmethod
    def create_for_user(cls, user, hours=24):
        import secrets
        from datetime import timedelta
        from django.utils import timezone
        cls.objects.filter(user=user, utilise=False).delete()
        token = secrets.token_urlsafe(48)
        expire = timezone.now() + timedelta(hours=hours)
        return cls.objects.create(user=user, token=token, expire_le=expire)

    @property
    def is_valid(self):
        from django.utils import timezone
        return not self.utilise and self.expire_le > timezone.now()


class Notification(models.Model):
    """Notifications en temps réel par utilisateur."""
    TYPE_CHOICES = [
        ('success', 'Succès'),
        ('info', 'Information'),
        ('warning', 'Avertissement'),
        ('danger', 'Erreur'),
    ]
    destinataire = models.ForeignKey(
        'Utilisateur', on_delete=models.CASCADE, related_name='notifications'
    )
    type_notif = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    titre = models.CharField(max_length=200)
    message = models.TextField()
    lu = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    action_url = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-cree_le']

    def __str__(self):
        return f"[{self.type_notif}] {self.titre} → {self.destinataire.username}"


class HistoriqueAction(models.Model):
    """Journal complet de toutes les actions effectuées dans l'application."""
    utilisateur = models.ForeignKey(
        'Utilisateur', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='historique_actions'
    )
    action = models.CharField(max_length=200)
    modele = models.CharField(max_length=100, blank=True, default='')
    objet_id = models.PositiveIntegerField(null=True, blank=True)
    objet_repr = models.CharField(max_length=255, blank=True, default='')
    details = models.TextField(blank=True, default='')
    date_action = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Historique action"
        verbose_name_plural = "Historique actions"
        ordering = ['-date_action']

    def __str__(self):
        return f"{self.utilisateur} — {self.action} ({self.date_action:%d/%m/%Y %H:%M})"


class ProfilUtilisateur(models.Model):
    """Extension du profil : photo, bio, préférences."""
    utilisateur = models.OneToOneField(
        'Utilisateur', on_delete=models.CASCADE, related_name='profil'
    )
    photo = models.ImageField(
        upload_to='profils/', null=True, blank=True,
        help_text="Photo de profil (JPG, PNG)"
    )
    bio = models.CharField(max_length=300, blank=True, default='')
    poste = models.CharField(max_length=150, blank=True, default='')
    linkedin = models.URLField(blank=True, default='')
    preferences = models.JSONField(default=dict, blank=True)
    maj_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"

    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None


class DocumentFichier(models.Model):
    """Fichiers uploadés associés à un document."""
    TYPES_AUTORISES = [
        ('pdf', 'PDF'), ('docx', 'Word'), ('xlsx', 'Excel'),
        ('png', 'Image PNG'), ('jpg', 'Image JPG'), ('autre', 'Autre'),
    ]
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name='fichiers'
    )
    fichier = models.FileField(upload_to='documents/%Y/%m/')
    nom_original = models.CharField(max_length=255)
    type_fichier = models.CharField(max_length=10, choices=TYPES_AUTORISES, default='autre')
    taille_ko = models.PositiveIntegerField(default=0)
    uploade_par = models.ForeignKey(
        'Utilisateur', on_delete=models.SET_NULL, null=True, blank=True
    )
    uploade_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Fichier document"
        verbose_name_plural = "Fichiers documents"

    def __str__(self):
        return self.nom_original
