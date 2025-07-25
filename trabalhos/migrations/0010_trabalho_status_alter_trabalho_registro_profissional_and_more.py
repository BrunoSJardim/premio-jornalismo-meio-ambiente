# Generated by Django 5.2 on 2025-07-24 11:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trabalhos', '0009_trabalho_chave_pix_trabalho_tipo_chave_pix'),
    ]

    operations = [
        migrations.AddField(
            model_name='trabalho',
            name='status',
            field=models.CharField(choices=[('pendente', 'Pendente'), ('aceito', 'Aceito'), ('rejeitado', 'Rejeitado')], default='pendente', max_length=20),
        ),
        migrations.AlterField(
            model_name='trabalho',
            name='registro_profissional',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='trabalho',
            name='veiculo_universidade',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
