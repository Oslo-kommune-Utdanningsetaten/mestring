import pytest

@pytest.mark.django_db
def test_groups(group_with_members):
    """Test group accessor methods """
    # Test various role acceessors
    assert group_with_members.get_members().count() == 3
    assert group_with_members.get_students().count() == 2
    assert group_with_members.get_teachers().count() == 1
    assert group_with_members.get_members(role='student').count() == 2
    assert group_with_members.get_members(role='teacher').count() == 1
