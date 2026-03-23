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

export const VALUE_INPUT_VARIANTS = [
  'sliderHorizontal',
  'sliderVertical',
  'sliderGiraffe',
  'starsHorizontal',
  'toggleHorizontal',
] as const
