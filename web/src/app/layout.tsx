import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "katex/dist/katex.min.css";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], display: "swap" });

export const metadata: Metadata = {
  title: "maths",
  description: "Notebook for a few open problems.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.className}>
      <body>
        <header className="site-header">
          <nav>
            <Link href="/" className="wordmark">
              maths
            </Link>
            <div className="nav-links">
              <Link href="/problems/">problems</Link>
              <Link href="/files/notes/">notes</Link>
              <Link href="/files/">files</Link>
              <a href="https://github.com/wustep/maths">github</a>
            </div>
          </nav>
        </header>
        <main>{children}</main>
        <footer className="site-footer">
          <a href="https://github.com/wustep/maths">wustep/maths</a>, rendered from the repo
          markdown.
        </footer>
      </body>
    </html>
  );
}
