/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// taskflow imports
import { API_BASE_URL } from "@taskflow/constants";
import type { TProjectTaskParameter } from "@taskflow/types";
// services
import { APIService } from "@/services/api.service";

export class ProjectParameterService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async list(workspaceSlug: string, projectId: string, includeArchived = false): Promise<TProjectTaskParameter[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/parameters/`, {
      params: includeArchived ? { all: "true" } : undefined,
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async create(
    workspaceSlug: string,
    projectId: string,
    data: Partial<TProjectTaskParameter>
  ): Promise<TProjectTaskParameter> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/parameters/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async update(
    workspaceSlug: string,
    projectId: string,
    parameterId: string,
    data: Partial<TProjectTaskParameter>
  ): Promise<TProjectTaskParameter> {
    return this.patch(`/api/workspaces/${workspaceSlug}/projects/${projectId}/parameters/${parameterId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteParameter(workspaceSlug: string, projectId: string, parameterId: string): Promise<void> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/parameters/${parameterId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
