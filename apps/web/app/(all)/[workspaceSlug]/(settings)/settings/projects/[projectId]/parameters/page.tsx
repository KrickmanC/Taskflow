/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo, useState } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { Pencil, Plus, Trash2 } from "lucide-react";
// taskflow imports
import { EUserPermissions, EUserPermissionsLevel } from "@taskflow/constants";
import { useTranslation } from "@taskflow/i18n";
import { Button } from "@taskflow/propel/button";
import { setPromiseToast } from "@taskflow/propel/toast";
import type { TProjectTaskParameter, TProjectTaskParameterType } from "@taskflow/types";
import { Input, Loader, TextArea, ToggleSwitch } from "@taskflow/ui";
import { cn } from "@taskflow/utils";
// components
import { NotAuthorizedView } from "@/components/auth-screens/not-authorized-view";
import { PageHead } from "@/components/core/page-title";
import { SettingsContentWrapper } from "@/components/settings/content-wrapper";
import { SettingsHeading } from "@/components/settings/heading";
// hooks
import { useProject } from "@/hooks/store/use-project";
import { useUserPermissions } from "@/hooks/store/user";
// services
import { ProjectParameterService } from "@/services/project";
// local imports
import type { Route } from "./+types/page";
import { ParametersProjectSettingsHeader } from "./header";

type TParameterForm = {
  id?: string;
  name: string;
  key: string;
  description: string;
  type: TProjectTaskParameterType;
  optionLabels: string;
  is_required: boolean;
  value_count?: number | null;
};

const PARAMETER_TYPES: { label: string; value: TProjectTaskParameterType }[] = [
  { label: "Text", value: "text" },
  { label: "Number", value: "number" },
  { label: "Date", value: "date" },
  { label: "Boolean", value: "boolean" },
  { label: "Single select", value: "single_select" },
  { label: "Multi select", value: "multi_select" },
  { label: "URL", value: "url" },
];

const getDefaultForm = (): TParameterForm => ({
  name: "",
  key: "",
  description: "",
  type: "text",
  optionLabels: "",
  is_required: false,
});

const slugify = (value: string) =>
  value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");

const getOptionLabels = (parameter: TProjectTaskParameter) => {
  const choices = parameter.options?.choices ?? parameter.options?.options ?? [];
  return choices.map((option) => option.label).join("\n");
};

const buildPayload = (form: TParameterForm): Partial<TProjectTaskParameter> => {
  const optionLabels = form.optionLabels
    .split("\n")
    .map((label) => label.trim())
    .filter(Boolean);

  const payload: Partial<TProjectTaskParameter> = {
    name: form.name.trim(),
    key: form.key.trim(),
    description: form.description.trim(),
    type: form.type,
    is_required: form.is_required,
    options: {},
  };

  if (form.type === "single_select" || form.type === "multi_select") {
    payload.options = {
      choices: optionLabels.map((label) => ({
        id: slugify(label),
        label,
      })),
    };
  }

  return payload;
};

