// Copy browsable binary assets (PDFs, HTML explainers, figures) from the
// repo into public/raw/ so the static site can serve them directly.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repoRoot = path.resolve(webRoot, "..");
const outRoot = path.join(webRoot, "public", "raw");

const EXCLUDED_DIRS = new Set([
  ".git",
  "node_modules",
  "web",
  ".vercel",
  ".next",
  "out",
  "_reference",
  ".lake",
  "__pycache__",
]);
// Keep in sync with web/src/lib/repo.ts. vercel.json is not a raw asset, but
// the walk should skip the same deploy-only basenames as the file viewer.
const EXCLUDED_FILES = new Set(["vercel.json"]);
const RAW_EXT = new Set([".pdf", ".html", ".png", ".jpg", ".jpeg", ".gif", ".svg"]);

fs.rmSync(outRoot, { recursive: true, force: true });

let count = 0;
function walk(abs, rel) {
  for (const e of fs.readdirSync(abs, { withFileTypes: true })) {
    if (e.name.startsWith(".")) continue;
    const childAbs = path.join(abs, e.name);
    const childRel = rel === "" ? e.name : `${rel}/${e.name}`;
    if (e.isDirectory()) {
      if (EXCLUDED_DIRS.has(e.name)) continue;
      walk(childAbs, childRel);
    } else if (e.isFile()) {
      if (EXCLUDED_FILES.has(e.name)) continue;
      if (!RAW_EXT.has(path.extname(e.name).toLowerCase())) continue;
      const dest = path.join(outRoot, childRel);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.copyFileSync(childAbs, dest);
      count += 1;
    }
  }
}

walk(repoRoot, "");
console.log(`collect-raw: copied ${count} files into public/raw/`);
