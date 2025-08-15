import pytest

@pytest.mark.django_db
def test_group_membership(teaching_group_with_members):
    """Test group accessor methods """
    # Test various role acceessors
    assert teaching_group_with_members.get_members().count() == 3
    assert teaching_group_with_members.get_students().count() == 2
    assert teaching_group_with_members.get_teachers().count() == 1
    assert teaching_group_with_members.get_members(role='student').count() == 2
    assert teaching_group_with_members.get_members(role='teacher').count() == 1


@pytest.mark.django_db
def test_user_school_affiliation(teaching_group_with_members, school):
    """Test user affiliation to school, via group"""
    # Groups should connect a user to a school
    teacher = teaching_group_with_members.get_teachers().first()
    student = teaching_group_with_members.get_students().first()
    assert teacher.get_schools().first().id == school.id 
    assert student.get_schools().first().id == school.id
