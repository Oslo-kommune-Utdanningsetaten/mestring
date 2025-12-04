import pytest
from mastery.data_import.cleaner_bot import update_data_integrity
from mastery import models
from django.utils import timezone


@pytest.fixture
def valid_group(school):
    now = timezone.now()
    return models.Group.objects.create(
        feide_id="fc:group:some-basis-group-valid",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now + timezone.timedelta(days=1)
    )


@pytest.fixture
def invalid_group(school):
    now = timezone.now()
    return models.Group.objects.create(
        feide_id="fc:group:some-basis-group-invalid",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True,
        deleted_at=None,
        valid_from=now - timezone.timedelta(days=3),
        valid_to=now - timezone.timedelta(days=1)
    )


@pytest.fixture
def observation(student, goal_personal):
    return models.Observation.objects.create(
        student=student,
        goal=goal_personal,
        is_visible_to_student=True
    )


@pytest.fixture
def other_observation(other_student, goal_personal):
    return models.Observation.objects.create(
        student=other_student,
        goal=goal_personal,
        is_visible_to_student=True
    )


@pytest.fixture
def personal_goal(db, student):
    return models.Goal.objects.create(
        title="Lese 2 bøker",
        student=student,
    )


@pytest.fixture
def group_goal(db, valid_group, student, student_role):
    valid_group.add_member(student, student_role)
    return models.Goal.objects.create(
        title="Lese 2 bøker",
        group=valid_group,
    )


@pytest.fixture
def other_student_personal_goal(db, other_student):
    return models.Goal.objects.create(
        title="Lese 2 bøker",
        student=other_student,
    )


@pytest.mark.django_db
def test_soft_delete_unmaintained_valid_group(valid_group):
    now = timezone.now()

    # unmaintained valid group should be soft-deleted
    valid_group.maintained_at = now - timezone.timedelta(days=10)
    valid_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 1
    assert valid_group.deleted_at is not None

    # unmaintained, deleted group should not be handled
    previous_deleted_at = valid_group.deleted_at
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert valid_group.deleted_at == previous_deleted_at


@pytest.mark.django_db
def test_soft_delete_unmaintained_invalid_group(invalid_group):
    now = timezone.now()
    invalid_group.maintained_at = now - timezone.timedelta(days=10)
    invalid_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    invalid_group.refresh_from_db()
    # unmaintained invalid group should not be soft-deleted
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert invalid_group.deleted_at is None


@pytest.mark.django_db
def test_keep_maintained_user(student):
    now = timezone.now()
    # Don't soft-delete maintained user
    student.maintained_at = now
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_unmaintained_user(student):
    now = timezone.now()
    # Soft-delete unmaintained user without active memberships
    student.maintained_at = now - timezone.timedelta(days=10)
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 1
    assert student.deleted_at is not None


@pytest.mark.django_db
def test_keep_user_with_membership(student, student_role, valid_group):
    now = timezone.now()
    # Don't soft-delete user with active memberships
    valid_group.add_member(student, student_role)
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_keep_superadmin_user(student):
    now = timezone.now()
    # Don't soft-delete superadmin
    student.is_superadmin = True  # unlikely for a student, but hey
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_observation(student, observation, other_observation):
    now = timezone.now()
    # Soft-delete observation for soft-deleted student
    student.deleted_at = now
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    observation.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["observation"]["soft-deleted"] == 1
    assert observation.deleted_at is not None
    # Don't soft-delete observation for non-deleted student
    other_observation.refresh_from_db()
    assert other_observation.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_personal_goal(
        student, personal_goal, group_goal, other_student_personal_goal):
    now = timezone.now()
    # Initial cleanup -> no deletes
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    personal_goal.refresh_from_db()
    group_goal.refresh_from_db()
    other_student_personal_goal.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert personal_goal.deleted_at is None
    assert group_goal.deleted_at is None
    assert other_student_personal_goal.deleted_at is None

    # Soft-delete personal goal for soft-deleted student
    student.deleted_at = now
    student.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    personal_goal.refresh_from_db()
    group_goal.refresh_from_db()
    other_student_personal_goal.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["goal"]["soft-deleted"] == 1
    assert personal_goal.deleted_at is not None
    assert group_goal.deleted_at is None
    assert other_student_personal_goal.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_group_goal(
        personal_goal, group_goal, other_student_personal_goal, valid_group):
    now = timezone.now()
    # Initial cleanup -> no deletes
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    personal_goal.refresh_from_db()
    group_goal.refresh_from_db()
    other_student_personal_goal.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert personal_goal.deleted_at is None
    assert group_goal.deleted_at is None
    assert other_student_personal_goal.deleted_at is None

    # Soft-delete group goal for soft-deleted group
    valid_group.deleted_at = now
    valid_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    personal_goal.refresh_from_db()
    group_goal.refresh_from_db()
    other_student_personal_goal.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["goal"]["soft-deleted"] == 1
    assert group_goal.deleted_at is not None
    assert personal_goal.deleted_at is None
    assert other_student_personal_goal.deleted_at is None


@pytest.mark.django_db
def test_do_not_soft_delete_user_group(student, student_role, valid_group):
    now = timezone.now()
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    # Initial cleanup -> no deletes
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    user_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["soft-deleted"] == 0
    assert user_group.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_unmaintained_user_group(student, student_role, valid_group):
    now = timezone.now()
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    # Soft-delete user_group if unmaintained and group is valid
    user_group.maintained_at = now - timezone.timedelta(days=10)
    user_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    user_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["soft-deleted"] == 1
    assert user_group.deleted_at is not None


@pytest.mark.django_db
def test_soft_delete_user_group_for_deleted_group(student, student_role, valid_group):
    now = timezone.now()
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    # Soft-delete user_group if group is soft-deleted
    valid_group.deleted_at = now
    valid_group.save()
    result = update_data_integrity(now)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    user_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["soft-deleted"] == 1
    assert user_group.deleted_at is not None
