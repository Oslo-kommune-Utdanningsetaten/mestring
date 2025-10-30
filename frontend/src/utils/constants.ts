export const TEACHER_ROLE = 'teacher'
export const STUDENT_ROLE = 'student'
export const SCHOOL_ADMIN_ROLE = 'admin'
export const SCHOOL_INSPECTOR_ROLE = 'inspector'
export const SUBJECTS_ALLOWED_ALL = 'all'
export const SUBJECTS_ALLOWED_CUSTOM = 'only-custom'
export const SUBJECTS_ALLOWED_GROUP = 'only-group'
export const NONE_FIELD_VALUE = '__none__'
export const GROUP_TYPE_BASIS = 'basis'
export const GROUP_TYPE_TEACHING = 'teaching'

// Mastery missing reasons
export const MISSING_REASON_NO_OBSERVATIONS = 'no-observations'
export const MISSING_REASON_NO_GOALS = 'no-goals'

// Maintenance task states
export const TASK_STATES: Record<string, string> = {
  pending: 'secondary',
  running: 'primary',
  finished: 'success',
  failed: 'danger',
}
