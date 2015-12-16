# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trackingapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceExpansion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('expansion', models.ForeignKey(to='trackingapp.Expansion')),
                ('source', models.ForeignKey(to='trackingapp.Source')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
