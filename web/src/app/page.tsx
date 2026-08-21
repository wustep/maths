import { readRepoFile } from "@/lib/repo";
import { renderMarkdown } from "@/lib/markdown";

export default async function Home() {
  const html = await renderMarkdown(readRepoFile("README.md"), "README.md");
  return <article className="md" dangerouslySetInnerHTML={{ __html: html }} />;
}
