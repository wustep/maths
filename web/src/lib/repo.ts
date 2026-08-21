import fs from "node:fs";
import path from "node:path";

// The app lives in web/; the maths content is the repo root above it.
export const REPO_ROOT = path.resolve(process.cwd(), "..");
export const GITHUB_REPO = "https://github.com/wustep/maths";
export const GITHUB_BRANCH = "main";

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

// Files rendered as readable pages.
const MARKDOWN_EXT = new Set([".md"]);
const TEXT_EXT = new Set([
  ".txt",
  ".py",
  ".c",
  ".h",
  ".sh",
  ".rs",
  ".lean",
  ".tex",
  ".toml",
  ".yaml",
  ".yml",
  ".json",
  ".jsonl",
  ".csv",
  ".tsv",
  ".log",
]);
const TEXT_NAMES = new Set(["Makefile", "LICENSE", "lean-toolchain"]);
const PDF_EXT = new Set([".pdf"]);
const HTML_EXT = new Set([".html"]);
const IMAGE_EXT = new Set([".png", ".jpg", ".jpeg", ".gif", ".svg"]);

// Above this size a text file gets a GitHub link instead of an inline page.
export const TEXT_SIZE_CAP = 200 * 1024;

export type FileKind = "markdown" | "text" | "pdf" | "html" | "image" | "external";

export interface RepoFile {
  path: string; // repo-relative, posix
  name: string;
  size: number;
  kind: FileKind;
}

export interface RepoDir {
  path: string; // repo-relative, posix; "" for root
  name: string;
  dirs: RepoDir[];
  files: RepoFile[];
}

export function classify(name: string, size: number): FileKind {
  const ext = path.posix.extname(name).toLowerCase();
  if (MARKDOWN_EXT.has(ext)) return size <= TEXT_SIZE_CAP ? "markdown" : "external";
  if (PDF_EXT.has(ext)) return "pdf";
  if (HTML_EXT.has(ext)) return "html";
  if (IMAGE_EXT.has(ext)) return "image";
  if (TEXT_EXT.has(ext) || TEXT_NAMES.has(name))
    return size <= TEXT_SIZE_CAP ? "text" : "external";
  // Everything else: SAT dumps, compiled binaries, archives, data blobs.
  return "external";
}

function scanDir(abs: string, rel: string): RepoDir {
  const entries = fs.readdirSync(abs, { withFileTypes: true });
  const dirs: RepoDir[] = [];
  const files: RepoFile[] = [];
  for (const e of entries) {
    if (e.name.startsWith(".")) continue;
    const childRel = rel === "" ? e.name : `${rel}/${e.name}`;
    if (e.isDirectory()) {
      if (EXCLUDED_DIRS.has(e.name)) continue;
      dirs.push(scanDir(path.join(abs, e.name), childRel));
    } else if (e.isFile()) {
      const size = fs.statSync(path.join(abs, e.name)).size;
      files.push({
        path: childRel,
        name: e.name,
        size,
        kind: classify(e.name, size),
      });
    }
  }
  dirs.sort((a, b) => a.name.localeCompare(b.name));
  files.sort((a, b) => a.name.localeCompare(b.name));
  return { path: rel, name: rel === "" ? "" : path.posix.basename(rel), dirs, files };
}

let cachedTree: RepoDir | null = null;

export function repoTree(): RepoDir {
  if (!cachedTree) cachedTree = scanDir(REPO_ROOT, "");
  return cachedTree;
}

let cachedIndex: { dirs: Map<string, RepoDir>; files: Map<string, RepoFile> } | null = null;

function index() {
  if (!cachedIndex) {
    const dirs = new Map<string, RepoDir>();
    const files = new Map<string, RepoFile>();
    const walk = (d: RepoDir) => {
      dirs.set(d.path, d);
      for (const f of d.files) files.set(f.path, f);
      for (const c of d.dirs) walk(c);
    };
    walk(repoTree());
    cachedIndex = { dirs, files };
  }
  return cachedIndex;
}

export function getDir(rel: string): RepoDir | undefined {
  return index().dirs.get(rel);
}

export function getFile(rel: string): RepoFile | undefined {
  return index().files.get(rel);
}

export function allDirs(): RepoDir[] {
  return [...index().dirs.values()];
}

export function allFiles(): RepoFile[] {
  return [...index().files.values()];
}

// "problems/<slug>" directories have a rendered problem page too.
export function getProblemSlugForDir(rel: string): string | null {
  const m = rel.match(/^problems\/([^/]+)$/);
  return m ? m[1] : null;
}

export function readRepoFile(rel: string): string {
  return fs.readFileSync(path.join(REPO_ROOT, rel), "utf8");
}

export function githubBlobUrl(rel: string): string {
  return `${GITHUB_REPO}/blob/${GITHUB_BRANCH}/${rel}`;
}

export function githubTreeUrl(rel: string): string {
  return rel === "" ? GITHUB_REPO : `${GITHUB_REPO}/tree/${GITHUB_BRANCH}/${rel}`;
}

export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(bytes < 10240 ? 1 : 0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
