import { getDir, getFile, readRepoFile } from "./repo";

export interface Problem {
  slug: string;
  title: string;
  status: string; // raw markdown from the README table cell
  docs: ProblemDoc[]; // which of the four docs exist
}

export type ProblemDoc = "problem" | "attack" | "walkthrough" | "research";

export const DOC_FILES: Record<ProblemDoc, string> = {
  problem: "PROBLEM.md",
  attack: "ATTACK.md",
  walkthrough: "WALKTHROUGH.md",
  research: "RESEARCH.md",
};

export const DOC_LABELS: Record<ProblemDoc, string> = {
  problem: "Problem",
  attack: "Attack",
  walkthrough: "Walkthrough",
  research: "Research",
};

let cached: Problem[] | null = null;

// The README problems table is the source of truth for order and status.
export function problems(): Problem[] {
  if (cached) return cached;
  const readme = readRepoFile("README.md");
  const rows = [...readme.matchAll(/^\|\s*\[[^\]]+\]\(problems\/([^)]+)\)\s*\|\s*(.+?)\s*\|\s*$/gm)];
  const list: Problem[] = [];
  const seen = new Set<string>();
  for (const [, slug, status] of rows) {
    if (!getDir(`problems/${slug}`)) continue;
    seen.add(slug);
    list.push({ slug, title: problemTitle(slug), status, docs: docsFor(slug) });
  }
  // Folders not in the README table still get pages.
  const problemsDir = getDir("problems");
  for (const d of problemsDir?.dirs ?? []) {
    if (!seen.has(d.name)) {
      list.push({ slug: d.name, title: problemTitle(d.name), status: "", docs: docsFor(d.name) });
    }
  }
  cached = list;
  return list;
}

function docsFor(slug: string): ProblemDoc[] {
  return (Object.keys(DOC_FILES) as ProblemDoc[]).filter((d) =>
    getFile(`problems/${slug}/${DOC_FILES[d]}`),
  );
}

function problemTitle(slug: string): string {
  const f = getFile(`problems/${slug}/PROBLEM.md`);
  if (!f) return slug;
  const src = readRepoFile(f.path);
  const m = src.match(/^#\s+(.+)$/m);
  if (!m) return slug;
  // Titles are used as plain text (browser tab, index), so drop math delimiters.
  return m[1].replace(/\\[()]|\$/g, "").trim();
}

export function getProblem(slug: string): Problem | undefined {
  return problems().find((p) => p.slug === slug);
}
