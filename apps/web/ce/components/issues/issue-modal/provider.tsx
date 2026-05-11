/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useMemo, useState } from "react";
import { observer } from "mobx-react";
// taskflow imports
import type {
  ISearchIssueResponse,
  TIssue,
  TIssueTaskParameterValuePayload,
  TProjectTaskParameterValue,
} from "@taskflow/types";
// components
import { IssueModalContext } from "@/components/issues/issue-modal/context";
// hooks
import { useUser } from "@/hooks/store/user/user-user";
// services
import { IssueService } from "@/services/issue";

export type TIssueModalProviderProps = {
  templateId?: string;
  dataForPreload?: Partial<TIssue>;
  allowedProjectIds?: string[];
  children: React.ReactNode;
};

export const IssueModalProvider = observer(function IssueModalProvider(props: TIssueModalProviderProps) {
  const { children, allowedProjectIds } = props;
  // states
  const [selectedParentIssue, setSelectedParentIssue] = useState<ISearchIssueResponse | null>(null);
  const [issuePropertyValues, setIssuePropertyValues] = useState<Record<string, TProjectTaskParameterValue>>({});
  const [issuePropertyValueErrors, setIssuePropertyValueErrors] = useState<Record<string, string>>({});
  // store hooks
  const { projectsWithCreatePermissions } = useUser();
  // services
  const issueService = useMemo(() => new IssueService(), []);
  // derived values
  const projectIdsWithCreatePermissions = Object.keys(projectsWithCreatePermissions ?? {});

  const getParameterPayload = (): TIssueTaskParameterValuePayload[] =>
    Object.entries(issuePropertyValues).map(([parameterId, value]) => ({
      parameter_id: parameterId,
      value,
    }));

  return (
    <IssueModalContext.Provider
      value={{
        allowedProjectIds: allowedProjectIds ?? projectIdsWithCreatePermissions,
        workItemTemplateId: null,
        setWorkItemTemplateId: () => {},
        isApplyingTemplate: false,
        setIsApplyingTemplate: () => {},
        selectedParentIssue,
        setSelectedParentIssue,
        issuePropertyValues,
        setIssuePropertyValues,
        issuePropertyValueErrors,
        setIssuePropertyValueErrors,
        getIssueTypeIdOnProjectChange: () => null,
        getActiveAdditionalPropertiesLength: () => Object.keys(issuePropertyValues).length,
        handlePropertyValuesValidation: () => Object.keys(issuePropertyValueErrors).length === 0,
        handleCreateUpdatePropertyValues: async ({ issueId, projectId, workspaceSlug, isDraft }) => {
          if (isDraft) return;
          const payload = getParameterPayload();
          if (payload.length === 0) return;
          await issueService.updateIssueParameterValues(workspaceSlug, projectId, issueId, payload);
        },
        handleProjectEntitiesFetch: () => Promise.resolve(),
        handleTemplateChange: () => Promise.resolve(),
        handleConvert: () => Promise.resolve(),
        handleCreateSubWorkItem: () => Promise.resolve(),
      }}
    >
      {children}
    </IssueModalContext.Provider>
  );
});
