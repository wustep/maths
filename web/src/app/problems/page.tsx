import type { Metadata } from "next";
import Link from "next/link";
import { problems } from "@/lib/problems";
import { renderInline } from "@/lib/markdown";

export const metadata: Metadata = { title: "problems · maths" };

export default async function ProblemsIndex() {
  const list = problems();
  const statuses = await Promise.all(list.map((p) => renderInline(p.status)));
  return (
    <>
      <h1 className="page-title">Problems</h1>
      <p className="page-sub">
        {list.length} problem folders. Statuses come from the README table; each page renders the
        folder&apos;s PROBLEM, ATTACK, WALKTHROUGH, and RESEARCH files.
      </p>
      <ul className="problem-list">
        {list.map((p, i) => (
          <li key={p.slug}>
            <Link href={`/problems/${p.slug}/`} className="title">
              {p.title}
            </Link>{" "}
            <span className="slug">({p.slug})</span>
            {p.status && (
              <span className="status md" dangerouslySetInnerHTML={{ __html: statuses[i] }} />
            )}
          </li>
        ))}
      </ul>
    </>
  );
}
