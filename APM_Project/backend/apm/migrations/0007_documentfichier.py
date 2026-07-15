import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apm', '0006_notification_historique_profil'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentFichier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fichier', models.FileField(upload_to='documents/%Y/%m/')),
                ('nom_original', models.CharField(max_length=255)),
                ('type_fichier', models.CharField(choices=[('pdf','PDF'),('docx','Word'),('xlsx','Excel'),('png','Image PNG'),('jpg','Image JPG'),('autre','Autre')], default='autre', max_length=10)),
                ('taille_ko', models.PositiveIntegerField(default=0)),
                ('uploade_le', models.DateTimeField(auto_now_add=True)),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fichiers', to='apm.document')),
                ('uploade_par', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'verbose_name': 'Fichier document', 'verbose_name_plural': 'Fichiers documents'},
        ),
    ]
