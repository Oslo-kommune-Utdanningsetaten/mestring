import pytest
from django.test import Client
from mastery.models import School, User, Group, Role, Subject

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
        name="Teacher", 
        feide_id="teacher-id@example.com",
        email="teacher@example.com"
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
def teaching_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:some-teaching-group",
        display_name="Engelsk 7a",
        type="teaching",
        school=school
    )

@pytest.fixture
def teaching_group_with_members(db, roles, teacher, student, other_student, teaching_group):
    student_role, teacher_role = roles
    teaching_group.add_member(teacher, teacher_role)
    teaching_group.add_member(student, student_role)
    teaching_group.add_member(other_student, student_role)
    return teaching_group


@pytest.fixture
def teaching_group_without_members(db, school):
    return Group.objects.create(
        feide_id="fc:group:teaching-group-no-members",
        display_name="Other Group",
        type="teaching",
        school=school
    )

@pytest.fixture
def subject_with_group(db, teaching_group_with_members):  # changed dependency
    # Owned by school is None to simulate group subject
    subject = Subject.objects.create(
        display_name = "Engelsk 7. årstrinn",
        short_name = "Engelsk",
        grep_code = "ENG0007",
        grep_group_code = "ENG1Z03",
        owned_by_school = None,
    )
    teaching_group_with_members.subject = subject  # updated variable name
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
