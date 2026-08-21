import Link from "next/link";

export interface Crumb {
  label: string;
  href?: string;
}

export function Crumbs({ items }: { items: Crumb[] }) {
  return (
    <p className="crumbs">
      {items.map((c, i) => (
        <span key={i}>
          {i > 0 && " / "}
          {c.href ? <Link href={c.href}>{c.label}</Link> : c.label}
        </span>
      ))}
    </p>
  );
}

// Breadcrumbs for a repo path under the file browser.
export function fileCrumbs(rel: string): Crumb[] {
  const crumbs: Crumb[] = [{ label: "files", href: "/files/" }];
  if (rel === "") return crumbs;
  const segs = rel.split("/");
  segs.forEach((seg, i) => {
    const prefix = segs.slice(0, i + 1).join("/");
    crumbs.push({
      label: seg,
      href: i < segs.length - 1 ? `/files/${prefix}/` : undefined,
    });
  });
  return crumbs;
}
