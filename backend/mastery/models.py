from django.utils import timezone
from django.db import models
from django.db.models import Q
from nanoid import generate
from .querysets import GroupQuerySet

ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_nanoid(size=12):
    return generate(ALPHABET, size)


class BaseModel(models.Model):
    """
    Abstract base model that provides common fields for all models.
    """
    id = models.CharField(primary_key=True, max_length=50, default=generate_nanoid, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    maintained_at = models.DateTimeField(null=True)
    deleted_at = models.DateTimeField(null=True)  # soft delete
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True,
                                   related_name='created_%(class)s_set')
    updated_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True,
                                   related_name='updated_%(class)s_set')

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
    is_service_enabled_for_students = models.BooleanField(default=False)  # can students use the service
    is_group_goal_enabled = models.BooleanField(default=True)  # can group goals can be created
    is_student_list_enabled = models.BooleanField(default=False)  # can teachers see the /students menu item
    is_goal_title_enabled = models.BooleanField(default=True)  # are goals displayed with titles
    # which subjects can be used: 'only-custom' (owned by school), 'only-group', 'all'
    subjects_allowed = models.CharField(max_length=50, null=False, default='all')

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

    def get_teachers(self):
        """
        Get all teachers in this school.
        Only counts a user as a teacher here if they have a teacher role in a group
        that belongs to this school.
        """
        return User.objects.filter(
            user_groups__group__school=self,
            user_groups__role__name='teacher'
        ).distinct()

    def set_employed_user(self, user, role):
        """Add a user to this school with the specified role"""
        if isinstance(role, str):
            role, _ = Role.objects.get_or_create(name=role)

        user_school = UserSchool.objects.filter(
            user=user,
            school=self,
            role=role
        ).first()
        return user_school or UserSchool.objects.create(
            user=user,
            school=self,
            role=role
        )

    def get_employed_user(self, role_name):
        """Get all employed users, by optional role_name"""
        if role_name:
            return User.objects.filter(
                user_schools__school=self,
                user_schools__role__name=role_name
            )
        return User.objects.filter(user_schools__school=self)


class Subject(BaseModel):
    """
    A Subject represents something taught. If owned_by_school is unset, the row is Feide synchronized and will be overwritten by import scripts.
    Refer to UDIR grep for list of possible subjects
    """
    display_name = models.CharField(max_length=200)
    short_name = models.CharField(max_length=200)
    owned_by_school = models.ForeignKey(School, on_delete=models.CASCADE,
                                        null=True, related_name='owned_subjects')
    grep_code = models.CharField(max_length=200, null=True)  # UDIR grep code
    grep_group_code = models.CharField(max_length=200, null=True)  # UDIR grep code opplæringsfag

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
    groups = models.ManyToManyField(
        'Group', through='UserGroup', through_fields=('user', 'group'), null=True,
        related_name='members')
    schools = models.ManyToManyField(
        'School', through='UserSchool', through_fields=('user', 'school'),
        related_name='employees')
    is_superadmin = models.BooleanField(default=False)  # caution, site-wide admin

    def _get_groups_with_role(self, role_name):
        """Get all groups where user has a specific role"""
        return self.groups.filter(user_groups__role__name=role_name)

    def _get_groups_of_type(self, group_type):
        """Get all groups of a specific type (e.g. 'basis', 'teaching')"""
        return self.groups.filter(type=group_type)

    def get_schools(self):
        """Return all schools a user belongs to, via group or school memberships"""
        group_schools = School.objects.filter(groups__members=self)
        school_schools = School.objects.filter(user_schools__user=self)
        return (group_schools | school_schools).distinct()

    def has_role_at_school(self, role_name, school):
        """Check if user has a specific role at a given school"""
        return UserSchool.objects.filter(
            user=self,
            school=school,
            role__name=role_name
        ).exists()

    @property
    def student_groups(self):
        """Get all groups where user is a student"""
        return self._get_groups_with_role('student')

    @property
    def teacher_groups(self):
        """Get all groups where user is a teacher"""
        return self._get_groups_with_role('teacher')

    @property
    def basis_groups(self):
        """Get all basis groups where user is a member"""
        return self._get_groups_of_type('basis')

    @property
    def teaching_groups(self):
        """Get all teaching groups where user is a member"""
        return self._get_groups_of_type('teaching')

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
    A Role represents a role a User can have in a Group. So far we only have 'student', 'teacher', 'staff', 'admin', 'inspector'.
    """
    name = models.CharField(max_length=200)


class Group(BaseModel):
    """
    A Group represents a collection of Users in the system. Basis and teaching groups are the only types so far.
    """
    objects = GroupQuerySet.as_manager()  # Enable custom querysets

    feide_id = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200)
    type = models.CharField(max_length=200)  # either 'basis' or 'teaching' for now
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='groups')
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, related_name='groups')
    valid_from = models.DateTimeField(null=True)
    valid_to = models.DateTimeField(null=True)
    is_enabled = models.BooleanField(default=False)  # whether the group is active in the system

    def is_currently_valid(self):
        """Return True if in valid_from <--> valid_to range, or if no range is set"""
        return Group.objects.filter(id=self.id).within_validity_period().exists()

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
            role, _ = Role.objects.get_or_create(name=role)

        return UserGroup.objects.create(user=user, group=self, role=role)


class UserGroup(BaseModel):
    """
    A UserGroup represents a User in a Group with a specific Role. Teacher/Student roles are stored on UserGroup
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='user_groups')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False, related_name='user_groups')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, related_name='user_groups')

    class Meta:
        unique_together = ('user', 'group', 'role')


