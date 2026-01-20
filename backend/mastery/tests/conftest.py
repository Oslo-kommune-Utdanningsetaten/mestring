import pytest
from datetime import timedelta
from django.test import Client
from django.utils import timezone
from mastery.models import School, User, Group, Role, Subject, Goal, MasterySchema, Observation, Status


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
def student_role(db):
    return Role.objects.create(name="student")


@pytest.fixture
def teacher_role(db):
    return Role.objects.create(name="teacher")


@pytest.fixture
def admin_role(db):
    return Role.objects.create(name="admin")


@pytest.fixture
def inspector_role(db):
    return Role.objects.create(name="inspector")


@pytest.fixture
def superadmin(db) -> User:
    return User.objects.create(
        name="Superadmin",
        feide_id="superadmin001@kakrafoon.kommune.no",
        email="superadmin001@kakrafoon.kommune.no",
        is_superadmin=True
    )


@pytest.fixture
def school_admin(db, school, admin_role) -> User:
    user = User.objects.create(
        name="School admin",
        feide_id="schooladmin001@kakrafoon.kommune.no",
        email="schooladmin001@kakrafoon.kommune.no",
    )
    school.set_employed_user(user, admin_role)
    return user


@pytest.fixture
def school_inspector(db, school, inspector_role) -> User:
    user = User.objects.create(
        name="School inspector",
        feide_id="schoolinspector001@kakrafoon.kommune.no",
        email="schoolinspector001@kakrafoon.kommune.no",
    )
    school.set_employed_user(user, inspector_role)
    return user


@pytest.fixture
def other_school_admin(db, other_school, admin_role) -> User:
    user = User.objects.create(
        name="Other School admin",
        feide_id="otherschooladmin001@kakrafoon.kommune.no",
        email="otherschooladmin001@kakrafoon.kommune.no",
    )
    other_school.set_employed_user(user, admin_role)
    return user


@pytest.fixture
def other_school_inspector(db, other_school, inspector_role) -> User:
    user = User.objects.create(
        name="Other School inspector",
        feide_id="otherschoolinspector001@kakrafoon.kommune.no",
        email="otherschoolinspector001@kakrafoon.kommune.no",
    )
    other_school.set_employed_user(user, inspector_role)
    return user


@pytest.fixture
def teacher(db) -> User:
    return User.objects.create(
        name="Teacher 1",
        feide_id="teacher-id@example.com",
        email="teacher@example.com"
    )


@pytest.fixture
def other_teacher(db) -> User:
    return User.objects.create(
        name="Teacher 2",
        feide_id="other-teacher-id@example.com",
        email="other-teacher@example.com"
    )


@pytest.fixture
def other_school_teacher(db) -> User:
    return User.objects.create(
        name="Teacher 3",
        feide_id="other-school-teacher-id@example.com",
        email="other-school-teacher@example.com"
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
def other_school_student(db) -> User:
    return User.objects.create(
        name="Student 3",
        feide_id="other-school-student-id@example.com",
        email="other-school-student@example.com"
    )


@pytest.fixture
def teaching_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:some-teaching-group",
        display_name="Engelsk 7a",
        type="teaching",
        school=school,
        is_enabled=True
    )


@pytest.fixture
def disabled_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:disable-teaching-group",
        display_name="Engelsk 7x",
        type="teaching",
        school=school,
        is_enabled=False
    )


@pytest.fixture
def basis_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:some-basis-group",
        display_name="Klasse 7a",
        type="basis",
        school=school,
        is_enabled=True
    )


@pytest.fixture
def teaching_group_with_members(db, teacher, student, teaching_group, teacher_role, student_role):
    teaching_group.add_member(teacher, teacher_role)
    teaching_group.add_member(student, student_role)
    return teaching_group


@pytest.fixture
def other_teaching_group(db, school):
    return Group.objects.create(
        feide_id="fc:group:other-teaching-group",
        display_name="Engelsk 8a",
        type="teaching",
        school=school,
        is_enabled=True
    )


@pytest.fixture
def other_school_teaching_group(db, other_school):
    return Group.objects.create(
        feide_id="fc:group:some-teaching-group-at-other-school",
        display_name="Engelsk 1a",
        type="teaching",
        school=other_school,
        is_enabled=True
    )


@pytest.fixture
def other_school_teaching_group_with_members(
        db, other_school_teacher, other_school_student, other_school_teaching_group, teacher_role,
        student_role):
    other_school_teaching_group.add_member(other_school_teacher, teacher_role)
    other_school_teaching_group.add_member(other_school_student, student_role)
    return other_school_teaching_group


@pytest.fixture
def other_teaching_group_with_members(
        db, other_teaching_group, other_teacher, other_student, teacher_role, student_role):
    other_teaching_group.add_member(other_teacher, teacher_role)
    other_teaching_group.add_member(other_student, student_role)
    return other_teaching_group


@pytest.fixture
def teaching_group_without_members(db, school):
    return Group.objects.create(
        feide_id="fc:group:teaching-group-no-members",
        display_name="Other Group",
        type="teaching",
        school=school,
        is_enabled=True
    )


@pytest.fixture
def subject_with_group(db, teaching_group_with_members):
    # Owned by school is None to simulate group subject
    subject = Subject.objects.create(
        display_name="Engelsk 7. årstrinn",
        short_name="Engelsk",
        grep_code="ENG0007",
        grep_group_code="ENG1Z03",
        owned_by_school=None,
    )
    teaching_group_with_members.subject = subject
    teaching_group_with_members.save()
    return subject


@pytest.fixture
def subject_owned_by_school(db, school):
    # Owned by school is set to simulate subject managed by school
    return Subject.objects.create(
        display_name="Sosiale ferdigheter",
        short_name="Sosialt",
        owned_by_school=school,
    )


