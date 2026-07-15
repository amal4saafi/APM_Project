import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apm', '0005_passwordresettoken'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_notif', models.CharField(choices=[('success','Succès'),('info','Information'),('warning','Avertissement'),('danger','Erreur')], default='info', max_length=20)),
                ('titre', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('lu', models.BooleanField(default=False)),
                ('cree_le', models.DateTimeField(auto_now_add=True)),
                ('action_url', models.CharField(blank=True, default='', max_length=255)),
                ('destinataire', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Notification', 'verbose_name_plural': 'Notifications', 'ordering': ['-cree_le']},
        ),
        migrations.CreateModel(
            name='HistoriqueAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=200)),
                ('modele', models.CharField(blank=True, default='', max_length=100)),
                ('objet_id', models.PositiveIntegerField(blank=True, null=True)),
                ('objet_repr', models.CharField(blank=True, default='', max_length=255)),
                ('details', models.TextField(blank=True, default='')),
                ('date_action', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('utilisateur', models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='historique_actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Historique action', 'verbose_name_plural': 'Historique actions', 'ordering': ['-date_action']},
        ),
        migrations.CreateModel(
            name='ProfilUtilisateur',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(blank=True, help_text='Photo de profil (JPG, PNG)', null=True, upload_to='profils/')),
                ('bio', models.CharField(blank=True, default='', max_length=300)),
                ('poste', models.CharField(blank=True, default='', max_length=150)),
                ('linkedin', models.URLField(blank=True, default='')),
                ('preferences', models.JSONField(blank=True, default=dict)),
                ('maj_le', models.DateTimeField(auto_now=True)),
                ('utilisateur', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profil', to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Profil utilisateur', 'verbose_name_plural': 'Profils utilisateurs'},
        ),
    ]
