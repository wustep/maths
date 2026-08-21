import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { allDirs, allFiles, fileRouteCollides, getDir, getFile } from "@/lib/repo";
import { DirView, FileView } from "@/components/file-views";

export function generateStaticParams() {
  const dirs = allDirs()
    .filter((d) => d.path !== "")
    .map((d) => ({ path: d.path.split("/") }));
  const files = allFiles()
    .filter((f) => f.kind !== "external" && !fileRouteCollides(f))
    .map((f) => ({ path: f.path.split("/") }));
  return [...dirs, ...files];
}

export async function generateMetadata(props: {
  params: Promise<{ path: string[] }>;
}): Promise<Metadata> {
  const { path } = await props.params;
  return { title: `${path.join("/")} · maths` };
}

export default async function Page(props: { params: Promise<{ path: string[] }> }) {
  const { path } = await props.params;
  const rel = path.map(decodeURIComponent).join("/");
  const dir = getDir(rel);
  if (dir) return <DirView dir={dir} />;
  const file = getFile(rel);
  if (!file || file.kind === "external") notFound();
  return <FileView file={file} />;
}
