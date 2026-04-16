/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// taskflow imports
import type { TFilterProperty } from "@taskflow/types";
import { EQUALITY_OPERATOR, COLLECTION_OPERATOR } from "@taskflow/types";
// local imports
import type { TCreateFilterConfig, TCreateProjectFilterParams } from "../../../rich-filters";
import { createFilterConfig, createOperatorConfigEntry, getProjectMultiSelectConfig } from "../../../rich-filters";

// ------------ Project filter ------------

/**
 * Get the project filter config
 * @template K - The filter key
 * @param key - The filter key to use
 * @returns A function that takes parameters and returns the project filter config
 */
export const getProjectFilterConfig =
  <P extends TFilterProperty>(key: P): TCreateFilterConfig<P, TCreateProjectFilterParams> =>
  (params: TCreateProjectFilterParams) =>
    createFilterConfig<P>({
      id: key,
      label: "Projects",
      ...params,
      icon: params.filterIcon,
      supportedOperatorConfigsMap: new Map([
        createOperatorConfigEntry(COLLECTION_OPERATOR.IN, params, (updatedParams) =>
          getProjectMultiSelectConfig(updatedParams, EQUALITY_OPERATOR.EXACT)
        ),
      ]),
    });
