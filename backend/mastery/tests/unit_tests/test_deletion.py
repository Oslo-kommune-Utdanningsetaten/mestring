
import pytest
from mastery.models import School, Subject, Group, User, Role, UserGroup

@pytest.mark.django_db
def test_group_deletion_cascades_to_user_groups():
    """
    Verify that deleting a Group also deletes the associated UserGroup entries.
    """
    # 1. Setup Data
    school = School.objects.create(
        feide_id="school1", 
        display_name="Test School", 
        org_number="123"
    )
    subject = Subject.objects.create(
        display_name="Math",
        short_name="MAT101"
    )
    group = Group.objects.create(
        feide_id="group1",
        display_name="Test Group",
        type="teaching",
        school=school,
        subject=subject
    )
    user = User.objects.create(
        name="Test User",
        feide_id="user1",
        email="test@example.com"
    )
    role = Role.objects.create(name="student")

    # 2. Create Link (UserGroup)
    user_group = UserGroup.objects.create(
        user=user,
        group=group,
        role=role
    )

    # 3. Verify it exists
    assert UserGroup.objects.filter(id=user_group.id).exists()

    # 4. Perform Deletion
    group.delete()

    # 5. Verify Cascade Deletion
    assert not UserGroup.objects.filter(id=user_group.id).exists(), "UserGroup should have been deleted when Group was deleted"
