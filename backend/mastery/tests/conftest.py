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
    # Superadmin user
    superadmin_user = User.objects.create(
        name="Superadmin", 
        feide_id="superadmin001@kakrafoon.kommune.no",
        email="superadmin001@kakrafoon.kommune.no",
        is_superadmin=True
    )
    return superadmin_user


@pytest.fixture
def teaching_group_with_members(db, school, roles):
    # Create a teaching group
    group = Group.objects.create(
        feide_id="fc:group:test",
        display_name="Test Group",
        type="teaching",
        school=school
    )
    # create a subject for the group
    subject = Subject.objects.create(
        display_name = "Test Engelsk 7. årstrinn",
        short_name = "Engelsk",
        owned_by_school = None,
        grep_code = "ENG0007",
        grep_group_code = "ENG1Z03",
    )
    group.subject = subject
    group.save()
    # Create users
    student_1 = User.objects.create(
        name="Student 1", 
        feide_id="user-id-1@example.com",
        email="user1@example.com"
    )
    student_2 = User.objects.create(
        name="Student 2", 
        feide_id="user-id-2@example.com",
        email="user2@example.com"
    )
    teacher_1 = User.objects.create(
        name="Teacher 1", 
        feide_id="user-id-3@example.com",
        email="user3@example.com"
    )
    student_role, teacher_role = roles
    
    # Add members to the group
    group.add_member(student_1, student_role)
    group.add_member(student_2, student_role)
    group.add_member(teacher_1, teacher_role)
    return group


@pytest.fixture
def teaching_group_with_no_members(db, school):
    group = Group.objects.create(
        feide_id="fc:group:teaching-group-no-members",
        display_name="Other Group",
        type="teaching",
        school=school
    )
    return group


@pytest.fixture
def teaching_group_owned_by_school(db, school):
    group = Group.objects.create(
        feide_id="fc:group:teaching-group-owned-by-school",
        display_name="Some other Group",
        type="teaching",
        school=school
    )
    subject = Subject.objects.create(
        display_name = "Test Engelsk 6. årstrinn",
        short_name = "Engelsk",
        owned_by_school = school,
        grep_code = "ENG0006",
        grep_group_code = "ENG1Z03",
    )
    group.subject = subject
    group.save()
    return group
