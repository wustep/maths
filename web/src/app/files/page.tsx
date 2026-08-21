import type { Metadata } from "next";
import { repoTree } from "@/lib/repo";
import { DirView } from "@/components/file-views";

export const metadata: Metadata = { title: "files · maths" };

export default function FilesRoot() {
  return <DirView dir={repoTree()} />;
}
