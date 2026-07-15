# Generated manually for: 3 rôles métier (admin / admin_systeme / membre_dsi),
# gestion de la capacité totale CPU/RAM, environnement sans application
# obligatoire, et contrôles de saisie renforcés.

import re

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


def _clean_numeric(apps, schema_editor):
    """Avant de convertir cpu/ram en entiers, ne garde que les chiffres des
    anciennes valeurs texte (ex: '4 vCPU' -> '4'), sinon met 0."""
    Environnement = apps.get_model('apm', 'Environnement')
    for env in Environnement.objects.all():
        changed = False
        for field in ('cpu', 'ram'):
            raw = getattr(env, field) or ''
            digits = re.sub(r'[^0-9]', '', str(raw))
            new_val = digits if digits else '0'
            if new_val != raw:
                setattr(env, field, new_val)
                changed = True
        if changed:
            env.save(update_fields=['cpu', 'ram'])


def _noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('apm', '0003_application_exige_ssl'),
    ]

    operations = [
        migrations.RunPython(_clean_numeric, _noop),
        migrations.AddField(
            model_name='role',
            name='type_role',
            field=models.CharField(
                blank=True, default='autre', max_length=20,
                choices=[
                    ('admin', 'Administrateur (users & rôles)'),
                    ('admin_systeme', 'Administrateur Système'),
                    ('membre_dsi', 'Membre DSI'),
                    ('autre', 'Autre'),
                ],
                help_text="Catégorie du rôle : pilote les accès de l'application.",
            ),
        ),
        migrations.AddField(
            model_name='role',
            name='peut_gerer_ressources',
            field=models.BooleanField(
                default=False,
                help_text="Peut gérer la capacité totale CPU/RAM (Administrateur Système)",
            ),
        ),
        migrations.AlterField(
            model_name='role',
            name='peut_gerer_users',
            field=models.BooleanField(default=False, help_text='Peut gérer les utilisateurs'),
        ),
        migrations.AlterField(
            model_name='role',
            name='peut_gerer_apps',
            field=models.BooleanField(default=False, help_text='Peut gérer les applications'),
        ),
        migrations.AlterField(
            model_name='role',
            name='peut_voir_dashboard_admin',
            field=models.BooleanField(default=False, help_text='Peut voir le dashboard admin'),
        ),
        migrations.AlterField(
            model_name='utilisateur',
            name='telephone',
            field=models.CharField(
                blank=True, default='', max_length=30,
                validators=[django.core.validators.RegexValidator(
                    message='Numéro de téléphone invalide.', regex='^\\+?[0-9 ]{6,20}$'
                )],
            ),
        ),
        migrations.AlterField(
            model_name='application',
            name='nom',
            field=models.CharField(
                max_length=150,
                validators=[django.core.validators.RegexValidator(
                    message="Utilisez uniquement lettres, chiffres, espaces, '-', '_' ou '.' (2 à 150 caractères).",
                    regex='^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 _\\-\\.]{1,149}$'
                )],
            ),
        ),
        migrations.AlterField(
            model_name='environnement',
            name='nom',
            field=models.CharField(
                help_text='Ex: DEV, RECETTE, PREPROD, PROD', max_length=50,
                validators=[django.core.validators.RegexValidator(
                    message="Utilisez uniquement lettres, chiffres, espaces, '-' ou '_' (2 à 50 caractères).",
                    regex='^[A-Za-zÀ-ÿ0-9][A-Za-zÀ-ÿ0-9 _\\-]{1,49}$'
                )],
            ),
        ),
        migrations.AlterField(
            model_name='environnement',
            name='adresse_ip',
            field=models.CharField(
                blank=True, default='', max_length=50,
                validators=[django.core.validators.RegexValidator(
                    message='Adresse IP invalide (ex: 192.168.1.10).',
                    regex='^$|^(\\d{1,3}\\.){3}\\d{1,3}$'
                )],
            ),
        ),
        migrations.AlterField(
            model_name='environnement',
            name='cpu',
            field=models.PositiveIntegerField(
                default=0, help_text='Nombre de vCPU alloués à cet environnement',
                validators=[django.core.validators.MaxValueValidator(1024)],
            ),
        ),
        migrations.AlterField(
            model_name='environnement',
            name='ram',
            field=models.PositiveIntegerField(
                default=0, help_text='RAM allouée à cet environnement, en Go',
                validators=[django.core.validators.MaxValueValidator(4096)],
            ),
        ),
        migrations.AlterField(
            model_name='environnement',
            name='id_application',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                related_name='environnements', to='apm.application',
                help_text="Peut être laissée vide à la création puis liée à une application ensuite.",
            ),
        ),
        migrations.AlterField(
            model_name='nomdomaine',
            name='nom_domaine',
            field=models.CharField(
                max_length=200,
                validators=[django.core.validators.RegexValidator(
                    message='Format de domaine invalide (ex: exemple.tn).',
                    regex='^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\\.[A-Za-z0-9-]{1,63})+$'
                )],
            ),
        ),
        migrations.AlterField(
            model_name='certificatssl',
            name='domaine',
            field=models.CharField(
                max_length=200,
                validators=[django.core.validators.RegexValidator(
                    message='Format de domaine invalide (ex: exemple.tn).',
                    regex='^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\\.[A-Za-z0-9-]{1,63})+$'
                )],
            ),
        ),
        migrations.CreateModel(
            name='RessourcesGlobales',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cpu_total', models.PositiveIntegerField(
                    default=0, help_text='Capacité totale en vCPU',
                    validators=[django.core.validators.MaxValueValidator(100000)],
                )),
                ('ram_total', models.PositiveIntegerField(
                    default=0, help_text='Capacité totale de RAM, en Go',
                    validators=[django.core.validators.MaxValueValidator(100000)],
                )),
                ('maj_le', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Ressources globales',
                'verbose_name_plural': 'Ressources globales',
            },
        ),
    ]
