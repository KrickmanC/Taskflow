/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { addons } from "storybook/manager-api";
import { create } from "storybook/theming";

const taskflowTheme = create({
  base: "dark",
  brandTitle: "Taskflow UI",
  brandUrl: "https://taskflow.so",
  brandImage: "taskflow-lockup-light.svg",
  brandTarget: "_self",
});

addons.setConfig({
  theme: taskflowTheme,
});
