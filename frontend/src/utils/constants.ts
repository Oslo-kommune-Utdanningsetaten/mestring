// Views
import Home from '../views/Home.svelte'
import About from '../views/About.svelte'
import Student from '../views/Student.svelte'
import Group from '../views/Group.svelte'
import Groups from '../views/Groups.svelte'
import Students from '../views/Students.svelte'
import Status from '../views/Status.svelte'
import Profile from '../views/Profile.svelte'
import NotFound from '../views/NotFound.svelte'
// Admin views
import Users from '../views/admin/Users.svelte'
import AdminGroups from '../views/admin/Groups.svelte'
import Subjects from '../views/admin/Subjects.svelte'
import MasterySchemas from '../views/admin/MasterySchemas.svelte'
import DataMaintenanceTask from '../views/admin/DataMaintenanceTask.svelte'
import Schools from '../views/admin/Schools.svelte'
import School from '../views/admin/School.svelte'
import SchoolStats from '../views/admin/SchoolStats.svelte'

export const TEACHER_ROLE = 'teacher'
export const STUDENT_ROLE = 'student'
export const SCHOOL_ADMIN_ROLE = 'admin'
export const SCHOOL_INSPECTOR_ROLE = 'inspector'
export const SUBJECTS_ALLOWED_ALL = 'all'
export const SUBJECTS_ALLOWED_CUSTOM = 'only-custom'
export const SUBJECTS_ALLOWED_FEIDE = 'only-feide'
export const NONE_FIELD_VALUE = '__none__'
export const GROUP_TYPE_BASIS = 'basis'
export const GROUP_TYPE_TEACHING = 'teaching'

// Mastery missing reasons
export const MISSING_REASON_NO_OBSERVATIONS = 'no-observations'
export const MISSING_REASON_NO_GOALS = 'no-goals'

// Maintenance task states
export const TASK_STATES: Record<string, string> = {
  pending: 'secondary',
  running: 'secondary',
  finished: 'success',
  failed: 'danger',
}

export const PUBLIC_PATHS = ['', 'about']
export const STUDENT_PATHS = PUBLIC_PATHS.concat(['groups', 'profile', 'statuses'])
export const TEACHER_PATHS = PUBLIC_PATHS.concat(['groups', 'profile', 'statuses'])
export const RESTRICTED_PATHS = PUBLIC_PATHS.concat([
  'groups',
  'profile',
  'statuses',
  'students',
  'admin',
])

export enum CookieConsent {
  ALL = 'all',
  NECESSARY = 'only-necessary',
}

export enum USER_ROLES {
  STUDENT = 'student',
  TEACHER = 'teacher',
  STAFF = 'staff',
  INSPECTOR = 'inspector',
  ADMIN = 'admin',
  SUPERADMIN = 'superadmin',
}

const allRoles = [
  USER_ROLES.STUDENT,
  USER_ROLES.TEACHER,
  USER_ROLES.STAFF,
  USER_ROLES.INSPECTOR,
  USER_ROLES.ADMIN,
  USER_ROLES.SUPERADMIN,
]

// All routes in the app
export const ROUTES = [
  {
    path: '/',
    component: Home,
    isPublic: true,
  },
  {
    path: '/about',
    component: About,
    isPublic: true,
  },
  {
    path: '/groups',
    component: Groups,
    isPublic: false,
    accessibleBy: allRoles,
  },
  {
    path: '/groups/:groupId',
    component: Group,
    isPublic: false,
    accessibleBy: allRoles,
  },
  {
    path: '/profile',
    component: Profile,
    isPublic: false,
    accessibleBy: allRoles,
  },
  { path: '/statuses/:statusId', component: Status, isPublic: false, accessibleBy: allRoles },
  {
    path: '/students',
    component: Students,
    isPublic: false,
    accessibleBy: [USER_ROLES.INSPECTOR, USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN],
  },
  {
    path: '/students/:studentId',
    component: Student,
    isPublic: false,
    accessibleBy: [
      USER_ROLES.STUDENT,
      USER_ROLES.TEACHER,
      USER_ROLES.INSPECTOR,
      USER_ROLES.ADMIN,
      USER_ROLES.SUPERADMIN,
    ],
  },
  {
    path: '/admin',
    component: undefined,
    isPublic: false,
    accessibleBy: [USER_ROLES.INSPECTOR, USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/stats',
    component: SchoolStats,
    isPublic: false,
    accessibleBy: [USER_ROLES.INSPECTOR, USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/users',
    component: Users,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/groups',
    component: AdminGroups,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/subjects',
    component: Subjects,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/mastery-schemas',
    component: MasterySchemas,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/data-maintenance-tasks',
    component: DataMaintenanceTask,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/analytics',
    component: null,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/schools',
    component: Schools,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/schools/:schoolId',
    component: School,
    isPublic: false,
    accessibleBy: [USER_ROLES.SUPERADMIN],
  },
]
