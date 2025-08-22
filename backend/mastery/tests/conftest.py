import pytest
from django.test import Client
from mastery.models import School, User, Group, Role, Subject, Goal

# Basic fixture for Django client
@pytest.fixture
def client():
    return Client()


# Fixture for authenticated client
@pytest.fixture
def auth_client(db, client):
    return client


@pytest.fixture
def school(db):
    return School.objects.create(
        feide_id="fc:org:kakrafoon.kommune.no:unit:NO987654321",
        display_name="Kakrafoon vgs",
        org_number="987654321",
        owner="kakrafoon.kommune.no",
    )

@pytest.fixture
def other_school(db):
    return School.objects.create(
        feide_id="fc:org:kakrafoon.kommune.no:unit:NO123456789",
        display_name="Kakrafoon barneskole",
        org_number="123456789",
        owner="kakrafoon.kommune.no",
    )

@pytest.fixture
def roles(db):
    # Student and teacher roles
    student_role = Role.objects.create(name="student")
    teacher_role = Role.objects.create(name="teacher")
    return student_role, teacher_role

@pytest.fixture
def superadmin(db) -> User:
    return User.objects.create(
        name="Superadmin", 
        feide_id="superadmin001@kakrafoon.kommune.no",
        email="superadmin001@kakrafoon.kommune.no",
        is_superadmin=True
    )

@pytest.fixture
def teacher(db) -> User:
    return User.objects.create(
        name="Teacher 1", 
        feide_id="teacher-id@example.com",
        email="teacher@example.com"
    )

@pytest.fixture
def other_teacher(db) -> User:
    return User.objects.create(
        name="Teacher 2", 
        feide_id="other-teacher-id@example.com",
        email="other-teacher@example.com"
    )

@pytest.fixture
def other_school_teacher(db) -> User:
    return User.objects.create(
        name="Teacher 3", 
        feide_id="other-school-teacher-id@example.com",
        email="other-school-teacher@example.com"
    )

@pytest.fixture
def student(db) -> User:
    return User.objects.create(
        name="Student 1", 
        feide_id="student-id@example.com",
        email="student@example.com"
    )

@pytest.fixture
def other_student(db) -> User:
    return User.objects.create(
        name="Student 2",
        feide_id="other-student-id@example.com",
        email="other-student@example.com"
    )

@pytest.fixture
def other_school_student(db) -> User:
    return User.objects.create(
        name="Student 3",
        feide_id="other-school-student-id@example.com",
        email="other-school-student@example.com"
    )

@pytest.fixture
def teaching_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:some-teaching-group",
        display_name="Engelsk 7a",
        type="teaching",
        school=school
    )

@pytest.fixture
def teaching_group_with_members(db, roles, teacher, student, teaching_group):
    student_role, teacher_role = roles
    teaching_group.add_member(teacher, teacher_role)
    teaching_group.add_member(student, student_role)
    return teaching_group

@pytest.fixture
def other_teaching_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:other-teaching-group",
        display_name="Engelsk 8a",
        type="teaching",
        school=school
    )

@pytest.fixture
def other_school_teaching_group(db, other_school):
    return Group.objects.create(
        feide_id="fc:group:some-teaching-group-at-other-school",
        display_name="Engelsk 1a",
        type="teaching",
        school=other_school
    )

@pytest.fixture
def other_school_teaching_group_with_members(db, roles, other_school_teacher, other_school_student, other_school_teaching_group):
    student_role, teacher_role = roles
    other_school_teaching_group.add_member(other_school_teacher, teacher_role)
    other_school_teaching_group.add_member(other_school_student, student_role)
    return other_school_teaching_group

@pytest.fixture
def other_teaching_group_with_members(db, roles, other_teaching_group, other_teacher, other_student):
    student_role, teacher_role = roles
    other_teaching_group.add_member(other_teacher, teacher_role)
    other_teaching_group.add_member(other_student, student_role)
    return other_teaching_group


@pytest.fixture
def teaching_group_without_members(db, school):
    return Group.objects.create(
        feide_id="fc:group:teaching-group-no-members",
        display_name="Other Group",
        type="teaching",
        school=school
    )

@pytest.fixture
def subject_with_group(db, teaching_group_with_members):
    # Owned by school is None to simulate group subject
    subject = Subject.objects.create(
        display_name = "Engelsk 7. årstrinn",
        short_name = "Engelsk",
        grep_code = "ENG0007",
        grep_group_code = "ENG1Z03",
        owned_by_school = None,
    )
    teaching_group_with_members.subject = subject
    teaching_group_with_members.save()
    return subject

@pytest.fixture
def subject_without_group(db, school):
    # Owned by school is set to simulate subject managed by school
    return Subject.objects.create(
        display_name = "Sosiale ferdigheter",
        short_name = "Sosialt",
        owned_by_school = school,
    )

@pytest.fixture
def goal_with_group(db, teaching_group_with_members):
    return Goal.objects.create(
        title="Lese 2 bøker",
        group=teaching_group_with_members,
    )

@pytest.fixture
def goal_personal(db, subject_without_group, other_student):
    return Goal.objects.create(
        title="Lese 2 bøker",
        student=other_student,
        subject=subject_without_group,
    )
