// Views
import Home from '../views/Home.svelte'
import About from '../views/About.svelte'
import Student from '../views/Student.svelte'
import Group from '../views/Group.svelte'
import Groups from '../views/Groups.svelte'
import GroupsCompare from '../views/GroupsCompare.svelte'
import Students from '../views/Students.svelte'
import Status from '../views/Status.svelte'
import Profile from '../views/Profile.svelte'

// Admin views
import Users from '../views/admin/Users.svelte'
import AdminGroups from '../views/admin/Groups.svelte'
import Subjects from '../views/admin/Subjects.svelte'
import Goals from '../views/admin/Goals.svelte'
import MasterySchemas from '../views/admin/MasterySchemas.svelte'
import DataMaintenanceTask from '../views/admin/DataMaintenanceTask.svelte'
import Schools from '../views/admin/Schools.svelte'
import School from '../views/admin/School.svelte'
import SchoolStats from '../views/admin/SchoolStats.svelte'
import UsersByRole from '../views/UsersByRole.svelte'
import StatusCategory from '../views/admin/StatusCategory.svelte'

import { USER_ROLES } from './constants'

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
    path: '/users',
    component: UsersByRole,
    isPublic: false,
    accessibleBy: [USER_ROLES.INSPECTOR, USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN],
  },
  {
    path: '/groups/:groupId',
    component: Group,
    isPublic: false,
    accessibleBy: allRoles,
  },
  {
    path: '/groups-compare',
    component: GroupsCompare,
    isPublic: false,
    accessibleBy: [
      USER_ROLES.TEACHER,
      USER_ROLES.INSPECTOR,
      USER_ROLES.ADMIN,
      USER_ROLES.SUPERADMIN,
    ],
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
    component: undefined, // placeholder, as we just check for access to the admin menu
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
    path: '/admin/goals',
    component: Goals,
    isPublic: false,
    accessibleBy: [USER_ROLES.INSPECTOR, USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN],
  },
  {
    path: '/admin/users/:userId',
    component: Profile,
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
    path: '/admin/status-categories',
    component: StatusCategory,
    isPublic: false,
    accessibleBy: [USER_ROLES.ADMIN, USER_ROLES.SUPERADMIN],
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
    component: null, // placeholder, as we redirect to an external analytics dashboard,
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
