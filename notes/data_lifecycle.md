This issue sketches up a plan for the lifecycle of our various pieces of data.

# Model infrastructure

All models have, via `Basemodel`, these fields:

- `maintained_at` - Timestamp is updated each time the Feide import job creates or updates something, e.g. `Group`, `UserGroup`, `User`.
- `marked_for_deletion_at` - A "soft delete" flag. When this is set, the row is invisible to users unless a specific parameter is sent with the request. When this timestamp is 90 (or some other number) days old, the system will remove this row from the database ("hard delete"), see deletion below.

Additionally, groups have these fields which originate from the feide_id:
E.g.: `fc:org:kakrafoon.kommune.no:b:NO987654321:3a:2025-08-01:2026-06-30`

- `valid_from` - Originates from the first date stamp (in this case 2025-08-01). If current date is less than this value, the `Group` (and thereby user_groups/memberships) is invisible to users unless a specific param is sent with the request.
- `valid_to` - Originates from the last date stamp (in this case 2026-06-30). If current date is greater than this value, the `Group` (and thereby user_groups/memberships) is invisible to users unless a specific param is sent with the request.

**Note**: `UserGroup` rows (memberships) should not be visible if the associated `Group` is outside the `valid_from` <--> `valid_to` scope.

**Note**: `Goal` rows (memberships) should not be visible if the associated `Group` is outside the `valid_from` <--> `valid_to` scope. This only removes group goals from visibility. Personal goals will still be visible. Is this correct behavior❓

# Herding data through their respective lifecycles

_Easy come, not so easy go._

## Create and update

The daily Feide import job operates on school level. It happens in five stages, each of these stages are orchestrated by a row in the `DataMaintenanceTask` table:

1. **Fetch groups**: Get all school groups from Feide and store them in a sanitized `groups.json` file, ordered by group type (teaching, basis etc).
2. **Fetch members**: Based on the content of `groups.json`, fetch members for each group. Store these in a sanitized `memberships.json` file, ordered by group -> role -> user.
3. **Import groups**: Based on the content of `groups.json`. Create, or update existing, rows in the `group` table. The `maintained_at` timestamp is set in both cases, and the `marked_for_deletion_at` field is unset.
4. **Import memberships**: Based on the content of `memberships.json`. Create, or update existing, rows in the `user` table. Then create, or update existing, rows in the `user_group` table, representing user memberships in groups. The `maintained_at` timestamp is set, and the `marked_for_deletion_at` field is unset.
5. **Schedule cleanup**: When fetch and import is done, it's time to look at what was _not_ touched during the import. The running Feide import job has a `started_at` timestamp. All `User` and `UserGroup` rows with `maintained_at` < `started_at` are implicitly unkown to Feide. If the `Group` is inside the `valid_from` <--> `valid_to` scope, the `marked_for_deletion_at` timestamp is set to now. If the `Group` is outside this scope, leave it alone (it's considered historic data).

## Automatic data removal

There are four cases where data "disappears" automatically:

1. **Group memberships change**. E.g. school cancels a teaching group, a teacher is reassigned to a group, a student moves to another group etc. This should "just work", given the above logic. Users are given new memberships, and old memberships become invisible (due to `marked_for_deletion_at`).
2. **Student or teacher quits the school**. This should also "just work", given the above logic. Users loose memberships, due to `marked_for_deletion_at` on `UserGroup` rows. **Note**: The creator of an observation or goal (observation.created_by or goal.created_by) or the target of an observation (observation.student) will keep access to that thing - is this correct❓There might not be a UI where these things can be viewed...
3. **End of school year**: Due to the `valid_from` <--> `valid_to` scope, groups and memberships should automatically become invisible, and new groups + memberships automatically created on import.
4. **Deletion**: When the `marked_for_deletion_at` timestamp is more than 90 days (or some other pre-configured number) older than the current time, a delete task irrevocably removes the row from the database ("hard delete").

## Additional maintenance

- School admins and inspectors are promoted manually (using `UserSchool`). We should probably delete these at every new school year, and manually set new ones.
- We'll need a UI where superadmin can inspect and maybe update rows with `marked_for_deletion_at`.
- Anything else❓
