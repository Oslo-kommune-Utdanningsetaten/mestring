import pytest

@pytest.mark.django_db
def test_groups(teaching_group_with_members):
    """Test group accessor methods """
    # Test various role acceessors
    assert teaching_group_with_members.get_members().count() == 3
    assert teaching_group_with_members.get_students().count() == 2
    assert teaching_group_with_members.get_teachers().count() == 1
    assert teaching_group_with_members.get_members(role='student').count() == 2
    assert teaching_group_with_members.get_members(role='teacher').count() == 1
