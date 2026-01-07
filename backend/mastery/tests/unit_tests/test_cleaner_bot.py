import pytest
from mastery.data_import.cleaner_bot import update_data_integrity
from mastery import models
from django.utils import timezone
from mastery.constants import (
    DAYS_BEFORE_HARD_DELETE_OF_GROUP,
    DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION,
    DAYS_BEFORE_HARD_DELETE_OF_GOAL,
    DAYS_BEFORE_HARD_DELETE_OF_USER,
    HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP,
)


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
def personal_goal(db, school, student, subject_owned_by_school):
    return models.Goal.objects.create(
        title="Lese 2 bøker",
        student=student,
        subject=subject_owned_by_school,
        school=school,
    )


@pytest.fixture
def group_goal(db, school, valid_group, student, student_role):
    valid_group.add_member(student, student_role)
    return models.Goal.objects.create(
        title="Lese 2 bøker",
        group=valid_group,
        school=school,
    )


@pytest.fixture
def other_student_personal_goal(db, school, other_student):
    return models.Goal.objects.create(
        title="Lese 2 bøker",
        student=other_student,
        school=school,
    )


@pytest.mark.django_db
def test_soft_delete_unmaintained_valid_group(school, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }

    # unmaintained valid group should be soft-deleted
    valid_group.maintained_at = now - timezone.timedelta(days=10)
    valid_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 1
    assert valid_group.deleted_at is not None

    # unmaintained, deleted group should not be handled
    previous_deleted_at = valid_group.deleted_at
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    valid_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert valid_group.deleted_at == previous_deleted_at


@pytest.mark.django_db
def test_soft_delete_unmaintained_invalid_group(school, invalid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    invalid_group.maintained_at = now - timezone.timedelta(days=10)
    invalid_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    invalid_group.refresh_from_db()
    # unmaintained invalid group should not be soft-deleted
    assert final_chunk["is_done"] is True
    assert changes["group"]["soft-deleted"] == 0
    assert invalid_group.deleted_at is None


@pytest.mark.django_db
def test_keep_maintained_user(school, student):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Don't soft-delete maintained user
    student.maintained_at = now
    student.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_keep_user_with_membership(school, student, student_role, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Don't soft-delete user with active memberships
    valid_group.add_member(student, student_role)
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_unmaintained_user(school, student, student_role, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Soft-delete unmaintained user
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    user_group.deleted_at = now
    user_group.save()
    student.maintained_at = now - timezone.timedelta(days=10)
    student.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 1
    assert student.deleted_at is not None


@pytest.mark.django_db
def test_keep_superadmin_user(school, student):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Don't soft-delete superadmin
    student.is_superadmin = True  # unlikely for a student, but hey
    student.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    student.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user"]["soft-deleted"] == 0
    assert student.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_observation(school, student, observation, other_observation):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Soft-delete observation for soft-deleted student
    student.deleted_at = now
    student.save()
    result = update_data_integrity(school.org_number, options)
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
        school, student, personal_goal, group_goal, other_student_personal_goal):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
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
    result = update_data_integrity(school.org_number, options)
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
        school, personal_goal, group_goal, other_student_personal_goal, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
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
    result = update_data_integrity(school.org_number, options)
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
def test_do_not_soft_delete_user_group(school, student, student_role, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    user_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["soft-deleted"] == 0
    assert user_group.deleted_at is None


@pytest.mark.django_db
def test_soft_delete_unmaintained_user_group(school, student, student_role, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    # Soft-delete user_group if unmaintained and group is valid
    user_group.maintained_at = now - timezone.timedelta(days=10)
    user_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    user_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["soft-deleted"] == 1
    assert user_group.deleted_at is not None


@pytest.mark.django_db
def test_soft_delete_user_group_for_deleted_group(school, student, student_role, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    # Soft-delete user_group if group is soft-deleted
    valid_group.deleted_at = now
    valid_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    user_group.refresh_from_db()
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["soft-deleted"] == 1
    assert user_group.deleted_at is not None


@pytest.mark.django_db
def test_hard_delete_group(school, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    group_id = valid_group.id
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["group"]["hard-deleted"] == 0
    assert models.Group.objects.filter(id=group_id).exists()

    # Almost, but not quite ready for delete
    valid_group.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GROUP-1)
    valid_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["group"]["hard-deleted"] == 0
    assert models.Group.objects.filter(id=group_id).exists()

    # Hard-delete group which is has been soft-deleted a sufficient time
    valid_group.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GROUP)
    valid_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["group"]["hard-deleted"] == 1
    assert not models.Group.objects.filter(id=group_id).exists()


@pytest.mark.django_db
def test_hard_delete_user(school, student):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    user_id = student.id
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user"]["hard-deleted"] == 0
    assert models.User.objects.filter(id=user_id).exists()

    # Almost, but not quite ready for delete
    student.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_USER-1)
    student.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user"]["hard-deleted"] == 0
    assert models.User.objects.filter(id=user_id).exists()

    # Hard-delete user which is has been soft-deleted a sufficient time
    student.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_USER)
    student.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user"]["hard-deleted"] == 1
    assert not models.User.objects.filter(id=user_id).exists()


@pytest.mark.django_db
def test_hard_delete_observation(school, observation):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    observation_id = observation.id
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["observation"]["hard-deleted"] == 0
    assert models.Observation.objects.filter(id=observation_id).exists()

    # Almost, but not quite ready for delete
    observation.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION-1)
    observation.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["observation"]["hard-deleted"] == 0
    assert models.Observation.objects.filter(id=observation_id).exists()

    # Hard-delete user which is has been soft-deleted a sufficient time
    observation.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION)
    observation.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["observation"]["hard-deleted"] == 1
    assert not models.Observation.objects.filter(id=observation_id).exists()


