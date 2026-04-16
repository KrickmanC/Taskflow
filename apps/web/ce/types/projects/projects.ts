/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { IPartialProject, IProject } from "@taskflow/types";

export type TPartialProject = IPartialProject;

export type TProject = TPartialProject & IProject;
