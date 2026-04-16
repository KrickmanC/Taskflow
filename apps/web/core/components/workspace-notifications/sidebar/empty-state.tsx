/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
// taskflow imports
import { ENotificationTab } from "@taskflow/constants";
import { useTranslation } from "@taskflow/i18n";
import { EmptyStateCompact } from "@taskflow/propel/empty-state";

type TNotificationEmptyStateProps = {
  currentNotificationTab: ENotificationTab;
};

export const NotificationEmptyState = observer(function NotificationEmptyState({
  currentNotificationTab,
}: TNotificationEmptyStateProps) {
  // taskflow imports
  const { t } = useTranslation();

  return (
    <>
      <EmptyStateCompact
        assetKey="inbox"
        assetClassName="size-24"
        title={
          currentNotificationTab === ENotificationTab.ALL
            ? t("workspace_empty_state.inbox_sidebar_all.title")
            : t("workspace_empty_state.inbox_sidebar_mentions.title")
        }
        className="max-w-56"
      />
    </>
  );
});
