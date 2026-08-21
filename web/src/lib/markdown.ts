import path from "node:path";
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import remarkRehype from "remark-rehype";
import rehypeSlug from "rehype-slug";
import rehypeKatex from "rehype-katex";
import rehypeStringify from "rehype-stringify";
import { visit } from "unist-util-visit";
import { getDir, getFile, githubBlobUrl, githubTreeUrl } from "./repo";
import { DOC_FILES, type ProblemDoc } from "./problems";

// GitHub renders both $...$/$$...$$ and \(...\)/\[...\] as math. remark-math
// only knows dollars, so convert the LaTeX-style delimiters outside code
// spans and fences. The (?<!\\) guard keeps \\[2pt]-style TeX line breaks
// inside existing $$ blocks intact.
function convertMathDelimiters(src: string): string {
  const fenced = src.split(/(^(?:```|~~~)[^\n]*\n[\s\S]*?^(?:```|~~~)[^\n]*$)/m);
  return fenced
    .map((block, i) => {
      if (i % 2 === 1) return block;
      return block
        .split(/(`[^`\n]*`)/)
        .map((seg, j) => {
          if (j % 2 === 1) return seg;
          return seg
            .replace(/(?<!\\)\\\(/g, () => "$")
            .replace(/(?<!\\)\\\)/g, () => "$")
            .replace(/(?<!\\)\\\[/g, () => "$$")
            .replace(/(?<!\\)\\\]/g, () => "$$");
        })
        .join("");
    })
    .join("");
}

// Map a repo-relative target onto a site route.
function routeForRepoPath(target: string, isImage: boolean): string {
  const dir = getDir(target);
  if (dir) {
    const m = target.match(/^problems\/([^/]+)$/);
    if (m) return `/problems/${m[1]}/`;
    return `/files/${target}/`;
  }
  const file = getFile(target);
  if (file) {
    const m = target.match(/^problems\/([^/]+)\/([A-Z_]+\.md)$/);
    if (m) {
      const doc = (Object.keys(DOC_FILES) as ProblemDoc[]).find((d) => DOC_FILES[d] === m[2]);
      if (doc) return doc === "problem" ? `/problems/${m[1]}/` : `/problems/${m[1]}/${doc}/`;
    }
    if (isImage && file.kind === "image") return `/raw/${target}`;
    if (file.kind !== "external") return `/files/${target}/`;
    return githubBlobUrl(target);
  }
  // Path not in the tree (excluded or missing): GitHub still has it.
  return githubBlobUrl(target);
}

function rewriteUrl(url: string, baseDir: string, isImage: boolean): string {
  if (/^[a-z][a-z0-9+.-]*:/i.test(url) || url.startsWith("#") || url.startsWith("//")) return url;
  const [rawPath, fragment] = url.split("#");
  if (rawPath === "") return url;
  let resolved = path.posix.normalize(
    rawPath.startsWith("/") ? rawPath.slice(1) : path.posix.join(baseDir, rawPath),
  );
  resolved = resolved.replace(/\/+$/, "");
  if (resolved.startsWith("..") || resolved === ".") return githubTreeUrl("");
  const route = routeForRepoPath(resolved, isImage);
  return fragment ? `${route}#${fragment}` : route;
}

interface MdNode {
  type: string;
  url?: string;
  children?: MdNode[];
}

function remarkRewriteLinks(baseDir: string) {
  return () => (tree: MdNode) => {
    visit(tree as never, ["link", "image"], (node: MdNode) => {
      if (typeof node.url === "string") {
        node.url = rewriteUrl(node.url, baseDir, node.type === "image");
      }
    });
  };
}

function pipeline(baseDir: string) {
  return unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkMath)
    .use(remarkRewriteLinks(baseDir))
    .use(remarkRehype)
    .use(rehypeSlug)
    .use(rehypeKatex, { strict: false, throwOnError: false, errorColor: "#994444" })
    .use(rehypeStringify);
}

// Render a markdown document that lives at `repoPath` (repo-relative).
export async function renderMarkdown(src: string, repoPath: string): Promise<string> {
  const baseDir = path.posix.dirname(repoPath);
  const result = await pipeline(baseDir === "." ? "" : baseDir).process(convertMathDelimiters(src));
  return String(result);
}

// Render a fragment (e.g. a README table cell) and unwrap the outer <p>.
export async function renderInline(src: string): Promise<string> {
  const html = (await renderMarkdown(src, "README.md")).trim();
  const m = html.match(/^<p>([\s\S]*)<\/p>$/);
  return m ? m[1] : html;
}