@pytest.fixture
def subject_owned_by_other_school(db, other_school):
    return Subject.objects.create(
        display_name="Sosiale ferdigheter",
        short_name="Sosialt",
        owned_by_school=other_school,
    )


@pytest.fixture
def goal_with_group(db, school, teaching_group_with_members):
    return Goal.objects.create(
        title="Lese 2 bøker",
        group=teaching_group_with_members,
        school=school,
    )


@pytest.fixture
def goal_personal(db, school, student, subject_owned_by_school):
    return Goal.objects.create(
        title="Lese 2 bøker",
        student=student,
        subject=subject_owned_by_school,
        school=school,
    )


@pytest.fixture
def goal_personal_other_student(db, school, subject_owned_by_school, other_student):
    return Goal.objects.create(
        title="Lese 2 bøker",
        student=other_student,
        subject=subject_owned_by_school,
        school=school
    )


@pytest.fixture
def mastery_schema(db, school):
    return MasterySchema.objects.create(
        title="Vurderingsverb",
        description="Gjengi, forklare, se sammenhenger",
        school=school,
        config={
            "levels": [
                {
                    "text": "Gjengi",
                    "color": "rgb(229, 50, 43)",
                    "max_value": 33,
                    "min_value": 1
                },
                {
                    "text": "Forklare",
                    "color": "rgb(255, 204, 0)",
                    "max_value": 66,
                    "min_value": 34
                },
                {
                    "text": "Se sammenhenger",
                    "color": "rgb(23, 231, 21)",
                    "max_value": 100,
                    "min_value": 67
                },
            ],
            "input_increment": 1,
            "render_direction": "horizontal",
        },
    )


@pytest.fixture
def mastery_schema_other_school(db, other_school):
    return MasterySchema.objects.create(
        title="Vurderingsverb",
        description="Gjengi, forklare, se sammenhenger",
        school=other_school,
        config={
            "levels": [
                {
                    "text": "Gjengi",
                    "color": "rgb(229, 50, 43)",
                    "maxValue": 33,
                    "minValue": 1
                },
                {
                    "text": "Forklare",
                    "color": "rgb(255, 204, 0)",
                    "maxValue": 66,
                    "minValue": 34
                },
                {
                    "text": "Se sammenhenger",
                    "color": "rgb(23, 231, 21)",
                    "maxValue": 100,
                    "minValue": 67
                },
            ],
            "inputIncrement": 1,
            "renderDirection": "horizontal",
            "isColorGradientEnabled": False
        },
    )


@pytest.fixture
def observation_on_group_goal(db, student, goal_with_group):
    return Observation.objects.create(
        student=student,
        goal=goal_with_group,
        is_visible_to_student=True
    )


@pytest.fixture
def observation_on_personal_goal(db, student, goal_personal):
    return Observation.objects.create(
        student=student,
        goal=goal_personal,
        is_visible_to_student=True
    )


@pytest.fixture
def observation_on_personal_goal_other_student(db, other_student, goal_personal_other_student):
    return Observation.objects.create(
        student=other_student,
        goal=goal_personal_other_student,
        is_visible_to_student=True
    )


@pytest.fixture
def other_school_group_goal(db, other_school, other_school_teaching_group_with_members):
    return Goal.objects.create(
        title="Lese 2 bøker",
        group=other_school_teaching_group_with_members,
        school=other_school,
    )


@pytest.fixture
def other_school_personal_goal(db, other_school, other_school_student):
    return Goal.objects.create(
        title="Lese 2 bøker",
        student=other_school_student,
        school=other_school,
    )


@pytest.fixture
def groups_data(db, school):
    school_feide_id = school.feide_id
    teaching = school_feide_id.replace(":unit:", ":u:")
    basis = school_feide_id.replace(":unit:", ":b:")
    return {
        "teaching": [{
            "id": f"{teaching}:udg-fg-kropps%C3%B8ving%202e:2025-06-05:2026-06-04",
            "type": "fc:gogroup",
            "displayName": "Kroppsøving 2E",
            "notBefore": "2025-06-04T22:00:00Z",
            "notAfter": "2026-06-04T22:00:00Z",
            "go_type": "u",
            "parent": school_feide_id,
            "go_type_displayName": "undervisningsgruppe",
            "grep": {
                "displayName": "Kroppsøving 2. årstrinn",
                "code": "KRO0012"
            }
        }],
        "basis": [{
            "id": f"{basis}:udg-kl-4b:2025-06-05:2026-06-04",
            "type": "fc:gogroup",
            "displayName": "4B",
            "notBefore": "2025-06-04T22:00:00Z",
            "notAfter": "2026-06-04T22:00:00Z",
            "go_type": "b",
            "parent": school_feide_id,
            "go_type_displayName": "basisgruppe"
        }]
    }


@pytest.fixture
def status_at_school(db, school, student, subject_with_group):
    """
    Status for student at school in subject_with_group.
    Covers a past period (60-2 days ago), already visible to student since end_at has passed.
    """
    return Status.objects.create(
        student=student,
        subject=subject_with_group,
        school=school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=2),
    )


@pytest.fixture
def status_at_other_school(db, other_school, other_school_student, subject_owned_by_other_school):
    """
    Status for other_school_student at other_school.
    Covers a past period (60-2 days ago), already visible to student since end_at has passed.
    """
    return Status.objects.create(
        student=other_school_student,
        subject=subject_owned_by_other_school,
        school=other_school,
        begin_at=timezone.now() - timedelta(days=60),
        end_at=timezone.now() - timedelta(days=2),
    )
