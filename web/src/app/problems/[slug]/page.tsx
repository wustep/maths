import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getProblem, problems } from "@/lib/problems";
import { ProblemPage } from "@/components/problem-shell";

export function generateStaticParams() {
  return problems().map((p) => ({ slug: p.slug }));
}

export async function generateMetadata(props: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await props.params;
  const p = getProblem(slug);
  return { title: p ? `${p.title} · maths` : "maths" };
}

export default async function Page(props: { params: Promise<{ slug: string }> }) {
  const { slug } = await props.params;
  const problem = getProblem(slug);
  if (!problem || !problem.docs.includes("problem")) notFound();
  return <ProblemPage problem={problem} doc="problem" />;
}
