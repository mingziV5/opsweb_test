# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-11-09 06:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MasterConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cluster_name', models.CharField(max_length=100, verbose_name='数据库集群名称')),
                ('db_name', models.CharField(max_length=100, verbose_name='数据库名')),
                ('master_host', models.CharField(max_length=200, verbose_name='master主库地址')),
                ('master_port', models.IntegerField(default=3306, verbose_name='master库端口')),
                ('master_user', models.CharField(max_length=100, verbose_name='执行sql账号')),
                ('master_passwd', models.CharField(max_length=200, verbose_name='执行sql密码')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='修改时间')),
            ],
        ),
        migrations.CreateModel(
            name='SqlWorkflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workflow_name', models.CharField(max_length=100, verbose_name='sql工单名称')),
                ('proposer', models.CharField(max_length=150, verbose_name='申请人')),
                ('reviewer', models.CharField(max_length=150, verbose_name='审核人')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('review_time', models.DateTimeField(blank=True, null=True, verbose_name='审核时间')),
                ('finish_time', models.DateTimeField(blank=True, null=True, verbose_name='结束时间')),
                ('backup', models.CharField(choices=[(0, '否'), (1, '是')], max_length=10, verbose_name='是否备份')),
                ('review_content', models.TextField(verbose_name='自动审核返回的JSON')),
                ('cluster_db_name', models.CharField(max_length=200, verbose_name='执行目标库')),
                ('sql_content', models.TextField(verbose_name='具体执行内容')),
                ('excute_result', models.TextField(verbose_name='执行结果返回的JSON')),
            ],
        ),
        migrations.CreateModel(
            name='SqlWorkflowStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_name', models.CharField(max_length=50, verbose_name='工单状态')),
            ],
        ),
        migrations.AddField(
            model_name='sqlworkflow',
            name='status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inception.SqlWorkflowStatus'),
        ),
    ]
