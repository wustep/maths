import Link from "next/link";
import path from "node:path";
import { Crumbs, fileCrumbs } from "./chrome";
import {
  formatSize,
  getProblemSlugForDir,
  githubBlobUrl,
  githubTreeUrl,
  hrefForFile,
  readRepoFile,
  type RepoDir,
  type RepoFile,
} from "@/lib/repo";
import { renderMarkdown } from "@/lib/markdown";

export function DirView({ dir }: { dir: RepoDir }) {
  const problemSlug = getProblemSlugForDir(dir.path);
  const parent = dir.path.includes("/")
    ? `/files/${path.posix.dirname(dir.path)}/`
    : dir.path === ""
      ? null
      : "/files/";
  return (
    <>
      <Crumbs items={fileCrumbs(dir.path)} />
      {problemSlug && (
        <p className="file-meta">
          This is a problem folder. Readable version:{" "}
          <Link href={`/problems/${problemSlug}/`}>problems/{problemSlug}</Link>
        </p>
      )}
      <table className="listing">
        <tbody>
          {parent && (
            <tr>
              <td className="name">
                <Link href={parent}>..</Link>
              </td>
              <td className="size" />
            </tr>
          )}
          {dir.dirs.map((d) => (
            <tr key={d.path}>
              <td className="name">
                <Link href={`/files/${d.path}/`}>{d.name}/</Link>
              </td>
              <td className="size" />
            </tr>
          ))}
          {dir.files.map((f) => {
            const href = hrefForFile(f);
            const internal = href.startsWith("/");
            return (
              <tr key={f.path}>
                <td className="name">
                  {internal ? (
                    <Link href={href}>{f.name}</Link>
                  ) : (
                    <a className="gh" href={href} title="On GitHub (too large or binary to render here)">
                      {f.name}
                    </a>
                  )}
                </td>
                <td className="size">{formatSize(f.size)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p className="file-meta" style={{ marginTop: "1rem" }}>
        <a href={githubTreeUrl(dir.path)}>This folder on GitHub</a>
      </p>
    </>
  );
}

function Meta({ file, raw }: { file: RepoFile; raw?: boolean }) {
  return (
    <p className="file-meta">
      {formatSize(file.size)} · <a href={githubBlobUrl(file.path)}>on GitHub</a>
      {raw && (
        <>
          {" "}
          · <a href={`/raw/${file.path}`}>raw</a>
        </>
      )}
    </p>
  );
}

export async function FileView({ file }: { file: RepoFile }) {
  const crumbs = <Crumbs items={fileCrumbs(file.path)} />;
  switch (file.kind) {
    case "markdown": {
      const html = await renderMarkdown(readRepoFile(file.path), file.path);
      return (
        <>
          {crumbs}
          <Meta file={file} />
          <article className="md" dangerouslySetInnerHTML={{ __html: html }} />
        </>
      );
    }
    case "text":
      return (
        <>
          {crumbs}
          <Meta file={file} />
          <pre className="filetext">{readRepoFile(file.path)}</pre>
        </>
      );
    case "pdf":
      return (
        <>
          {crumbs}
          <p className="file-meta">
            {formatSize(file.size)} · <a href={`/raw/${file.path}`}>open the PDF directly</a> ·{" "}
            <a href={githubBlobUrl(file.path)}>on GitHub</a>
          </p>
          <object
            className="frame-pdf"
            data={`/raw/${file.path}`}
            type="application/pdf"
            aria-label={file.name}
          >
            <p>
              No inline PDF viewer here. <a href={`/raw/${file.path}`}>Open {file.name}</a> instead.
            </p>
          </object>
        </>
      );
    case "html":
      return (
        <>
          {crumbs}
          <p className="file-meta">
            {formatSize(file.size)} · <a href={`/raw/${file.path}`}>open full page</a> ·{" "}
            <a href={githubBlobUrl(file.path)}>source on GitHub</a>
          </p>
          <iframe className="frame-html" src={`/raw/${file.path}`} title={file.name} />
        </>
      );
    case "image":
      return (
        <>
          {crumbs}
          <Meta file={file} raw />
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={`/raw/${file.path}`} alt={file.name} />
        </>
      );
    default:
      return (
        <>
          {crumbs}
          <p className="file-meta">
            This file is not rendered here ({formatSize(file.size)}).{" "}
            <a href={githubBlobUrl(file.path)}>View it on GitHub</a>.
          </p>
        </>
      );
  }
}
