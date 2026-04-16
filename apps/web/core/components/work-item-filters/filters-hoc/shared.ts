/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// taskflow imports
import type { TSaveViewOptions, TUpdateViewOptions } from "@taskflow/constants";
import type { IWorkItemFilterInstance } from "@taskflow/shared-state";
import type { EIssuesStoreType, IIssueFilters, TWorkItemFilterExpression, TWorkItemFilterProperty } from "@taskflow/types";

export type TSharedWorkItemFiltersProps = {
  entityType: EIssuesStoreType; // entity type (project, cycle, workspace, teamspace, etc)
  filtersToShowByLayout: TWorkItemFilterProperty[];
  updateFilters: (updatedFilters: TWorkItemFilterExpression) => void;
  isTemporary?: boolean;
  showOnMount?: boolean;
} & ({ isTemporary: true; entityId?: string } | { isTemporary?: false; entityId: string }); // entity id (project_id, cycle_id, workspace_id, etc)

export type TSharedWorkItemFiltersHOCProps = TSharedWorkItemFiltersProps & {
  children: React.ReactNode | ((props: { filter: IWorkItemFilterInstance | undefined }) => React.ReactNode);
  initialWorkItemFilters: IIssueFilters | undefined;
};

export type TEnableSaveViewProps = {
  enableSaveView?: boolean;
  saveViewOptions?: Omit<TSaveViewOptions<TWorkItemFilterExpression>, "onViewSave">;
};

export type TEnableUpdateViewProps = {
  enableUpdateView?: boolean;
  updateViewOptions?: Omit<TUpdateViewOptions<TWorkItemFilterExpression>, "onViewUpdate">;
};