@pytest.mark.django_db
def test_hard_delete_goal(school, personal_goal):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    goal_id = personal_goal.id
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["goal"]["hard-deleted"] == 0
    assert models.Goal.objects.filter(id=goal_id).exists()

    # Almost, but not quite ready for delete
    personal_goal.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GOAL-1)
    personal_goal.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["goal"]["hard-deleted"] == 0
    assert models.Goal.objects.filter(id=goal_id).exists()

    # Hard-delete goal which is has been soft-deleted a sufficient time
    personal_goal.deleted_at = now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GOAL)
    personal_goal.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["goal"]["hard-deleted"] == 1
    assert not models.Goal.objects.filter(id=goal_id).exists()


@pytest.mark.django_db
def test_hard_delete_user_group(school, student, student_role, valid_group):
    now = timezone.now()
    options = {
        "groups_earlier_than": now,
        "memberships_earlier_than": now,
    }
    valid_group.add_member(student, student_role)
    user_group = models.UserGroup.objects.filter(user=student, role=student_role, group=valid_group).first()
    user_group_id = user_group.id
    # Initial cleanup -> no deletes
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["hard-deleted"] == 0
    assert models.UserGroup.objects.filter(id=user_group_id).exists()

    # Almost, but not quite ready for delete
    user_group.deleted_at = now - timezone.timedelta(hours=HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP-1)
    user_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["hard-deleted"] == 0
    assert models.UserGroup.objects.filter(id=user_group_id).exists()

    # Hard-delete user_group which is has been soft-deleted a sufficient time
    user_group.deleted_at = now - timezone.timedelta(hours=HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP)
    user_group.save()
    result = update_data_integrity(school.org_number, options)
    final_chunk = list(result)[-1]
    changes = final_chunk["result"]["changes"]
    assert final_chunk["is_done"] is True
    assert changes["user_group"]["hard-deleted"] == 1
    assert not models.UserGroup.objects.filter(id=user_group_id).exists()
