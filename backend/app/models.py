from django.db import models
from nanoid import generate

alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_nanoid():
    return generate(alphabet, 12)

class School(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    org_number = models.CharField(max_length=50)
    owner = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Subject(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    fagkode = models.CharField(max_length=200)
    opplaringsfagkode = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    name = models.CharField(max_length=200)
    feide_id = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    picture = models.CharField(max_length=500)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)

class Role(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Group(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.RESTRICT, null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.RESTRICT, null=False, blank=False)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UserGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'group', 'role')

# Observation, Goal, Situation, mastery-stuff
