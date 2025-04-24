from django.db import models
from nanoid import generate

alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_nanoid():
    return generate(alphabet, 12)


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models.
    """
    id = models.CharField(primary_key=True, max_length=12, default=generate_nanoid, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class School(BaseModel):
    """
    School matches a Feide school 1:1 
    https://docs.feide.no/reference/apis/groups_api/group_types/pse_school.html
    """
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    org_number = models.CharField(max_length=50)
    owner = models.CharField(max_length=200)


class Subject(BaseModel):
    """
    A Subject represents something taught in a Feide teaching group
    https://docs.feide.no/reference/apis/groups_api/group_types/pse_teaching.html
    Refer to UDIR GREP for list of possible subjects
    """
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    subject_code = models.CharField(max_length=200)
    group_subject_code = models.CharField(max_length=200)


class User(BaseModel):
    """
    A User represents a user in the system. Students, teachers and faculty are all modeled as users.
    A User belongs to a School via Group
    """
    name = models.CharField(max_length=200)
    feide_id = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)


class Role(BaseModel):
    """
    A Role represents a role a User can have in a Group
    """
    name = models.CharField(max_length=200)


class Group(BaseModel):
    """
    A Group represents a collection of Users in the system. Basis and teaching groups will be the most common, but School will also be modeled as a Group
    """
    feide_id = models.CharField(max_length=200)
    display_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)
    subject = models.ForeignKey(Subject, on_delete=models.RESTRICT, null=True, blank=True)
    school = models.ForeignKey(School, on_delete=models.RESTRICT, null=False, blank=False)
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_to = models.DateTimeField(null=True, blank=True)


class UserGroup(BaseModel):
    """
    A UserGroup represents a User in a Group with a specific Role. Teacher status in a group will be modeled as a UserGroup with the role of teacher
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        unique_together = ('user', 'group', 'role')


class Goal(BaseModel):
    """
    A Goal represents something a studen should strive towards. A Goal is either for all students in a Group (if goal.group is set), or personal for a specific student (if goal.student is set)
    """
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, null=True, blank=True)
    student = models.ForeignKey(User, on_delete=models.RESTRICT, null=True, blank=True)
    previous_goal = models.ForeignKey('Goal', on_delete=models.RESTRICT, null=True, blank=True)
    mastery_schema = models.JSONField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(group__isnull=False) | models.Q(student__isnull=False),
                name='goal_group_or_student'
            ),
        ]


class Situation(BaseModel):
    """
    A Situation represents a case wherein student mastery is observed. This can be a lesson, a test, conversation, or any other situation where a student demonstrates mastery
    """
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    happens_at = models.DateTimeField(null=True, blank=True)


class Observation(BaseModel):
    """
    An Observation represents an observation of a student by a teacher or student
    """
    goal = models.ForeignKey(Goal, on_delete=models.RESTRICT, null=False, blank=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='observations_received')
    observer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='observations_performed')
    situation = models.ForeignKey(Situation, on_delete=models.SET_NULL, null=True, blank=True)
    mastery_value = models.IntegerField()
    mastery_description = models.TextField(null=True, blank=True)

