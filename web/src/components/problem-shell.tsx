import Link from "next/link";
import { Crumbs } from "./chrome";
import { DOC_FILES, DOC_LABELS, type Problem, type ProblemDoc } from "@/lib/problems";
import { getDir, githubBlobUrl } from "@/lib/repo";
import { renderMarkdown } from "@/lib/markdown";
import { readRepoFile } from "@/lib/repo";

export async function ProblemPage({ problem, doc }: { problem: Problem; doc: ProblemDoc }) {
  const repoPath = `problems/${problem.slug}/${DOC_FILES[doc]}`;
  const html = await renderMarkdown(readRepoFile(repoPath), repoPath);

  const dir = getDir(`problems/${problem.slug}`);
  const docNames = new Set(Object.values(DOC_FILES));
  const extras = [
    ...(dir?.dirs ?? []).map((d) => ({ label: `${d.name}/`, href: `/files/${d.path}/` })),
    ...(dir?.files ?? [])
      .filter((f) => !docNames.has(f.name))
      .map((f) => ({
        label: f.name,
        href: f.kind === "external" ? githubBlobUrl(f.path) : `/files/${f.path}/`,
      })),
  ];

  return (
    <>
      <Crumbs
        items={[{ label: "problems", href: "/problems/" }, { label: problem.slug }]}
      />
      <nav className="doc-tabs">
        {problem.docs.map((d) => (
          <Link
            key={d}
            className={d === doc ? "active" : undefined}
            href={d === "problem" ? `/problems/${problem.slug}/` : `/problems/${problem.slug}/${d}/`}
          >
            {DOC_LABELS[d]}
          </Link>
        ))}
        <Link href={`/files/problems/${problem.slug}/`}>Files</Link>
      </nav>
      {extras.length > 0 && (
        <p className="folder-line">
          Also in this folder:{" "}
          {extras.map((e, i) => (
            <span key={e.label}>
              {i > 0 && " · "}
              <a href={e.href}>{e.label}</a>
            </span>
          ))}
        </p>
      )}
      <article className="md" dangerouslySetInnerHTML={{ __html: html }} />
    </>
  );
}
