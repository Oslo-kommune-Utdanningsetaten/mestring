from django.db import models
from nanoid import generate

alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_nanoid():
    return generate(alphabet, 12)

# School matches a Feide school 1:1 
# https://docs.feide.no/reference/apis/groups_api/group_types/pse_school.html
class School(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    org_number = models.CharField(max_length=50)
    owner = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# A Subject represents something taught in a Feide teaching group
# https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
# Refer to UDIR GREP for list of possible subjects
class Subject(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    fagkode = models.CharField(max_length=200)
    opplaringsfagkode = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# A User represents a user in the system. Students, teachers and faculty are all modeled as users. A user belongs to a School via Group
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


# A Role represents a role a User can have in a Group
class Role(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# A Group represents a group of students in the system. Basis and teaching groups will be the most common, but School will also be modeled as a Group
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


# A UserGroup represents a user in a group with a specific role. Teacher status in a group will be modeled as a UserGroup with the role of teacher
class UserGroup(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'group', 'role')


# A Goal represents a goal for all students in a group (if goal.group is set). Or a personal goal for a student (if goal.student is set)
class Goal(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    previous_goal = models.ForeignKey('Goal', on_delete=models.RESTRICT, null=True, blank=True)
    mastery_schema = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(group__isnull=False) | models.Q(student__isnull=False),
                name='goal_group_or_student'
            ),
        ]


# A Situation represents a situation where a student is observed. This can be a lesson, a test, or any other situation where the student is observed
class Situation(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    happens_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# An Observation represents an observation of a student by a teacher, student
class Observation(models.Model):
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    goal = models.ForeignKey(Goal, on_delete=models.RESTRICT, null=False, blank=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    observer = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, blank=False)
    situation = models.ForeignKey(Situation, on_delete=models.RESTRICT, null=True, blank=True)
    mastery_value = models.IntegerField()
    mastery_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

