# Plan: Project Task Parameters With Administrator Management

## Goal

Add configurable task parameters at the project level. Administrators define the parameters for a project, and every task/work item in that project can store values for those parameters.

The primary management UI should live in project settings because the configuration belongs to a single project. The existing instance admin app (`apps/admin`, God Mode) can optionally expose read-only oversight or bulk maintenance later, but it should not be the only place to manage per-project task parameters.

## Current Architecture Notes

- Backend is Django/DRF in `apps/api`.
- Project data is modeled in `apps/api/taskflow/db/models/project.py`.
- Task/work item data is modeled as `Issue` in `apps/api/taskflow/db/models/issue.py`.
- Project settings already exist in the web app at `/:workspaceSlug/settings/projects/:projectId/...`.
- Project settings access is driven by `packages/constants/src/settings/project.ts` and `packages/types/src/settings.ts`.
- Project updates already require project admin or workspace admin checks in `apps/api/taskflow/app/views/project/base.py`.
- Project entity writes currently use `ProjectEntityPermission` / `allow_permission` role checks.
- CE placeholders for issue properties already exist in:
  - `apps/web/ce/hooks/use-issue-properties.tsx`
  - `apps/web/ce/hooks/use-workspace-issue-properties-extended.tsx`
  - `apps/web/ce/types/issue-types/issue-property-values.d.ts`

## Product Decisions

1. A parameter is defined per project, not globally.
2. Only project admins and workspace admins can create, edit, archive, restore, or delete parameter definitions.
3. Project members can view active parameter definitions and edit parameter values on work items if they already have permission to edit that work item.
4. Guests can only read visible parameter values when they can already read the work item.
5. Parameter definitions should be archived instead of hard deleted when values exist.
6. Parameter values should remain attached to old work items even if a parameter is archived.

## Data Model

Add a new model file, likely `apps/api/taskflow/db/models/project_parameter.py`, and export it from `apps/api/taskflow/db/models/__init__.py`.

Create `ProjectTaskParameter` using `ProjectBaseModel`:

- `name`: display name, max 255.
- `key`: stable project-local slug, max 64.
- `description`: optional text.
- `type`: enum, initial values `text`, `number`, `date`, `boolean`, `single_select`, `multi_select`, `url`.
- `options`: JSON field for select values and type-specific settings.
- `default_value`: JSON field.
- `is_required`: boolean.
- `is_active`: boolean.
- `sort_order`: float.
- `created_by`, `updated_by`, soft delete inherited from base model.
- Unique active key per project.

Create `IssueTaskParameterValue` using `ProjectBaseModel`:

- `issue`: FK to `Issue`.
- `parameter`: FK to `ProjectTaskParameter`.
- `value`: JSON field.
- Unique active value per issue and parameter.

Validation rules:

- `key` must be normalized to lowercase kebab/snake safe text.
- Select options require stable option IDs and labels.
- Required parameters are enforced on create/update only when active.
- Values must match the parameter type.
- Parameter and issue must belong to the same project and workspace.

## Backend API

Add serializers under `apps/api/taskflow/app/serializers/`:

- `ProjectTaskParameterSerializer`
- `IssueTaskParameterValueSerializer`
- A lightweight definition serializer for work item forms and lists.

Add a view set under `apps/api/taskflow/app/views/project/parameter.py`:

- `GET /api/workspaces/:slug/projects/:project_id/parameters/`
- `POST /api/workspaces/:slug/projects/:project_id/parameters/`
- `GET /api/workspaces/:slug/projects/:project_id/parameters/:pk/`
- `PATCH /api/workspaces/:slug/projects/:project_id/parameters/:pk/`
- `DELETE /api/workspaces/:slug/projects/:project_id/parameters/:pk/`

Permissions:

- `GET`: any active project member.
- `POST`, `PATCH`, `DELETE`: project admin or workspace admin.
- Reuse the existing project permission patterns instead of creating a separate role system.

Add issue value support:

