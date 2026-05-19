# AiWhisperers

> *Cryptographic provenance for AI-generated content,
> built around a documented practice of human-AI collaboration.*

**Live:** [aiwhisperers.pl](https://aiwhisperers.pl)

AiWhisperers is an open-source ecosystem with two faces, and you are
welcome through either door.

---

## Two entrances

### → For practitioners and curious readers

If you have ever worked alongside an AI system and wondered how to
keep that work **yours** — verifiable, attributable, and grounded in
something other than vibes — start with the **map of knowing**:

**[aiwhisperers.pl →](https://aiwhisperers.pl)** *(also available
locally as [`./index.html`](./index.html))*

The map is the project's living surface. It shows the modules as
they are, the methodology as it is practiced, and the lineage of
each artifact. It is meant to be **looked at**, not just read.

If you want to understand the why before the what, read
**[REMEDY](./apps/_remedy/AiWRemedy.html)** — the relational
framework that shapes how this project works with AI systems.

### → For compliance, legal, and integration teams

If you arrived here because of **EU AI Act Article 50**, content
provenance certificates, or because your organization needs
cryptographic verification of AI-generated material:

**[Read COMPLIANCE.md →](./COMPLIANCE.md)**

That document covers Article 50 mapping, technical specifications
of provenance certificates, integration patterns, and the
commercial licensing path for proprietary deployments.

---

## What this project is, in one paragraph

AiWhisperers is a methodology and a set of cryptographic tools for
documenting work produced in collaboration between human operators
and AI systems. Each session is signed (Ed25519), each derivative
work can be traced back through a verifiable lineage chain, and
each artifact carries a cryptographic certificate of its origin.
The architecture is modular, open-source under AGPL-3.0, and built
to be self-sovereign — no central authority, no platform dependency.

---

## Status

**Live at:** [aiwhisperers.pl](https://aiwhisperers.pl)
**First public release:** [date]
**Current modules:** Pass, Verify, Quick, Schema, Boot, Postcard,
Remedy, Protocol *(plus modules in active development)*
**Active development:** yes
**Documentation:** primary in Polish, English translation in
progress
**Reviewable code:** yes — start from the map or jump directly to
[`apps/_pass/`](./apps/_pass/) for the cryptographic core

---

## Repository structure

```
/
├── index.html          ← the map (project entry point)
├── README.md           ← this file
├── COMPLIANCE.md       ← compliance and integration guide
├── LICENSE             ← AGPL-3.0 + additional terms
├── TRADEMARK.md        ← trademark policy
├── COMMERCIAL.md       ← commercial licensing
├── CONTRIBUTING.md     ← contribution policy with DCO
├── FUNDING.md          ← project sustainability
├── NOTICE              ← attribution for forks
├── PUBLICATION.md      ← first public release record
├── PRIOR_ART.md        ← public disclosure log
└── apps/
    ├── _pass/          ← cryptographic identity & certificates
    ├── _verify/        ← independent verification
    ├── _quick/         ← session closure protocol
    ├── _schema/        ← canonical schema
    ├── _boot/          ← bootstrap and orchestration
    ├── _postcard/      ← module visiting card format
    ├── _remedy/        ← relational calibration framework
    └── _protocol/      ← communication protocol specs
```

The map (`index.html`) is the project's entry point, not a module.
Modules live in `/apps/`. The map navigates them.

---

## Licensing in 30 seconds

- **Code:** AGPL-3.0 with additional attribution terms.
  See [LICENSE](./LICENSE).
- **Names** ("AiWhisperers", "AiW\*" family): trademarks.
  See [TRADEMARK.md](./TRADEMARK.md).
- **For commercial deployments** beyond AGPL terms:
  See [COMMERCIAL.md](./COMMERCIAL.md).

---

## Supporting the project

Maintained by an individual. If the project is useful to you,
consider sustaining it:

- [Sponsor on GitHub](https://github.com/sponsors/iAnoNeFactory)
- See [FUNDING.md](./FUNDING.md) for other ways

Support sustains the commons. It does not buy influence over
direction, special licenses, or trademark permissions —
deliberately. See FUNDING.md for the full clarification.

---

## Contact

**Denis Czuliński** (iAnoNeFactory)
denis.czulinski@gmail.com
[aiwhisperers.pl](https://aiwhisperers.pl)

For commercial licensing inquiries:
see [COMMERCIAL.md](./COMMERCIAL.md).

For trademark and attribution questions:
see [TRADEMARK.md](./TRADEMARK.md).

For contribution to the codebase:
see [CONTRIBUTING.md](./CONTRIBUTING.md).

---

## Lineage and prior art

This project was developed in private from [13.05.2026] and made
publicly available on [13.05.2026]. The full record
of public disclosure, including external timestamp anchors
(Software Heritage, Zenodo DOI, OpenTimestamps), is in
**[PUBLICATION.md](./PUBLICATION.md)** and **[PRIOR_ART.md](./PRIOR_ART.md)**.

---

*The two doors are intentional. Each leads to a real part of this
project. Walk through the one that calls you.*
