/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export type TProjectTaskParameterType =
  | "text"
  | "number"
  | "date"
  | "boolean"
  | "single_select"
  | "multi_select"
  | "url";

export type TProjectTaskParameterOption = {
  id: string;
  label: string;
  sort_order?: number;
};

export type TProjectTaskParameterOptions = {
  choices?: TProjectTaskParameterOption[];
  options?: TProjectTaskParameterOption[];
};

export type TProjectTaskParameterValue = string | number | boolean | string[] | null;

export type TProjectTaskParameter = {
  id: string;
  name: string;
  key: string;
  description: string;
  type: TProjectTaskParameterType;
  options: TProjectTaskParameterOptions;
  default_value: TProjectTaskParameterValue;
  is_required: boolean;
  is_active: boolean;
  sort_order: number;
  value_count?: number | null;
  project: string;
  workspace: string;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
};

export type TIssueTaskParameterValue = {
  id: string;
  issue: string;
  parameter: string;
  parameter_id: string;
  parameter_detail?: TProjectTaskParameter;
  value: TProjectTaskParameterValue;
  project: string;
  workspace: string;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
};

export type TIssueTaskParameterValuePayload = {
  parameter_id: string;
  value: TProjectTaskParameterValue;
};
