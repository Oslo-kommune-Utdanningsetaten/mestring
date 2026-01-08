import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from mastery.models import Status

thirty_days_ago = timezone.now() - timedelta(days=30)
two_days_ago = timezone.now() - timedelta(days=2)


@pytest.mark.django_db
def test_non_user_status_access(status_at_school):
    """Non-authenticated users cannot access statuses."""
    client = APIClient()

    # Non-authenticated user cannot access statuses
    resp = client.get(f"/api/status/")
    assert resp.status_code == 403
    resp = client.get(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_superadmin_status_access(superadmin, school, other_school, student,
                                  subject_with_group, status_at_school,
                                  status_at_other_school):
    """Superadmin has full access to all statuses."""
    client = APIClient()
    client.force_authenticate(user=superadmin)

    # Endpoint requires school parameter
    resp = client.get("/api/status/")
    assert resp.status_code == 400

    # Can list statuses at any school
    resp = client.get("/api/status/", {"school": school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_at_school.id

    resp = client.get("/api/status/", {"school": other_school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_at_other_school.id

    # Can retrieve statuses at any school
    resp = client.get(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 200
    resp = client.get(f"/api/status/{status_at_other_school.id}/")
    assert resp.status_code == 200

    # Can create statuses at any school
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Can update any status
    resp = client.put(f"/api/status/{created_id}/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Fortsett sånn",
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()["feedforward"] == "Fortsett sånn"

    # Can delete any status
    resp = client.delete(f"/api/status/{created_id}/")
    assert resp.status_code == 204


@pytest.mark.django_db
def test_school_inspector_status_access(
        school, other_school, school_inspector, student,
        subject_with_group, status_at_school, status_at_other_school):
    """
    School inspectors have read-only access to all statuses at their school.
    They cannot create, update, or delete any statuses.
    """
    client = APIClient()
    client.force_authenticate(user=school_inspector)

    # Endpoint requires school parameter
    resp = client.get("/api/status/")
    assert resp.status_code == 400

    # Can list statuses at their school
    resp = client.get("/api/status/", {"school": school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_at_school.id

    # Cannot list statuses at other schools (empty list due to scope filtering)
    resp = client.get("/api/status/", {"school": other_school.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Can retrieve statuses at their school
    resp = client.get(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 200

    # Cannot retrieve statuses at other schools
    resp = client.get(f"/api/status/{status_at_other_school.id}/")
    assert resp.status_code == 404

    # School inspector cannot create statuses
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # School inspector cannot update statuses
    resp = client.put(f"/api/status/{status_at_school.id}/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # School inspector cannot delete statuses
    resp = client.delete(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_school_admin_status_access(
        school, other_school, school_admin, student, other_school_student,
        subject_with_group, subject_owned_by_other_school,
        status_at_school, status_at_other_school):
    """
    School admins have full CRUD access to statuses at their school.
    They cannot access statuses at other schools.
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    # Endpoint requires school parameter
    resp = client.get("/api/status/")
    assert resp.status_code == 400

    # Can list statuses at their school
    resp = client.get("/api/status/", {"school": school.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_at_school.id

    # Cannot list statuses at other schools (empty list due to scope filtering)
    resp = client.get("/api/status/", {"school": other_school.id})
    assert resp.status_code == 200
    assert resp.json() == []

    # Can retrieve statuses at their school
    resp = client.get(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 200

    # Cannot retrieve statuses at other schools
    resp = client.get(f"/api/status/{status_at_other_school.id}/")
    assert resp.status_code == 404

    # Can create statuses at their school
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Cannot create statuses at other schools
    resp = client.post("/api/status/", {
        "student_id": other_school_student.id,
        "subject_id": subject_owned_by_other_school.id,
        "school_id": other_school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # Can update statuses at their school
    resp = client.put(f"/api/status/{created_id}/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Fortsett sånn",
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()["feedforward"] == "Fortsett sånn"

    # Cannot update statuses at other schools
    resp = client.put(f"/api/status/{status_at_other_school.id}/", {
        "student_id": other_school_student.id,
        "subject_id": subject_owned_by_other_school.id,
        "school_id": other_school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Nah",
    }, format='json')
    assert resp.status_code == 403

    # Can delete statuses at their school
    resp = client.delete(f"/api/status/{created_id}/")
    assert resp.status_code == 204

    # Cannot delete statuses at other schools
    resp = client.delete(f"/api/status/{status_at_other_school.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_teaching_group_teacher_status_access(
        school, teacher, student, other_student, student_role, teacher_role,
        teaching_group_with_members, other_teaching_group_with_members,
        subject_with_group, subject_owned_by_school, status_at_school):
    """
    Teaching group teachers can create, read, update, and delete statuses
    for students they teach in those subjects.
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Status for student in subject teacher does NOT teach
    status_untaught = Status.objects.create(
        student=student,
        subject=subject_owned_by_school,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=2),
    )

    # Status for other student (not in teacher's group)
    status_other_student = Status.objects.create(
        student=other_student,
        subject=subject_with_group,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=2),
    )

    # Can list statuses for students they teach in subjects they teach
    resp = client.get("/api/status/", {"school": school.id, "students": student.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {s["id"] for s in data}
    assert status_at_school.id in received_ids  # Student in subject they teach
    assert status_untaught.id not in received_ids  # Student not in subject they teach

    # Can retrieve status for student in subject they teach
    resp = client.get(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 200

    # Cannot retrieve status for student in subject they don't teach
    resp = client.get(f"/api/status/{status_untaught.id}/")
    assert resp.status_code == 404

    # Cannot retrieve status for other student not in their group
    resp = client.get(f"/api/status/{status_other_student.id}/")
    assert resp.status_code == 404

    # But if teacher created it, they can see it
    status_other_student.created_by = teacher
    status_other_student.save()
    resp = client.get(f"/api/status/{status_other_student.id}/")
    assert resp.status_code == 200
    # Reset for further tests
    status_other_student.created_by = None
    status_other_student.save()

    # Can create status for student they teach in subject they teach
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 201
    created_id = resp.json()["id"]

    # Cannot create status for student they teach in subject they don't teach
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_owned_by_school.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # Cannot create status for student they don't teach
    resp = client.post("/api/status/", {
        "student_id": other_student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # Can update status they have access to
    resp = client.put(f"/api/status/{created_id}/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Fortsett sånn",
    }, format='json')
    assert resp.status_code == 200
    assert resp.json()["feedforward"] == "Fortsett sånn"

    # Cannot update status for subject they don't teach
    resp = client.put(f"/api/status/{status_untaught.id}/", {
        "student_id": student.id,
        "subject_id": subject_owned_by_school.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Should not work!",
    }, format='json')
    assert resp.status_code == 403

    # Can delete status they have access to
    resp = client.delete(f"/api/status/{created_id}/")
    assert resp.status_code == 204

    # Cannot delete status for subject they don't teach
    resp = client.delete(f"/api/status/{status_untaught.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_basis_group_teacher_status_access(
        school, teacher, other_teacher, student, student_role, teacher_role,
        basis_group, other_teaching_group_with_members, subject_owned_by_school):
    """
    Basis group teachers can view all statuses for students in their basis group,
    but cannot modify statuses they don't own (unless they teach the subject).
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Add student and teacher to basis group
    basis_group.add_member(student, student_role)
    basis_group.add_member(teacher, teacher_role)

    # Add student to another teaching group (taught by other_teacher)
    other_teaching_group_with_members.add_member(student, student_role)

    # Status created by other teacher for student's subject
    status_by_other_teacher = Status.objects.create(
        student=student,
        subject=subject_owned_by_school,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=2),
        created_by=other_teacher,
    )

    # Basis teacher can view statuses for students in their basis group
    resp = client.get(f"/api/status/{status_by_other_teacher.id}/")
    assert resp.status_code == 200

    # Basis teacher cannot create status for subject they don't teach
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_owned_by_school.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher cannot update status they don't own
    resp = client.put(f"/api/status/{status_by_other_teacher.id}/", {
        "student_id": student.id,
        "subject_id": subject_owned_by_school.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Should not work!",
    }, format='json')
    assert resp.status_code == 403

    # Basis teacher cannot delete status they don't own
    resp = client.delete(f"/api/status/{status_by_other_teacher.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_student_status_access(
        school, student, other_student, subject_with_group, teaching_group_with_members):
    """
    Students can only see statuses about themselves after the end_at date (publish date).
    They cannot create, update, or delete statuses.
    """
    client = APIClient()
    client.force_authenticate(user=student)

    # Status with end_at in the past - visible to student (published)
    status_visible = Status.objects.create(
        student=student,
        subject=subject_with_group,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=1),  # Yesterday
    )

    # Status with end_at in the future - not yet visible to student
    status_not_yet_visible = Status.objects.create(
        student=student,
        subject=subject_with_group,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() + timedelta(days=2),  # Visible to students in 2 days
    )

    # Status for other student (student should NOT see regardless of end_at)
    status_other_student = Status.objects.create(
        student=other_student,
        subject=subject_with_group,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=1),  # Yesterday
    )

    # Student can list statuses where end_at has passed
    resp = client.get("/api/status/", {"school": school.id})
    assert resp.status_code == 200
    data = resp.json()
    received_ids = {s["id"] for s in data}
    assert status_visible.id in received_ids  # Published status
    assert status_not_yet_visible.id not in received_ids  # Not yet published
    assert status_other_student.id not in received_ids  # Other student's status

    # Student can retrieve status that is published (end_at in past)
    resp = client.get(f"/api/status/{status_visible.id}/")
    assert resp.status_code == 200

    # Student cannot retrieve status not yet published (end_at in future)
    resp = client.get(f"/api/status/{status_not_yet_visible.id}/")
    assert resp.status_code == 404

    # Student cannot retrieve other student's status
    resp = client.get(f"/api/status/{status_other_student.id}/")
    assert resp.status_code == 404

    # Student cannot create statuses
    resp = client.post("/api/status/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403

    # Student cannot update statuses
    resp = client.put(f"/api/status/{status_visible.id}/", {
        "student_id": student.id,
        "subject_id": subject_with_group.id,
        "school_id": school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
        "feedforward": "Should not work!",
    }, format='json')
    assert resp.status_code == 403

    ################### Delete ###################

    # Student cannot delete statuses
    resp = client.delete(f"/api/status/{status_visible.id}/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_user_can_see_own_created_statuses(
        school, teacher, student, other_student, subject_owned_by_school):
    """
    Users can see statuses they created, regardless of other access rules.
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Status created by teacher for a student they don't teach
    status_created_by_teacher = Status.objects.create(
        student=other_student,
        subject=subject_owned_by_school,
        school=school,
        begin_at=thirty_days_ago,
        end_at=two_days_ago,
        created_by=teacher,
    )

    # Teacher can see status they created even if they don't teach the student
    resp = client.get(f"/api/status/{status_created_by_teacher.id}/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_cross_school_status_isolation(
        other_school, teacher, other_school_student,
        subject_owned_by_other_school,
        status_at_school, status_at_other_school):
    """
    Teachers should not be able to access statuses at schools where they don't work.
    """
    client = APIClient()
    client.force_authenticate(user=teacher)

    # Teacher can see status at their school
    resp = client.get(f"/api/status/{status_at_school.id}/")
    assert resp.status_code == 200

    # Teacher cannot see status at other school
    resp = client.get(f"/api/status/{status_at_other_school.id}/")
    assert resp.status_code == 404

    # Teacher cannot create status at other school
    resp = client.post("/api/status/", {
        "student_id": other_school_student.id,
        "subject_id": subject_owned_by_other_school.id,
        "school_id": other_school.id,
        "begin_at": thirty_days_ago,
        "end_at": two_days_ago,
    }, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_status_filtering_by_students(
        school, school_admin, student, other_student, subject_with_group,
        status_at_school):
    """
    Test that filtering by students parameter works correctly.
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    Status.objects.create(
        student=other_student,
        subject=subject_with_group,
        school=school,
        begin_at=thirty_days_ago,
        end_at=two_days_ago,
    )

    # Filter by single student
    resp = client.get("/api/status/", {"school": school.id, "students": student.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_at_school.id

    # Filter by multiple students
    resp = client.get("/api/status/", {"school": school.id, "students": f"{student.id},{other_student.id}"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2


@pytest.mark.django_db
def test_status_filtering_by_subject(
        school, school_admin, student, subject_with_group, subject_owned_by_school,
        status_at_school):
    """
    Test that filtering by subject parameter works correctly.
    """
    client = APIClient()
    client.force_authenticate(user=school_admin)

    Status.objects.create(
        student=student,
        subject=subject_owned_by_school,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=2),
    )

    # Filter by subject
    resp = client.get("/api/status/", {"school": school.id, "subject": subject_with_group.id})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == status_at_school.id
