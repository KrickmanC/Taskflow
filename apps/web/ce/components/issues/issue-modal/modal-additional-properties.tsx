/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useMemo } from "react";
import useSWR from "swr";
// taskflow imports
import type { TProjectTaskParameter, TProjectTaskParameterValue } from "@taskflow/types";
import { Input, ToggleSwitch } from "@taskflow/ui";
import { cn } from "@taskflow/utils";
// hooks
import { useIssueModal } from "@/hooks/context/use-issue-modal";
// services
import { IssueService } from "@/services/issue";
import { ProjectParameterService } from "@/services/project";

export type TWorkItemModalAdditionalPropertiesProps = {
  isDraft?: boolean;
  projectId: string | null;
  workItemId: string | undefined;
  workspaceSlug: string;
};

const getOptions = (parameter: TProjectTaskParameter) => parameter.options?.choices ?? parameter.options?.options ?? [];

const isEmptyValue = (value: TProjectTaskParameterValue) =>
  value === null || value === "" || (Array.isArray(value) && value.length === 0);

export function WorkItemModalAdditionalProperties(props: TWorkItemModalAdditionalPropertiesProps) {
  const { isDraft = false, projectId, workItemId, workspaceSlug } = props;
  // context
  const { issuePropertyValues, setIssuePropertyValues, issuePropertyValueErrors, setIssuePropertyValueErrors } =
    useIssueModal();
  // services
  const projectParameterService = useMemo(() => new ProjectParameterService(), []);
  const issueService = useMemo(() => new IssueService(), []);
  // fetch
  const parametersKey = projectId ? `WORK_ITEM_PROJECT_PARAMETERS_${workspaceSlug}_${projectId}` : null;
  const valuesKey = projectId && workItemId && !isDraft
    ? `WORK_ITEM_PARAMETER_VALUES_${workspaceSlug}_${projectId}_${workItemId}`
    : null;
  const { data: parameters } = useSWR(parametersKey, () =>
    projectParameterService.list(workspaceSlug, projectId ?? "")
  );
  const { data: values } = useSWR(valuesKey, () =>
    issueService.getIssueParameterValues(workspaceSlug, projectId ?? "", workItemId ?? "")
  );

  useEffect(() => {
    if (!parameters) return;

    const existingValues = new Map((values ?? []).map((item) => [item.parameter_id, item.value]));
    const nextValues: Record<string, TProjectTaskParameterValue> = {};
    const nextErrors: Record<string, string> = {};

    parameters.forEach((parameter) => {
      const value = existingValues.has(parameter.id)
        ? existingValues.get(parameter.id) ?? null
        : parameter.default_value === undefined
          ? null
          : parameter.default_value;

      nextValues[parameter.id] = value;
      if (parameter.is_required && isEmptyValue(value)) nextErrors[parameter.id] = "Required";
    });

    setIssuePropertyValues(nextValues);
    setIssuePropertyValueErrors(nextErrors);
  }, [parameters, values, setIssuePropertyValues, setIssuePropertyValueErrors]);

  const updateValue = (parameter: TProjectTaskParameter, value: TProjectTaskParameterValue) => {
    setIssuePropertyValues((current) => ({ ...current, [parameter.id]: value }));
    setIssuePropertyValueErrors((current) => {
      const nextErrors = { ...current };
      if (parameter.is_required && isEmptyValue(value)) {
        nextErrors[parameter.id] = "Required";
      } else {
        delete nextErrors[parameter.id];
      }
      return nextErrors;
    });
  };

  if (!parameters || parameters.length === 0 || !projectId) return null;

  return (
    <div className="border-t border-subtle px-5 pt-3">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {parameters.map((parameter) => {
          const value = issuePropertyValues[parameter.id];
          const error = issuePropertyValueErrors[parameter.id];

          return (
            <label key={parameter.id} className="flex flex-col gap-1">
              <span className="truncate text-caption-md-medium text-secondary">{parameter.name}</span>
              {parameter.type === "boolean" ? (
                <div className="flex h-8 items-center">
                  <ToggleSwitch
                    value={Boolean(value)}
                    onChange={() => updateValue(parameter, !Boolean(value))}
                    size="sm"
                  />
                </div>
              ) : parameter.type === "single_select" ? (
                <select
                  className="h-8 rounded-md border border-subtle bg-layer-2 px-2 text-13 text-primary outline-none"
                  value={typeof value === "string" ? value : ""}
                  onChange={(event) => updateValue(parameter, event.target.value || null)}
                >
                  <option value="">None</option>
                  {getOptions(parameter).map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : parameter.type === "multi_select" ? (
                <select
                  multiple
                  className={cn(
                    "min-h-16 rounded-md border border-subtle bg-layer-2 px-2 py-1",
                    "text-13 text-primary outline-none"
                  )}
                  value={Array.isArray(value) ? value : []}
                  onChange={(event) =>
                    updateValue(
                      parameter,
                      Array.from(event.target.selectedOptions).map((option) => option.value)
                    )
                  }
                >
                  {getOptions(parameter).map((option) => (
                    <option key={option.id} value={option.id}>
                      {option.label}
                    </option>
                  ))}
                </select>
              ) : (
                <Input
                  type={parameter.type === "number" ? "number" : parameter.type === "date" ? "date" : "text"}
                  value={value === null || Array.isArray(value) ? "" : String(value)}
                  onChange={(event) =>
                    updateValue(
                      parameter,
                      parameter.type === "number" && event.target.value !== ""
                        ? Number(event.target.value)
                        : event.target.value
                    )
                  }
                />
              )}
              {error && <span className="text-caption-sm-medium text-danger-secondary">{error}</span>}
            </label>
          );
        })}
      </div>
    </div>
  );
}
