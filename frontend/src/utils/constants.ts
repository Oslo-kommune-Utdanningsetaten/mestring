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
export const STUDENT_PATHS = ['', 'about', 'groups', 'profile', 'statuses']
export const TEACHER_PATHS = ['', 'about', 'groups', 'profile', 'statuses', 'students']
export const RESTRICTED_PATHS = ['', 'about', 'groups', 'profile', 'statuses', 'students', 'users']

export enum CookieConsent {
  ALL = 'all',
  NECESSARY = 'only-necessary',
}

export enum UserRoles {
  STUDENT = 'student',
  TEACHER = 'teacher',
  STAFF = 'staff',
  ADMIN = 'admin',
  INSPECTOR = 'inspector',
}
