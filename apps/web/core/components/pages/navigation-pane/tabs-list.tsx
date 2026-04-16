/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// taskflow imports
import { useTranslation } from "@taskflow/i18n";
import { Tabs } from "@taskflow/propel/tabs";
// taskflow web components
import { ORDERED_PAGE_NAVIGATION_TABS_LIST } from "@/taskflow-web/components/pages/navigation-pane";

export function PageNavigationPaneTabsList() {
  // translation
  const { t } = useTranslation();

  return (
    <div className="mx-3.5">
      <Tabs.List>
        {ORDERED_PAGE_NAVIGATION_TABS_LIST.map((tab) => (
          <Tabs.Trigger key={tab.key} value={tab.key}>
            {t(tab.i18n_label)}
          </Tabs.Trigger>
        ))}
        <Tabs.Indicator />
      </Tabs.List>
    </div>
  );
}
