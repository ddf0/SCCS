# Coding and documentation conventions

## Documentation discipline

- Every public Python module under `src/sccs/` has exactly one matching
  page under `docs/api/<module-path>.md`. Sub-modules use dotted
  notation in the filename (e.g. `docs/api/sccs.drivers.hccd.md`).
- Every public class gets an H2 section on its module's page listing its
  constructor signature, public methods, attributes, and a usage
  example.
- Firmware modules are documented under `docs/firmware/<module>.md`.
- The top-level [`INDEX.md`](INDEX.md) must list every documented
  module/class.
- **A code change that touches a public symbol is incomplete until its
  doc page is updated in the same commit.**

## Code style

- Python: `ruff check` clean. Line length 100. Imports sorted by ruff.
- C++: Arduino-flavour C++17, namespace `sccs`, no exceptions, no STL
  containers beyond `<stdint.h>` and `<math.h>`. Public functions
  declared in headers, definitions in `.cpp`.
- Identifiers and comments in English. Commit messages in English,
  Conventional Commits.
- Tests live in `tests/` (Python). Firmware tests are deferred until
  hardware bring-up.

## Git workflow

- Default branch: `main`.
- Conventional Commits: `feat`, `fix`, `docs`, `refactor`, `chore`,
  `test`, `ci`. Subject ≤ 72 chars, imperative mood, no trailing
  period.
- One logical change per commit. Doc updates ride with the code change
  that motivated them.