- Accept `parameter_values` in `IssueCreateSerializer`.
- Return `parameter_values` in issue list/detail serializers.
- Add a dedicated endpoint if needed for partial value updates:
  - `PATCH /api/workspaces/:slug/projects/:project_id/issues/:issue_id/parameter-values/`

Activity/audit:

- Include parameter definition changes in `model_activity`.
- Include work item parameter value changes in issue activity only when values actually change.

## Frontend Web App

Project settings navigation:

- Add a new project settings tab, `parameters`, to `packages/types/src/settings.ts`.
- Add it to `PROJECT_SETTINGS` and `GROUPED_PROJECT_SETTINGS` in `packages/constants/src/settings/project.ts`.
- Add an icon mapping in `apps/web/core/components/settings/project/sidebar/item-icon.tsx`.
- Access should be `[EUserProjectRoles.ADMIN]` for the management page.

Routes:

- Add route `:workspaceSlug/settings/projects/:projectId/parameters`.
- Add page and header files under:
  - `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/parameters/page.tsx`
  - `apps/web/app/(all)/[workspaceSlug]/(settings)/settings/projects/[projectId]/parameters/header.tsx`

Services and state:

- Add a `ProjectParameterService` near `apps/web/core/services/project/`.
- Add MobX store support near `apps/web/core/store/project/` or a focused store if the state is shared across issue forms and settings.
- Add TypeScript types in `packages/types/src/project/` or `packages/types/src/issues/`.

Admin UI behavior:

- List parameters with type, required state, visibility, and sort order.
- Create/edit modal for name, type, options, default value, required flag, and description.
- Disable type changes after values exist unless a migration path is implemented.
- Archive/delete confirmation with value-count warning.
- Reorder parameters.

Work item UI:

- Show parameter inputs in create issue modal, quick add details, and issue detail sidebar.
- Render parameter columns in spreadsheet/list layouts only after display property support is added.
- Use the CE issue-property hook placeholders as the integration point.

## Optional Instance Admin App

Only add `apps/admin` support if the requirement is truly instance-level administration.

Possible God Mode scope:

- Read-only list of all project parameter definitions across workspaces.
- Instance-admin bulk archive for unsafe or duplicated definitions.
- No direct task value editing from God Mode in the first release.

If implemented, add:

- `apps/admin/app/(all)/(dashboard)/project-parameters/page.tsx`
- Sidebar entry via `apps/admin/hooks/use-sidebar-menu`.
- Backend endpoints under `/api/instances/project-parameters/` guarded by `InstanceAdminPermission`.

## Tests

Backend tests:

- Model validation for parameter types, unique keys, option shapes, and same-project constraints.
- API permission tests for admin, member, guest, workspace admin, and non-member.
- Issue create/update tests with valid and invalid `parameter_values`.
- Archive/delete behavior when values exist.

Frontend tests:

- Type checks for new shared types.
- Component tests for parameter form validation if the repo test setup supports it.
- Manual verification of project settings access for admin and non-admin users.

Commands:

- `pnpm check:types`
- `pnpm check:lint`
- Backend test target for project/issue API tests, using the existing `apps/api` pytest setup.

## Rollout Steps

1. Add backend models, migrations, serializers, views, and URL routes.
2. Add API tests for permissions and value validation.
3. Add shared TypeScript types and frontend service methods.
4. Add the project settings `Parameters` page for admins.
5. Wire parameter definitions and values into work item create/edit/detail flows.
6. Add activity logging and verify payloads.
7. Add optional spreadsheet/list rendering once core value editing is stable.
8. Add optional God Mode oversight only if instance administrators need cross-workspace control.

## Open Questions

- Should workspace admins who are not project members manage parameters? Current project update behavior allows workspace admins, so the plan follows that.
- Should parameter values be filterable/sortable in the first release? If yes, add typed value columns or indexed generated fields instead of relying only on JSON.
- Should parameters support user/member references, labels, or formulas in the first release? The first release should keep to primitive and select types.
- Should required parameters block draft work items? Recommended: enforce only when converting to a normal work item or when explicitly saving full details.
