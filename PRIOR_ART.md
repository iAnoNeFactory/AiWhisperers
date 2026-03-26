# AiWhisperers · Prior Art Log

This document records the timeline of public disclosure of names,
concepts, and protocols within the AiWhisperers ecosystem. It is
maintained as evidence for trademark and copyright purposes.

---

## How to read this document

- **"Date"** means the date of first **public** availability of the
  named element, not the date of private development.
- **"Source"** is where the public availability can be independently
  verified (link to commit, release, external archive).
- **Entries are append-only.** If a date or claim needs to be
  corrected, the correction is logged in the "Amendments" section
  at the bottom, with the original entry left intact.
- **Order:** chronological, newest at top within each section.

---

## Initial public release · YYYY-MM-DD

See `PUBLICATION.md` for the full statement of first public release
and the complete list of names, modules, and concepts released on
this date.

### Summary of initial disclosure

**Master mark:**
- AiWhisperers

**Module names ("AiW*" family):**
- AiWBoot, AiWQuick, AiWPass, AiWVerify, AiWSchema, AiWPostcard,
  AiWRemedy, AiWProtocol

**Conceptual marks:**
- iAnoNeFactory, iFactory5.0, Operator Chain, Proof of Lineage,
  Lineage Chain, Kuźnia / Forge

### External timestamp anchors for initial release

| Anchor | Identifier | Date |
|--------|------------|------|
| GitHub first push | [commit SHA] | YYYY-MM-DD |
| GitHub Release v1.0 | v1.0 | YYYY-MM-DD |
| Software Heritage Archive | [SWHID] | YYYY-MM-DD |
| Zenodo deposit | [DOI] | YYYY-MM-DD |
| OpenTimestamps proof of `PUBLICATION.md` | [hash] | YYYY-MM-DD |

*Fill in each row as the respective service completes archival.
Software Heritage and Zenodo may take 1–7 days; GitHub and
OpenTimestamps are immediate.*

---

## Subsequent disclosures

*Append new entries here as new modules, marks, or concepts become
public. Each entry has its own date and evidence.*

### Template for new entries

```markdown
### YYYY-MM-DD · [name of new element]

**Type:** [module / mark / concept / protocol element]
**Brief description:** [one or two sentences]
**First public commit:** [commit SHA and short URL]
**First release tag (if applicable):** [tag and URL]
**Software Heritage SWHID (if applicable):** [SWHID]
**Notes:** [any relevant context — e.g. "supersedes earlier name X",
"first appears as part of module Y"]
```

---

## Naming reservations declared at initial release

The following names have been **reserved as part of the "AiW*" family
mark** at the initial release, but are NOT YET in active use in
public modules. They are reserved for future ecosystem expansion:

*(Add reserved names here as you plan modules. Examples below — keep
or remove as appropriate.)*

- [reserved name] — *for future module on [topic]*

The reservation is declared by virtue of the family mark claim in
`TRADEMARK.md`. Any future use of these names within the ecosystem
will be logged as a new entry above with its date of first public
implementation.

---

## Names explicitly NOT reserved

The following names appear in the documentation but are **not**
claimed as trademarks of this project. They may be common terms,
references to external concepts, or terms released to public domain
(see `PUBLICATION.md` section (d)):

- The nine-metric vocabulary words in their ordinary Polish meaning
  (Lustro, Klej, Zakorzeniony, Tarcie, Rezonans, Cisza, Gęstość,
  Iskra, Tryb)
- General technical terms (SHA-256, Ed25519, AGPL, etc.)
- Names of external projects referenced for compatibility (C2PA,
  IETF, EUIPO, etc.)

---

## Amendments

*If a date or claim above needs to be corrected, log the amendment
here. The original entry remains intact above.*

### Template for amendments

```markdown
### Amendment YYYY-MM-DD

**Original entry:** [quote the original statement]
**Correction:** [the corrected information]
**Reason:** [why the correction is being made]
**Evidence for correction:** [what supports the corrected version]
```

---

## Document integrity

This document is committed to the project repository and is part of
the public record. Significant updates should be:

1. Committed with descriptive commit messages
2. Tagged in releases when they accompany version bumps
3. Independently timestamped (OpenTimestamps recommended for major
   amendments)

The intent is that this document, together with the git history of
the repository and external timestamp anchors, forms a complete and
verifiable record of when each element of the AiWhisperers ecosystem
became publicly available.

---

**Maintained by:** Denis Czuliński (iAnoNeFactory)
**Contact:** denis.czulinski@gmail.com
