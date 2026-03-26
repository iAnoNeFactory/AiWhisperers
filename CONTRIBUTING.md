# Contributing to AiWhisperers

Thank you for considering a contribution to AiWhisperers. This
document explains the practical and legal terms of contributing.

---

## Spirit of contribution

AiWhisperers is a project about **relational quality in human-AI
work**. Contributions are welcome from anyone who shares that
orientation — whether you are an operator with a session insight, a
developer fixing a bug, a researcher proposing an extension to the
methodology, or a translator opening up the project to a new
language.

The project moves slowly and deliberately. A contribution that
resonates with the methodology is more valuable than a contribution
that simply adds features.

---

## How to contribute

### Bug reports and small fixes

Open an issue on https://github.com/iAnoNeFactory/AiWhisperers/issues describing the
bug, the expected behavior, and the actual behavior. For small fixes
(typos, broken links, minor refactors), a pull request without prior
discussion is fine.

### Substantive changes

For anything that touches the canonical Schema, the session-closing
protocol, the lineage chain format, or the trademark-protected
naming: **open an issue first** describing what you want to change
and why. This avoids you investing time in a PR that doesn't fit
the project's direction.

### New modules or major features

These are best discussed via email (denis.czulinski@gmail.com)
before implementation, especially if you anticipate the change
becoming part of the Core Protocol.

**Note on naming:** any new module proposed for inclusion in the
upstream AiWhisperers repository should follow the "AiW*" naming
convention (e.g., "AiWBridge", "AiWFlow"). New modules in
third-party forks must NOT use the "AiW*" prefix — see
`TRADEMARK.md`.

### Translations

Translation contributions are very welcome. Please follow existing
language file structure (see `apps/*/lang/`). The default language
of the project's internal documentation is Polish; user-facing
strings and external documentation are being progressively
translated to English.

---

## Developer Certificate of Origin (DCO)

To contribute code, documentation, or other content to AiWhisperers,
you must certify the Developer Certificate of Origin version 1.1
(below) for each contribution. This is done by adding a
`Signed-off-by` line to your commit messages.

In git, this is done automatically with the `-s` flag:

```
git commit -s -m "Your commit message"
```

This produces a commit message ending with:

```
Signed-off-by: Your Name <your.email@example.com>
```

**Important:** the name and email must be your real name and a real
email address. Pseudonymous contributions are accepted as long as
the pseudonym is consistent and reachable; anonymous contributions
are not.

### DCO v1.1 — full text

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.


Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

---

## Why DCO instead of a Contributor License Agreement (CLA)?

A CLA would require you to sign a separate legal document assigning
or licensing your contribution. DCO is lighter: it is a per-commit
certification that you have the right to contribute the code under
the project's license. Most large FOSS projects (Linux kernel,
Docker, Kubernetes, etc.) use DCO for this reason.

**Important practical implication for dual-licensing:** because
AiWhisperers offers commercial licenses (see `COMMERCIAL.md`) for
deployments that don't fit AGPL, contributions are accepted under
the following terms:

1. Your contribution is licensed under AGPL-3.0 (the project's
   default license).

2. By submitting a contribution, you grant the project maintainer
   (Denis Czuliński) a **perpetual, worldwide, non-exclusive,
   royalty-free, sublicensable license** to re-license your
   contribution under alternative terms for commercial-licensing
   purposes.

3. You retain copyright in your contribution. Point (2) is a
   license, not an assignment.

This dual-licensing grant is **necessary** for the project's
sustainability model to work. Without it, the project could not
offer commercial licenses for contributions made by others.

If you cannot agree to point (2) for a specific contribution,
please mention this in the PR description. We can discuss whether
the contribution fits under a different arrangement (e.g., an
external plugin that interfaces with the project but is not merged
into the main codebase).

---

## Code style and conventions

For now, the project does not have a formal style guide. Match the
style of surrounding code. The boot documents (`*-boot.md`)
describe the architectural conventions; consult them before making
structural changes.

---

## Lineage and attribution

If your contribution introduces a new module, new protocol element,
or other substantive new structure:

- Add a CHANGELOG entry to the relevant boot document
- Add yourself to a `CONTRIBUTORS.md` file (create one if it
  doesn't exist yet)
- For substantial contributions: consider whether your work should
  be acknowledged in the lineage chain of subsequent sessions

This is part of the **proof of lineage** principle of the project —
who contributed what, when, is visible and verifiable.

---

## Code of conduct

The project's code of conduct is implicit in `_remedy-boot.md`:
relational quality, calibrated friction, presence over performance,
silence when nothing useful can be added.

Disrespectful, harassing, or hostile communication is not welcome
and will result in contribution permissions being revoked.

---

## Questions

For questions about contributing that aren't answered here:
**denis.czulinski@gmail.com**
