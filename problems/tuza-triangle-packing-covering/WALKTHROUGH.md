# Walkthrough — Tuza's triangle packing-covering conjecture

## 0. What was actually missing

Tuza's conjecture is $\tau\le 2\nu$ for every graph. The published sparsity line stops at Puleo's $\mathrm{mad}<7$ (so $\Delta\le 6$) and Gupta's eleven-day-old preprint for $\Delta\le 7$. Gupta's last step is a pair reduction: in a 7-regular minimal counterexample every link is a connected non-WKE 7-vertex graph, hence every vertex is incident with an edge of triangle-codegree 4, 5 or 6, and those three local graphs are reducible. He asks whether $\mathrm{mad}<8$ is next (Question 12.1), and whether any 7-regular graph is tight (Question 12.3). Split graphs remain open except for threshold graphs and $\delta\ge 3n/5$.

A dent tonight is a new Puleo exchange with certificates, a certified new tight example outside Tuza's $K_4/K_5$-block family, or a documented obstruction to the obvious next reduction. Isolated $(\nu,\tau)$ tables are residue.

## 1. Named false starts

**Treat the 2025 DAM paper as Botler et al.** The list file says “Botler et al., On Tuza's conjecture in dense graphs”. The paper at that DOI is Chahua–Gutiérrez, *Discrete Appl. Math.* 377 (2025). Botler–Fernandes–Gutiérrez is the 2021 treewidth-6 paper. Dense split $\delta\ge 3n/5$ is Chahua–Gutiérrez, not a Botler theorem.

**Force codegree $\ge 5$ at degree 8, then copy Gupta.** The n=8 WKE census was supposed to be Gupta's Lemma 4.5 with one extra vertex. It is not. Among 443 connected non-WKE 8-vertex graphs, eight have $\Delta=4$ and two have fewer than three vertices of degree $\ge 4$ (graph6 `G?r@e[` and `G?ouUW`). An 8-regular minimal counterexample can have all incident codegrees $\le 4$. The 12-vertex local graph at a codegree-4 edge ($|A|=|B|=3$) is the size Gupta already found painful at codegree 4 in the 7-regular case.

**Mine small split graphs for a new tight example.** `geng -S` through 10 vertices produces 13,796 unlabelled split graphs. CBC finds 116 with $\tau=2\nu$, and every one of them has its triangles supported on a single $K_3$, $K_4$ or $K_5$. That is Tuza's family, restricted to the graphs that are split (one clique block plus pendant $K_2$s). No new extremal split example, and no counterexample. A table.

**Close codegree 6 in 8-regular with the same transferable template.** 156 cores: 120 template, 24 ILP, 12 failures including the empty graph and $K_6$. The empty-core “failure” is an artefact of forcing $\{ua,vb\}$ into $X$. A neighbourhood-dependent certificate exists there; a uniform one was not produced. Not claimed.

**Improve Haxell's $66/23$.** The 1999 PDF stayed behind Elsevier. Every 2026 paper still quotes $66/23$. Not attacked.

## 2. The useful failure

The n=8 census is the right lemma, just not the one we wanted. After a labelled replay of Gupta's $2^{21}$ scan (167,871 / 166,793 / 4,620, exact), the same two WKE checkers were run on all 12,346 unlabelled 8-vertex graphs. They agree.

What survives:

- every connected non-WKE 8-vertex graph has $\Delta\ge 4$ (sharp: eight graphs);
- therefore every vertex of an 8-regular minimal counterexample is incident with an edge of codegree in $\{4,5,6,7\}$;
- the n=7 statement “at least three vertices of degree $\ge 4$” is an accident of order 7.

The eight $\Delta=4$ graphs are explicit (`certs/n8_exceptions.json`). Two are 4-regular (`GEnfbW` with 6 triangles, `GEnbvG` with 7). Several others have two leaves, so a single 8-regular vertex can see a link that is almost a small clique plus pending edges and still not be WKE. Puleo's singleton reduction does not fire.

So the $\Delta=8$ project, if anyone continues it, has to reduce codegree 4 on a 12-vertex local graph. That is not tonight. What tonight can finish is the *easiest* new exchange the census still forces: codegree 7, where $A=B=\emptyset$ and the local graph is $K_2$ joined to an arbitrary 7-vertex core.

## 3. The click

At triangle-codegree 7 in an 8-regular graph the exclusive neighbourhoods vanish. The local graph $L$ on $W=\{u,v\}\cup C$, $|C|=7$, contains every triangle through $u$ or $v$. There is nothing to discard. Reducibility of $\{u,v\}$ is a finite statement about the 1,044 unlabelled graphs $H=G[C]$.

