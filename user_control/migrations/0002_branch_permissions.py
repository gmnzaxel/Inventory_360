# Generated to require branch on employees and expose product view permission.

from django.db import migrations, models


def assign_branch_to_employees(apps, schema_editor):
    User = apps.get_model('user_control', 'User')
    Branch = apps.get_model('control', 'Branch')
    for user in User.objects.filter(role='user', branch__isnull=True, business__isnull=False):
        branch = Branch.objects.filter(business=user.business).order_by('id').first()
        if branch:
            user.branch = branch
            user.save(update_fields=['branch'])


def grant_admin_product_view(apps, schema_editor):
    User = apps.get_model('user_control', 'User')
    User.objects.filter(role='admin').update(can_view_products=True)


class Migration(migrations.Migration):

    dependencies = [
        ('control', '0010_case_insensitive_uniques'),
        ('user_control', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='can_view_products',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(assign_branch_to_employees, migrations.RunPython.noop, elidable=True),
        migrations.RunPython(grant_admin_product_view, migrations.RunPython.noop, elidable=True),
        migrations.AddConstraint(
            model_name='user',
            constraint=models.CheckConstraint(
                check=models.Q(role='admin') | ~models.Q(branch__isnull=True),
                name='user_branch_required_for_non_admin',
            ),
        ),
    ]
