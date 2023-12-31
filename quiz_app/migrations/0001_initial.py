# Generated by Django 4.2.2 on 2023-08-25 17:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('verification_code', models.CharField(max_length=4)),
                ('is_verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_text', models.CharField(max_length=400)),
                ('option_a', models.CharField(max_length=200)),
                ('option_b', models.CharField(max_length=200)),
                ('option_c', models.CharField(max_length=200)),
                ('option_d', models.CharField(max_length=200)),
                ('correct_answer', models.CharField(max_length=100)),
                ('max_score', models.IntegerField(default=0)),
                ('code', models.CharField(blank=True, editable=False, max_length=12)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=2, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('total_score', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='UserResponse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_answer', models.CharField(max_length=1)),
                ('score', models.IntegerField(default=0)),
                ('answered_question_codes', models.TextField(blank=True)),
                ('correct_answer', models.CharField(max_length=1)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_responses', to='quiz_app.question')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_responses', to='quiz_app.userdetails')),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='quiz_app.userdetails')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quiz_app.questioncategory'),
        ),
    ]
