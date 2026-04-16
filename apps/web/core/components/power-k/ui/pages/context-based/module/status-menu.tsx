/**
 * Copyright (c) 2023-present Taskflow Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { Command } from "cmdk";
import { observer } from "mobx-react";
// taskflow imports
import { MODULE_STATUS } from "@taskflow/constants";
import { useTranslation } from "@taskflow/i18n";
import { ModuleStatusIcon } from "@taskflow/propel/icons";
import type { TModuleStatus } from "@taskflow/types";
// local imports
import { PowerKModalCommandItem } from "../../../modal/command-item";

type Props = {
  handleSelect: (data: TModuleStatus) => void;
  value: TModuleStatus;
};

export const PowerKModuleStatusMenu = observer(function PowerKModuleStatusMenu(props: Props) {
  const { handleSelect, value } = props;
  // translation
  const { t } = useTranslation();

  return (
    <Command.Group>
      {MODULE_STATUS.map((status) => (
        <PowerKModalCommandItem
          key={status.value}
          iconNode={<ModuleStatusIcon status={status.value} className="size-3.5 shrink-0" />}
          label={t(status.i18n_label)}
          isSelected={status.value === value}
          onSelect={() => handleSelect(status.value)}
        />
      ))}
    </Command.Group>
  );
});
