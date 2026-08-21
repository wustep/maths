# Tuza's triangle packing-covering conjecture

- Slug: `tuza-triangle-packing-covering`
- List: P38
- Solver: SuperGrok CLI `grok-4.6` `--reasoning-effort xhigh`
- Status: open
- Area: Extremal graph theory
- Sources: Haxell 1999; Botler et al. 2025
- Started: 2026-08-17

## Statement

For every graph G, Tuza conjectured that the minimum number tau(G) of edges meeting all triangles satisfies tau(G) <= 2 nu(G), where nu(G) is the maximum number of edge-disjoint triangles. It is open even for split graphs in full generality.

## Tonight

A certified extremal split or bounded-treewidth example, a new local exchange rule with an independently checkable certificate, or a documented obstruction. Isolated ILP tables are an incomplete search unless they imply a reusable lemma. Fetch the current published status before searching.

## Tonight's bound

In every 8-regular graph, the two ends of an edge of triangle-codegree 7 form a Puleo reducible pair. Certificates for all 1044 unlabelled 7-vertex cores are in `compute/certs/c7_8reg_verified.json` and are independently checkable. This does not prove Tuza for $\Delta\le 8$. See `WALKTHROUGH.md`.
