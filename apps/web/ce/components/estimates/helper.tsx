/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { TEstimateSystemKeys } from "@taskflow/types";
import { EEstimateSystem } from "@taskflow/types";

export const isEstimateSystemEnabled = (key: TEstimateSystemKeys) => {
  switch (key) {
    case EEstimateSystem.POINTS:
      return true;
    case EEstimateSystem.CATEGORIES:
      return true;
    default:
      return false;
  }
};
