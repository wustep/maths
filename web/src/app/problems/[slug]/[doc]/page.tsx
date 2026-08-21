import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getProblem, problems, DOC_LABELS, type ProblemDoc } from "@/lib/problems";
import { ProblemPage } from "@/components/problem-shell";

export function generateStaticParams() {
  return problems().flatMap((p) =>
    p.docs.filter((d) => d !== "problem").map((doc) => ({ slug: p.slug, doc })),
  );
}

export async function generateMetadata(props: {
  params: Promise<{ slug: string; doc: string }>;
}): Promise<Metadata> {
  const { slug, doc } = await props.params;
  return { title: `${slug} ${doc} · maths` };
}

export default async function Page(props: {
  params: Promise<{ slug: string; doc: string }>;
}) {
  const { slug, doc } = await props.params;
  const problem = getProblem(slug);
  if (!problem) notFound();
  if (!(doc in DOC_LABELS) || doc === "problem") notFound();
  const typedDoc = doc as ProblemDoc;
  if (!problem.docs.includes(typedDoc)) notFound();
  return <ProblemPage problem={problem} doc={typedDoc} />;
}