class UserSchool(BaseModel):
    """
    A UserSchool represents a User in a School with a specific Role. We use this to model roles that are not connected to a specific Group, e.g. school admins
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='user_schools')
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, related_name='user_schools')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=False, related_name='user_schools')

    class Meta:
        unique_together = ('user', 'school', 'role')


class MasterySchema(BaseModel):
    """
    A MasterySchema models how student mastery, with regards to a specific Goal, is considered.
    """
    title = models.CharField(max_length=200, null=False, default="Navnløst mestringsskjema")
    description = models.TextField(null=True)
    config = models.JSONField(null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False, related_name='mastery_schemas')
    is_default = models.BooleanField(default=False)  # is this the default schema for the school


class Goal(BaseModel):
    """
    A Goal represents something a student should strive towards. A Goal is either for all students in a Group (if goal.group is set), or personal for a specific student (if goal.student is set)

    The integer value sort_order is relative to goal.subject (for personal goals) or goal.group.subject (for group goals) and won't make sense to use across subjects.
    """
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(null=True)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='goals')
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='goals')
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='goals')
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=False,
                               related_name='goals')  # for easier querying
    previous_goal = models.ForeignKey('Goal', on_delete=models.SET_NULL, null=True)
    mastery_schema = models.ForeignKey(
        MasterySchema, on_delete=models.SET_NULL, null=True, related_name='goals')
    sort_order = models.IntegerField(null=True)
    is_relevant = models.BooleanField(default=True)  # keep old goals for history

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(group__isnull=False) | models.Q(student__isnull=False),
                name='goal_group_or_student'),]

    @property
    def is_personal(self):
        return self.group is None and self.student is not None


class Situation(BaseModel):
    """
    A Situation represents a case wherein student mastery is observed. This can be a lesson, a test, conversation, or any other situation where a student demonstrates mastery
    """
    title = models.CharField(max_length=200, null=False)
    description = models.TextField(null=True)
    happens_at = models.DateTimeField(null=True)


class Observation(BaseModel):
    """
    An Observation represents an observation of a student, performed by a teacher or student. Only teachers, inspectors and admins can access an observation if is_visible_to_student is False.
    """
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, null=False, related_name='observations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False,
                                related_name='observations_received')
    observer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                 related_name='observations_performed')
    situation = models.ForeignKey(Situation, on_delete=models.SET_NULL, null=True)
    mastery_value = models.IntegerField(null=True)
    mastery_description = models.TextField(null=True)
    feedforward = models.TextField(null=True)
    observed_at = models.DateTimeField(null=True)
    is_visible_to_student = models.BooleanField(default=True)

    class Meta:
        ordering = ["observed_at"]


class Status(BaseModel):
    """
    A status represents a snapshot of a students mastery at a point in time, typically in a subject, e.g. how is Lois doing in math (all math Goals are then considered)
    """
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='statuses')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, null=False, related_name='statuses')
    estimated_at = models.DateTimeField(null=True)
    mastery_value = models.IntegerField(null=True)
    mastery_description = models.TextField(null=True)
    feedforward = models.TextField(null=True)


class DataMaintenanceTask(BaseModel):
    """
    A DataMaintenanceTask represents a task that maintains data in the system, such as importing groups for a school.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('finished', 'Finished'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    job_name = models.CharField(max_length=200, blank=False)  # e.g. 'fetch_groups_for_school'
    job_params = models.JSONField(null=True, blank=False)  # JSON field for params the job needs
    display_name = models.CharField(max_length=200, null=True, blank=False)  # human-readable name of the task
    handler_name = models.CharField(max_length=200, null=True, blank=False)  # handler instance
    is_overwrite_enabled = models.BooleanField(default=False)  # overwrite/update existing data
    is_crash_on_error_enabled = models.BooleanField(default=False)  # should task crash on error
    started_at = models.DateTimeField(null=True)
    failed_at = models.DateTimeField(null=True)  # only set if task failed
    finished_at = models.DateTimeField(null=True)  # only set if successful
    last_heartbeat_at = models.DateTimeField(null=True)  # last time the task reported progress
    earliest_run_at = models.DateTimeField(null=True, default=timezone.now)  # earliest execution time
    result = models.JSONField(null=True, blank=False)  # JSON field to store updated result of task execution
    attempts = models.IntegerField(default=0)  # number of attempts made (initial + retries)
