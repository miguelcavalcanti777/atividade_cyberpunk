from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cyberpunk', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Modalidade',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nome', models.CharField(blank=True, max_length=100, null=True)),
                ('alunos', models.IntegerField(blank=True, null=True)),
                ('data_inicio', models.DateField(blank=True, null=True)),
                ('ativa', models.BooleanField(blank=True, null=True)),
            ],
            options={
                'db_table': 'modalidade',
                'ordering': ['nome', 'id'],
                'managed': False,
            },
        ),
    ]
