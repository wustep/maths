import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkMath from "remark-math";
import remarkRehype from "remark-rehype";
import rehypeKatex from "rehype-katex";
import rehypeStringify from "rehype-stringify";

const require = createRequire(import.meta.url);

test("Markdown math and the stylesheet package resolve the same KaTeX", () => {
  for (const consumer of ["rehype-katex", "micromark-extension-math"]) {
    const fromConsumer = createRequire(require.resolve(consumer));
    assert.equal(fromConsumer.resolve("katex"), require.resolve("katex"), consumer);
  }
});

test("the upgraded renderer handles inline and display math and rejects unsafe links", async () => {
  const render = (source) => unified()
    .use(remarkParse)
    .use(remarkMath)
    .use(remarkRehype)
    .use(rehypeKatex, { strict: false, throwOnError: false })
    .use(rehypeStringify)
    .process(source);

  for (const expression of ["x^2 + y^2", "\\frac{1}{\\sqrt{2}}", "\\sum_{n=1}^{\\infty} n^{-2}", "\\begin{pmatrix}1&2\\\\3&4\\end{pmatrix}"]) {
    for (const displayMode of [false, true]) {
      const delimiters = displayMode ? ["$$\n", "\n$$"] : ["$", "$"];
      const html = String(await render(delimiters[0] + expression + delimiters[1]));
      assert.ok(html.includes('class="katex-mathml"'), expression);
      assert.ok(html.includes('<annotation encoding="application/x-tex">'), expression);
      assert.equal(html.includes('class="katex-display"'), displayMode, expression);
      assert.ok(!html.includes("katex-error"), expression);
    }
  }
  const unsafe = String(await render("$\\href{javascript:alert(1)}{unsafe}$"));
  assert.ok(!unsafe.includes("href=\"javascript:"));
  assert.ok(!unsafe.includes("<script"));
});