function ParametersSettingsPage({ params }: Route.ComponentProps) {
  const { workspaceSlug, projectId } = params;
  // translation
  const { t } = useTranslation();
  // store
  const { currentProjectDetails } = useProject();
  const { workspaceUserInfo, allowPermissions } = useUserPermissions();
  // local state
  const [form, setForm] = useState<TParameterForm | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  // services
  const parameterService = useMemo(() => new ProjectParameterService(), []);
  // derived values
  const canPerformProjectAdminActions = allowPermissions([EUserPermissions.ADMIN], EUserPermissionsLevel.PROJECT);
  const pageTitle = currentProjectDetails?.name ? `${currentProjectDetails.name} - Parameters` : undefined;
  const swrKey = workspaceSlug && projectId ? `PROJECT_PARAMETERS_${workspaceSlug}_${projectId}` : null;
  const { data: parameters, isLoading, mutate } = useSWR(swrKey, () => parameterService.list(workspaceSlug, projectId));

  const startEdit = (parameter: TProjectTaskParameter) => {
    setForm({
      id: parameter.id,
      name: parameter.name,
      key: parameter.key,
      description: parameter.description ?? "",
      type: parameter.type,
      optionLabels: getOptionLabels(parameter),
      is_required: parameter.is_required,
      value_count: parameter.value_count,
    });
  };

  const handleSubmit = async () => {
    if (!form || !form.name.trim() || !form.key.trim()) return;

    setIsSubmitting(true);
    const payload = buildPayload(form);
    const request = form.id
      ? parameterService.update(workspaceSlug, projectId, form.id, payload)
      : parameterService.create(workspaceSlug, projectId, payload);

    setPromiseToast(request, {
      loading: "Saving parameter",
      success: {
        title: "Success",
        message: () =>
          form.id ? t("project_settings.parameters.toasts.updated") : t("project_settings.parameters.toasts.created"),
      },
      error: {
        title: "Error",
        message: () => t("project_settings.parameters.toasts.error"),
      },
    });

    await request
      .then(() => {
        setForm(null);
        mutate();
      })
      .finally(() => setIsSubmitting(false));
  };

  const handleDelete = async (parameter: TProjectTaskParameter) => {
    const shouldDelete = window.confirm(`Archive parameter "${parameter.name}"?`);
    if (!shouldDelete) return;

    const request = parameterService.deleteParameter(workspaceSlug, projectId, parameter.id);
    setPromiseToast(request, {
      loading: "Archiving parameter",
      success: {
        title: "Success",
        message: () => t("project_settings.parameters.toasts.deleted"),
      },
      error: {
        title: "Error",
        message: () => t("project_settings.parameters.toasts.error"),
      },
    });
    await request.then(() => mutate());
  };

  if (workspaceUserInfo && !canPerformProjectAdminActions) {
    return <NotAuthorizedView section="settings" isProjectView className="h-auto" />;
  }

  return (
    <SettingsContentWrapper header={<ParametersProjectSettingsHeader />}>
      <PageHead title={pageTitle} />
      <div className="flex w-full flex-col gap-6">
        <SettingsHeading
          title={t("project_settings.parameters.heading")}
          description={t("project_settings.parameters.description")}
          control={
            <Button
              size="sm"
              prependIcon={<Plus />}
              onClick={() => setForm(getDefaultForm())}
              disabled={!!form || isSubmitting}
            >
              {t("project_settings.parameters.add")}
            </Button>
          }
        />

        {form && (
          <div className="flex flex-col gap-4 rounded-lg border border-subtle bg-layer-2 p-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <label className="flex flex-col gap-1.5">
                <span className="text-caption-md-medium text-secondary">
                  {t("project_settings.parameters.fields.name")}
                </span>
                <Input
                  value={form.name}
                  onChange={(event) =>
                    setForm((current) =>
                      current
                        ? {
                            ...current,
                            name: event.target.value,
                            key: current.id ? current.key : slugify(event.target.value),
                          }
                        : current
                    )
                  }
                />
              </label>
              <label className="flex flex-col gap-1.5">
                <span className="text-caption-md-medium text-secondary">
                  {t("project_settings.parameters.fields.key")}
                </span>
                <Input
                  value={form.key}
                  disabled={!!form.id}
                  onChange={(event) =>
                    setForm((current) => (current ? { ...current, key: slugify(event.target.value) } : current))
                  }
                />
              </label>
              <label className="flex flex-col gap-1.5">
                <span className="text-caption-md-medium text-secondary">
                  {t("project_settings.parameters.fields.type")}
                </span>
                <select
                  className="h-9 rounded-md border border-subtle bg-layer-2 px-3 text-13 text-primary outline-none"
                  value={form.type}
                  disabled={!!form.id && !!form.value_count}
                  onChange={(event) =>
                    setForm((current) =>
                      current ? { ...current, type: event.target.value as TProjectTaskParameterType } : current
                    )
                  }
                >
                  {PARAMETER_TYPES.map((parameterType) => (
                    <option key={parameterType.value} value={parameterType.value}>
                      {parameterType.label}
                    </option>
                  ))}
                </select>
              </label>
              <div className="flex items-center justify-between rounded-md border border-subtle px-3 py-2">
                <span className="text-caption-md-medium text-secondary">
                  {t("project_settings.parameters.fields.required")}
                </span>
                <ToggleSwitch
                  value={form.is_required}
                  onChange={() =>
                    setForm((current) => (current ? { ...current, is_required: !current.is_required } : current))
                  }
                  size="sm"
                />
              </div>
            </div>

            <label className="flex flex-col gap-1.5">
              <span className="text-caption-md-medium text-secondary">
                {t("project_settings.parameters.fields.description")}
              </span>
              <TextArea
                value={form.description}
                onChange={(event) =>
                  setForm((current) => (current ? { ...current, description: event.target.value } : current))
                }
              />
            </label>

            {(form.type === "single_select" || form.type === "multi_select") && (
              <label className="flex flex-col gap-1.5">
                <span className="text-caption-md-medium text-secondary">
                  {t("project_settings.parameters.fields.options")}
                </span>
                <TextArea
                  value={form.optionLabels}
                  placeholder="One option per line"
                  onChange={(event) =>
                    setForm((current) => (current ? { ...current, optionLabels: event.target.value } : current))
                  }
                />
              </label>
            )}

            <div className="flex justify-end gap-2">
              <Button variant="secondary" size="sm" onClick={() => setForm(null)} disabled={isSubmitting}>
                Cancel
              </Button>
              <Button size="sm" onClick={handleSubmit} disabled={isSubmitting || !form.name.trim() || !form.key.trim()}>
                {form.id ? "Update" : "Create"}
              </Button>
            </div>
          </div>
        )}

        {isLoading ? (
          <Loader className="space-y-3">
            <Loader.Item height="72px" width="100%" />
            <Loader.Item height="72px" width="100%" />
          </Loader>
        ) : parameters && parameters.length > 0 ? (
          <div className="flex flex-col gap-3">
            {parameters.map((parameter) => (
              <div
                key={parameter.id}
                className={cn(
                  "flex flex-col gap-3 rounded-lg border border-subtle bg-layer-2 px-4 py-3",
                  "md:flex-row md:items-center md:justify-between"
                )}
              >
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h4 className="truncate text-body-sm-medium text-primary">{parameter.name}</h4>
                    <span className="rounded bg-layer-3 px-1.5 py-0.5 text-caption-sm-medium text-tertiary">
                      {parameter.type.replace("_", " ")}
                    </span>
                    {parameter.is_required && (
                      <span className="rounded bg-layer-3 px-1.5 py-0.5 text-caption-sm-medium text-tertiary">
                        Required
                      </span>
                    )}
                  </div>
                  <p className="mt-1 truncate text-caption-md-regular text-tertiary">
                    {parameter.description || parameter.key}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <Button
                    variant="secondary"
                    size="sm"
                    prependIcon={<Pencil />}
                    onClick={() => startEdit(parameter)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant="error-outline"
                    size="sm"
                    prependIcon={<Trash2 />}
                    onClick={() => handleDelete(parameter)}
                  >
                    Archive
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className={cn("rounded-lg border border-dashed border-subtle px-4 py-10 text-center")}>
            <h4 className="text-body-sm-medium text-primary">{t("project_settings.parameters.empty_title")}</h4>
            <p className="mt-1 text-caption-md-regular text-tertiary">
              {t("project_settings.parameters.empty_description")}
            </p>
          </div>
        )}
      </div>
    </SettingsContentWrapper>
  );
}

export default observer(ParametersSettingsPage);
