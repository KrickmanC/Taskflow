import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";

const root = process.cwd();
const targets = [
  [join(root, ".env.native.example"), join(root, ".env")],
  [join(root, "apps/api/.env.native.example"), join(root, "apps/api/.env")],
  [join(root, "apps/web/.env.native.example"), join(root, "apps/web/.env")],
  [join(root, "apps/admin/.env.native.example"), join(root, "apps/admin/.env")],
  [join(root, "apps/space/.env.native.example"), join(root, "apps/space/.env")],
  [join(root, "apps/live/.env.native.example"), join(root, "apps/live/.env")],
];

const force = process.argv.includes("--force");

for (const [source, target] of targets) {
  if (!existsSync(source)) {
    throw new Error(`Missing template: ${source}`);
  }

  if (existsSync(target) && !force) {
    console.log(`exists: ${target}`);
    continue;
  }

  mkdirSync(dirname(target), { recursive: true });
  copyFileSync(source, target);
  console.log(`copied: ${target}`);
}