The hub-only template (Gupta §6 with $t=1$) asks for a rim set $R\subseteq E(H)$ with
$$
1+|R|+2\beta(H-R)\le 2p(R),
$$
where $p(R)$ is the maximum packing among $\{uvx:x\in C\}$ and $\{uxy,vxy:xy\in R\}$. This works for 1,002 of the 1,044 cores.

The remaining 42 include the complete core $H=K_7$. Then $L\cong K_9$. $K_9$ decomposes into the affine plane of order 3: an STS(9) with 12 triples covering every pair exactly once. Take $S$ to be those 12 triples and $X=E(K_7)\cup\{uv\}$. Then $|X|=22\le 24=2|S|$; every triangle through $u$ or $v$ is either $uvx$ (contains $uv$) or $uxy$/$vxy$ (contains a rim edge); every $S$-edge off $\{u,v\}$ is a rim edge. That is the Fano-for-$K_8$ step, one order up.

The other 41 incomplete cores get explicit $(S,X)$ from CBC, using a few triangles inside $C$. None fail.

## 4. The argument, in the order it was found

1. Fetch Haxell (paywalled, bound taken from later papers), Puleo 2015, Botler–Fernandes–Gutiérrez 2021, Bonamy et al. 2022, Chahua–Gutiérrez 2025, Gupta 2026 and its ancillary checkers.
2. Replay $(\nu,\tau)$ on $K_3,\ldots,K_8$ and the named $K_4$-block graphs. $K_8$ is 7-regular with ratio $3/2$.
3. Replay Gupta's labelled 7-vertex WKE census. Numbers agree.
4. Run the same census at n=8. Discover that codegree $\ge 5$ cannot be forced, and that “three vertices of degree $\ge 4$” already fails.
5. Enumerate 7-regular graphs on 8, 10 and 12 vertices. No tight example. Max ratios $3/2$, $6/5$, $4/3$.
6. Enumerate split graphs through 10 vertices. 116 tight, all Tuza-classical.
7. Search Puleo certificates for every 7-vertex core at an 8-regular codegree-7 edge. 1,002 templates, 42 ILP, 0 failures.
8. Independently rebuild every template $(S,X)$ from the stored rim set and re-check all 1,044 triples by edge incidence. Pass.
9. Recognise the $K_7$ certificate as STS(9).
10. Attempt codegree 6. Stop at 12 unresolved transferable cores. Do not claim it.

The transfer from $L$ to $G$ is Gupta's local-reducibility criterion with empty exclusive neighbourhoods. Every triangle of $G$ through $u$ or $v$ has its third vertex in $C$ and its three edges in $L$. A Puleo witness in $L$ is a Puleo witness in $G$.

The $K_7$ witness, written out. Vertices $C=\{0,1,2,3,4,5,6\}$, hubs $u=7$, $v=8$.

```
S = {578, 467, 017, 038, 148, 237, 268,
     024, 056, 125, 136, 345}
X = all 21 edges of C, plus uv.
```

Every pair among the nine vertices lies in exactly one member of $S$. Certificate key `F~~~w` in `certs/c7_8reg_verified.json`.

## 5. Computer residue

- Labelled WKE n=7: `certs/wke_labelled_n7.json`. Replay of Gupta, not a dent.
- Unlabelled WKE n=5..8: `certs/wke_unlabelled.json`. n=8 is new.
- n=8 $\Delta=4$ list, two WKE checkers: `certs/n8_exceptions.json`.
- Codegree-7 search log and verified certificates: `certs/reduce_c7_8reg.json`, `certs/c7_8reg_verified.json` (1,044 triples).
- Codegree-6 remainder: `certs/reduce_c6_8reg.json` (12 fails).
- Split n≤10: `certs/split_census.json` (13,796 graphs, 116 tight, 0 new, 0 counterexamples).
- 7-regular n≤12: `certs/regular7_census.json` (1,553 graphs, 0 tight). n=12 maximiser `KQyurj]yrzUy` recomputed $(\nu,\tau)=(12,16)$.

Replay: `compute/run_all.sh`.

## 6. What is proved vs still open

**Proved tonight.** If $G$ is 8-regular and $c(uv)=7$, then $\{u,v\}$ is reducible in Puleo's sense. Independently checkable. Also: every connected non-WKE 8-vertex graph has $\Delta\ge 4$; Gupta's 7-vertex counts are correct; no 7-regular graph on $n\le 12$ has $\tau=2\nu$; no split graph on $n\le 10$ is a nonclassical tight example.

**Still open.** The conjecture. Split graphs. Treewidth 7. $\mathrm{mad}<8$ and $\Delta\le 8$. Whether any 7-regular graph on $n\ge 14$ is tight. A human proof of Gupta's 1,144 codegree-4 catalogue. Haxell's constant $66/23$.

We did not beat Haxell's universal bound. We did not prove Tuza for any new infinite class. We produced one new local exchange that any later $\Delta=8$ argument can call, and a census that says the rest of that argument cannot skip codegree 4.
