from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator

from .models import (Application, CertificatSSL, Contrat, Document,
                      Environnement, Fournisseur, NomDomaine,
                      ProfilUtilisateur, RessourcesGlobales, Role, Utilisateur)

WIDGET_ATTRS = {'class': 'form-control'}
CHECK_ATTRS = {'class': 'form-check-input'}

NOM_PERSONNE_VALIDATOR = RegexValidator(
    regex=r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ' \-]*$",
    message="Ce champ ne doit contenir que des lettres (espaces, apostrophes et tirets autorisés), aucun chiffre."
)


def _appliquer_validateur_nom_prenom(form):
    """Ajoute le validateur 'lettres uniquement' sur les champs first_name / last_name du formulaire."""
    for name in ('first_name', 'last_name'):
        field = form.fields.get(name)
        if field is not None:
            field.validators.append(NOM_PERSONNE_VALIDATOR)


class UtilisateurCreateForm(UserCreationForm):
    email = forms.EmailField(
        label="Email", required=True,
        help_text="Un email de bienvenue avec les identifiants sera envoyé à cette adresse.",
        widget=forms.EmailInput(attrs=WIDGET_ATTRS)
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email',
                  'telephone', 'departement', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update(WIDGET_ATTRS)
        _appliquer_validateur_nom_prenom(self)

    def clean_email(self):
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError as DjValidationError
        email = self.cleaned_data.get('email', '').strip()
        try:
            validate_email(email)
        except DjValidationError:
            raise forms.ValidationError("Adresse email invalide.")
        if Utilisateur.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé par un autre compte.")
        return email


class UtilisateurEditForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'first_name', 'last_name', 'email',
                  'telephone', 'departement', 'role', 'is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs=CHECK_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'is_active':
                field.widget.attrs.update(WIDGET_ATTRS)
        _appliquer_validateur_nom_prenom(self)


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['nom', 'description', 'type_role', 'peut_gerer_users',
                  'peut_gerer_apps', 'peut_voir_dashboard_admin', 'peut_gerer_ressources']
        labels = {
            'type_role': 'Type de rôle',
            'peut_gerer_users': 'Peut gérer users',
            'peut_gerer_apps': 'Peut gérer apps',
            'peut_voir_dashboard_admin': 'Peut voir dashboard admin',
            'peut_gerer_ressources': 'Peut gérer les ressources (CPU/RAM)',
        }
        widgets = {
            'peut_gerer_users': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'peut_gerer_apps': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'peut_voir_dashboard_admin': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'peut_gerer_ressources': forms.CheckboxInput(attrs=CHECK_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(WIDGET_ATTRS)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['nom', 'description', 'critere', 'statut', 'type_app', 'date_mise_prod',
                  'date_fin_vie', 'nombre_utilisateurs', 'direction_metier', 'id_user', 'exige_ssl']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'statut': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'date_mise_prod': forms.DateInput(attrs={'type': 'date'}),
            'date_fin_vie': forms.DateInput(attrs={'type': 'date'}),
            'exige_ssl': forms.CheckboxInput(attrs=CHECK_ATTRS),
        }
        labels = {
            'id_user': 'Propriétaire',
            'type_app': "Type d'application",
            'date_fin_vie': "Date de fin de vie / d'expiration",
        }
        help_texts = {
            'type_app': "Si « Externe », une notification sera envoyée quelques jours avant la date de fin de vie.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(WIDGET_ATTRS)
        self.fields['id_user'].required = False
        self.fields['nombre_utilisateurs'].widget.attrs.update({'min': 0, 'step': 1})

    def clean(self):
        cleaned = super().clean()
        debut = cleaned.get('date_mise_prod')
        fin = cleaned.get('date_fin_vie')
        if debut and fin and fin < debut:
            self.add_error('date_fin_vie', "La date de fin de vie doit être postérieure à la date de mise en production.")
        return cleaned


class EnvironnementForm(forms.ModelForm):
    class Meta:
        model = Environnement
        fields = ['nom', 'id_application', 'url', 'adresse_ip', 'os', 'cpu', 'ram',
                  'hebergeur', 'type_hebergement', 'docker', 'kubernetes', 'exige_ssl', 'id_serveur']
        labels = {'id_application': 'Application (facultatif à la création)', 'id_serveur': 'Serveur'}
        widgets = {
            'docker': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'kubernetes': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'exige_ssl': forms.CheckboxInput(attrs=CHECK_ATTRS),
            'cpu': forms.NumberInput(attrs={'min': 0, 'max': 1024, 'step': 1}),
            'ram': forms.NumberInput(attrs={'min': 0, 'max': 4096, 'step': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(WIDGET_ATTRS)
        # Une application peut être ajoutée après coup : on ne l'exige pas à la création.
        self.fields['id_application'].required = False
        self.fields['cpu'].widget.attrs.update({'min': 0})
        self.fields['ram'].widget.attrs.update({'min': 0})

    def clean(self):
        cleaned = super().clean()
        cpu = cleaned.get('cpu') or 0
        ram = cleaned.get('ram') or 0
        ressources = RessourcesGlobales.get_solo()
        deja_alloue_cpu = self.instance.cpu if self.instance.pk else 0
        deja_alloue_ram = self.instance.ram if self.instance.pk else 0
        cpu_dispo = ressources.cpu_restant + deja_alloue_cpu
        ram_dispo = ressources.ram_restant + deja_alloue_ram
        if ressources.cpu_total and cpu > cpu_dispo:
            self.add_error('cpu', f"Capacité CPU insuffisante : {cpu_dispo} vCPU disponible(s) sur {ressources.cpu_total}.")
        if ressources.ram_total and ram > ram_dispo:
            self.add_error('ram', f"Capacité RAM insuffisante : {ram_dispo} Go disponible(s) sur {ressources.ram_total}.")
        return cleaned


class ImportExcelForm(forms.Form):
    fichier = forms.FileField(
        label="Fichier Excel (.xlsx)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.xlsx'})
    )


class CertificatSSLForm(forms.ModelForm):
    class Meta:
        model = CertificatSSL
        fields = ['domaine', 'id_environnement', 'fournisseur_ssl', 'date_debut', 'date_expiration', 'statut']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        app_id = kwargs.pop('app_id', None)
        super().__init__(*args, **kwargs)
        # If an app_id is provided, limit environment choices to that app's envs
        if app_id:
            self.fields['id_environnement'].queryset = Environnement.objects.filter(id_application__pk=app_id)
        for name, field in self.fields.items():
            field.widget.attrs.update(WIDGET_ATTRS)

    def clean(self):
        cleaned = super().clean()
        debut = cleaned.get('date_debut')
        fin = cleaned.get('date_expiration')
        if debut and fin and fin <= debut:
            self.add_error('date_expiration', "La date d'expiration doit être postérieure à la date de début.")
        return cleaned


class NomDomaineForm(forms.ModelForm):
    class Meta:
        model = NomDomaine
        fields = ['nom_domaine', 'id_application', 'registrar', 'dns', 'date_achat', 'date_expiration', 'renouvellement_auto']
        widgets = {
            'date_achat': forms.DateInput(attrs={'type': 'date'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date'}),
            'renouvellement_auto': forms.CheckboxInput(attrs=CHECK_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update(WIDGET_ATTRS)

    def clean(self):
        cleaned = super().clean()
        debut = cleaned.get('date_achat')
        fin = cleaned.get('date_expiration')
        if debut and fin and fin <= debut:
            self.add_error('date_expiration', "La date d'expiration doit être postérieure à la date d'achat.")
        return cleaned


class ContratForm(forms.ModelForm):
    class Meta:
        model = Contrat
        fields = ['numero_contrat', 'id_application', 'date_debut', 'date_fin', 'cout_annuel', 'sla', 'statut', 'id_fournisseur']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'type': 'date'}),
            'cout_annuel': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update(WIDGET_ATTRS)

    def clean(self):
        cleaned = super().clean()
        debut = cleaned.get('date_debut')
        fin = cleaned.get('date_fin')
        cout = cleaned.get('cout_annuel')
        if debut and fin and fin <= debut:
            self.add_error('date_fin', "La date de fin doit être postérieure à la date de début.")
        if cout is not None and cout < 0:
            self.add_error('cout_annuel', "Le coût annuel ne peut pas être négatif.")
        return cleaned


class RessourcesGlobalesForm(forms.ModelForm):
    """Formulaire réservé à l'Administrateur Système : capacité totale CPU/RAM."""
    class Meta:
        model = RessourcesGlobales
        fields = ['cpu_total', 'ram_total']
        labels = {'cpu_total': 'Capacité totale CPU (vCPU)', 'ram_total': 'Capacité totale RAM (Go)'}
        widgets = {
            'cpu_total': forms.NumberInput(attrs={'min': 0, 'max': 100000, 'step': 1}),
            'ram_total': forms.NumberInput(attrs={'min': 0, 'max': 100000, 'step': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update(WIDGET_ATTRS)

    def clean(self):
        cleaned = super().clean()
        cpu_total = cleaned.get('cpu_total')
        ram_total = cleaned.get('ram_total')
        if cpu_total is not None and cpu_total < self.instance.cpu_utilise:
            self.add_error('cpu_total', f"Impossible : {self.instance.cpu_utilise} vCPU sont déjà alloués aux environnements.")
        if ram_total is not None and ram_total < self.instance.ram_utilise:
            self.add_error('ram_total', f"Impossible : {self.instance.ram_utilise} Go sont déjà alloués aux environnements.")
        return cleaned


class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultiFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultiFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        # Bypass single-file validation; actual files are pulled from request.FILES in the view.
        return data


class DocumentForm(forms.ModelForm):
    fichiers = MultiFileField(
        label="Importer des fichiers (PDF, DOCX, XLSX, PNG, JPG)",
        required=False,
        help_text="Vous pouvez sélectionner plusieurs fichiers à joindre dès la création du document.",
    )

    class Meta:
        model = Document
        fields = ['nom_fichier', 'type_fichier', 'categorie', 'description', 'id_application']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != 'fichiers':
                field.widget.attrs.update(WIDGET_ATTRS)
        if self.instance and self.instance.pk:
            # Le document existe déjà : on utilise la zone de dépôt dédiée plus bas.
            del self.fields['fichiers']


# ---------------------------------------------------------------------------
# Réinitialisation du mot de passe
# ---------------------------------------------------------------------------

class PasswordResetRequestForm(forms.Form):
    """Étape 1 : l'utilisateur saisit son email ou son nom d'utilisateur."""
    identifiant = forms.CharField(
        label="Email ou nom d'utilisateur",
        max_length=254,
        widget=forms.TextInput(attrs={
            **WIDGET_ATTRS,
            'placeholder': "Ex : jean.dupont ou jean@topnet.tn",
            'autofocus': True,
        }),
    )

    def clean_identifiant(self):
        val = self.cleaned_data['identifiant'].strip()
        if not val:
            raise forms.ValidationError("Ce champ est obligatoire.")
        user = (
            Utilisateur.objects.filter(email__iexact=val).first()
            or Utilisateur.objects.filter(username__iexact=val).first()
        )
        if not user:
            raise forms.ValidationError("Aucun compte ne correspond à cet identifiant.")
        if not user.is_active:
            raise forms.ValidationError("Ce compte est désactivé. Contactez un administrateur.")
        self.cleaned_data['user'] = user
        return val


class SetNewPasswordForm(forms.Form):
    """Étape 2 : l'utilisateur saisit et confirme son nouveau mot de passe."""
    nouveau_mdp = forms.CharField(
        label="Nouveau mot de passe",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            **WIDGET_ATTRS,
            'placeholder': "Minimum 8 caractères",
            'autocomplete': 'new-password',
        }),
    )
    confirmer_mdp = forms.CharField(
        label="Confirmer le mot de passe",
        min_length=8,
        widget=forms.PasswordInput(attrs={
            **WIDGET_ATTRS,
            'placeholder': "Répétez le mot de passe",
            'autocomplete': 'new-password',
        }),
    )

    def clean(self):
        cleaned = super().clean()
        mdp1 = cleaned.get('nouveau_mdp', '')
        mdp2 = cleaned.get('confirmer_mdp', '')
        if mdp1 and mdp2 and mdp1 != mdp2:
            self.add_error('confirmer_mdp', "Les deux mots de passe ne correspondent pas.")
        # Règles de complexité minimales
        if mdp1:
            if not any(c.isupper() for c in mdp1):
                self.add_error('nouveau_mdp', "Le mot de passe doit contenir au moins une majuscule.")
            if not any(c.isdigit() for c in mdp1):
                self.add_error('nouveau_mdp', "Le mot de passe doit contenir au moins un chiffre.")
        return cleaned


# ---------------------------------------------------------------------------
# Profil utilisateur
# ---------------------------------------------------------------------------

class ProfilForm(forms.ModelForm):
    """Formulaire profil : photo + coordonnées + info user."""
    first_name = forms.CharField(label="Prénom", max_length=150, required=False,
                                  validators=[NOM_PERSONNE_VALIDATOR],
                                  widget=forms.TextInput(attrs=WIDGET_ATTRS))
    last_name = forms.CharField(label="Nom", max_length=150, required=False,
                                 validators=[NOM_PERSONNE_VALIDATOR],
                                 widget=forms.TextInput(attrs=WIDGET_ATTRS))
    email = forms.EmailField(label="Email", required=False,
                              widget=forms.EmailInput(attrs=WIDGET_ATTRS))
    telephone = forms.CharField(label="Téléphone", max_length=30, required=False,
                                 widget=forms.TextInput(attrs=WIDGET_ATTRS))
    departement = forms.CharField(label="Département", max_length=100, required=False,
                                   widget=forms.TextInput(attrs=WIDGET_ATTRS))

    class Meta:
        model = ProfilUtilisateur
        fields = ['photo', 'bio', 'poste', 'linkedin']
        widgets = {
            'bio': forms.Textarea(attrs={**WIDGET_ATTRS, 'rows': 3}),
            'poste': forms.TextInput(attrs=WIDGET_ATTRS),
            'linkedin': forms.URLInput(attrs=WIDGET_ATTRS),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
            self.fields['telephone'].initial = getattr(self.user, 'telephone', '')
            self.fields['departement'].initial = getattr(self.user, 'departement', '')

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError as DjValidationError
            try:
                validate_email(email)
            except DjValidationError:
                raise forms.ValidationError("Adresse email invalide.")
        return email

    def save(self, commit=True):
        profil = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            self.user.telephone = self.cleaned_data.get('telephone', '')
            self.user.departement = self.cleaned_data.get('departement', '')
            self.user.save(update_fields=['first_name', 'last_name', 'email', 'telephone', 'departement'])
        if commit:
            profil.save()
        return profil
