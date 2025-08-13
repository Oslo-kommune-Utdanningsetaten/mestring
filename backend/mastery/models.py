from django.db import models
from nanoid import generate

alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def generate_nanoid():
    return generate(alphabet, 12)


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models.
    """
    id = models.CharField(primary_key=True, max_length=50, default=generate_nanoid, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    maintained_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_%(class)s_set')
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_%(class)s_set')
    
    class Meta:
        abstract = True


class School(BaseModel):
    """
    School matches a Feide school 1:1 
    https://docs.feide.no/reference/apis/groups_api/group_types/pse_school.html
    """
    feide_id = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=10, null=True)
    org_number = models.CharField(max_length=50)
    owner = models.CharField(max_length=200, null=True)
    is_service_enabled = models.BooleanField(default=False)

    def ensure_short_name(self, short_name):
        """Update short_name (used by import)"""
        if not self.short_name == short_name:
            self.short_name = short_name
            self.save()

    def get_group_subjects(self):
        """
        Get all subjects used by this school via groups.
        These subjects are synchronized from Feide and will be overwritten by import scripts.
        """
        return Subject.objects.filter(groups__school=self).distinct()
    
    def get_all_subjects(self):
        """
        Get all subjects used by this school, both owned and synchronized.
        """
        return self.owned_subjects.all() | self.get_group_subjects()

class Subject(BaseModel):
    """
    A Subject represents something taught. If owned_by_school is unset, the row is Feide synchronized and will be overwritten by import scripts.
    Refer to UDIR grep for list of possible subjects
    """
    display_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    owned_by_school = models.ForeignKey(School, on_delete=models.RESTRICT, null=True, related_name='owned_subjects')
    grep_code = models.CharField(max_length=200, null=True) # UDIR grep code
    grep_group_code = models.CharField(max_length=200, null=True) # UDIR grep code opplæringsfag

    @property
    def is_feide_synchronized(self):
        """Convenience property to check if subject is Feide synchronized"""
        return self.owned_by_school is None


class User(BaseModel):
    """
    A User represents a user in the system. Students, teachers and faculty are all modeled as users.
    A User belongs to a School via Group
    """
    name = models.CharField(max_length=200)
    feide_id = models.CharField(max_length=200, unique=True)
    email = models.CharField(max_length=200)
    last_activity_at = models.DateTimeField(null=True)
    disabled_at = models.DateTimeField(null=True)
    groups = models.ManyToManyField('Group', through='UserGroup', through_fields=('user', 'group'), related_name='members', null=True)
    is_superadmin = models.BooleanField(default=False)

    def _get_groups_with_role(self, role_name):
        """Get all groups where user has a specific role"""
        return self.groups.filter(user_groups__role__name=role_name)
    
    def schools(self):
        """Return all schools a user belongs to, via group memeberships"""
        return School.objects.filter(groups__members=self).distinct()
    
    @property
    def student_groups(self):
        """Get all groups where user is a student"""
        return self._get_groups_with_role('student')
    
    @property
    def teacher_groups(self):
        """Get all groups where user is a teacher"""
        return self._get_groups_with_role('teacher')

    # Needed for DRF permissions
    @property
    def is_authenticated(self):
        return True

    # Needed for DRF permissions
    @property
    def is_anonymous(self):
        return False


class Role(BaseModel):
    """
    A Role represents a role a User can have in a Group
    """
    name = models.CharField(max_length=200)


class Group(BaseModel):
    """
    A Group represents a collection of Users in the system. Basis and teaching groups will be the most common, but School will also be modeled as a Group
    """
    feide_id = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200) # either 'basis' or 'teaching' for now
    subject = models.ForeignKey(Subject, on_delete=models.RESTRICT, null=True)
    school = models.ForeignKey(School, on_delete=models.RESTRICT, null=False, related_name='groups')
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    # members attribute added via User.groups reverse relation
    
    def get_members(self, role=None):
        """
        Get all users in this group, optionally filtered by role
        
        Args:
            role: Role name or Role object to filter by. If None, returns all members.
        
        Returns:
            QuerySet of User objects
        """
        if role is None:
            return self.members.all()
        
        if isinstance(role, str):
            return self.members.filter(user_groups__role__name=role)
        else:
            return self.members.filter(user_groups__role=role)
    

    def get_students(self):
        """Get all students in this group"""
        return self.get_members(role='student')
    
    def get_teachers(self):
        """Get all teachers in this group"""
        return self.get_members(role='teacher')
    
    def add_member(self, user, role):
        """
        Add a user to this group with the specified role
        
        Args:
            user: User object to add to the group
            role: Role object or string role name
            
        Returns:
            UserGroup object that was created
        """
        if isinstance(role, str):
            from mastery.models import Role
            role, created = Role.objects.get_or_create(name=role)
            
        return UserGroup.objects.create(user=user, group=self, role=role)


class UserGroup(BaseModel):
    """
    A UserGroup represents a User in a Group with a specific Role. Teacher/Student roles are stored on UserGroup
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='user_groups')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, blank=False, related_name='user_groups')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        unique_together = ('user', 'group', 'role')


class MasterySchema(BaseModel):
    """
    A MasterySchema models how student mastery, with regards to a specific Goal, is considered.
    """
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    config = models.JSONField(null=True)


class Goal(BaseModel):
    """
    A Goal represents something a student should strive towards. A Goal is either for all students in a Group (if goal.group is set), or personal for a specific student (if goal.student is set)

    The integer value sort_order is relative to goal.subject (for personal goals) or goal.group.subject (for group goals) and won't make sense to use across subjects.
    """
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    group = models.ForeignKey(Group, on_delete=models.RESTRICT, null=True)
    student = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.RESTRICT, null=True)
    previous_goal = models.ForeignKey('Goal', on_delete=models.RESTRICT, null=True)
    mastery_schema = models.ForeignKey(MasterySchema, on_delete=models.RESTRICT, null=True)
    sort_order = models.IntegerField(null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(group__isnull=False) | models.Q(student__isnull=False),
                name='goal_group_or_student'
            ),
        ]

    @property
    def is_personal(self):
        return self.group is None and self.student is not None

    @property
    def is_group(self):
        return self.student is None and self.group is not None 


class Situation(BaseModel):
    """
    A Situation represents a case wherein student mastery is observed. This can be a lesson, a test, conversation, or any other situation where a student demonstrates mastery
    """
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True)
    happens_at = models.DateTimeField(null=True)


class Observation(BaseModel):
    """
    An Observation represents an observation of a student, performed by a teacher or student. Only the observer can access the observation if it is private.
    """
    goal = models.ForeignKey(Goal, on_delete=models.RESTRICT, null=False, blank=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False, related_name='observations_received')
    observer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='observations_performed')
    situation = models.ForeignKey(Situation, on_delete=models.SET_NULL, null=True)
    mastery_value = models.IntegerField(null=True)
    mastery_description = models.TextField(null=True)
    feedforward = models.TextField(null=True)
    observed_at = models.DateTimeField(null=True)
    is_private = models.BooleanField(default=True)

    class Meta:
        ordering = ["observed_at"]


class Status(BaseModel):
    """
    A status represents a snapshot of a students mastery at a point in time, typically in a subject, e.g. how is Lois doing in math (all math Goals are then considered)
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=False, blank=False)
    estimated_at = models.DateTimeField(null=True)
    mastery_value = models.IntegerField(null=True)
    mastery_description = models.TextField(null=True)
    feedforward = models.TextField(null=True)
