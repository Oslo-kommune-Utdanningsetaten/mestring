import pytest
from django.test import Client
from mastery.models import School, User, Group, Role, UserGroup

# Basic fixture for Django client
@pytest.fixture
def client():
    return Client()

# Fixture for authenticated client
@pytest.fixture
def auth_client(db, client):
    # Implement authentication logic here
    # For example:
    # from django.contrib.auth import get_user_model
    # User = get_user_model()
    # user = User.objects.create_user(username='testuser', password='password')
    # client.force_login(user)
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
def roles(db):
    # Create a student role
    student_role = Role.objects.create(name="student")
    # Create a teacher role
    teacher_role = Role.objects.create(name="teacher")
    return student_role, teacher_role

@pytest.fixture
def group_with_members(db, school, roles):
    # Create a group
    group = Group.objects.create(
        feide_id="fc:group:test",
        display_name="Test Group",
        type="basis",
        school=school
    )
    
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