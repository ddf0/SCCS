# Documentation Index

Top-level map of all classes and modules in the SCCS codebase. Update
this index whenever you add, rename, or delete a public symbol.

## Convention

- Every public Python module has a matching page under `docs/api/<module>.md`.
- Every public class has its own H2 section inside its module page.
- Firmware modules (`.h`/`.cpp` pairs) are documented under `docs/firmware/`.
- Architecture overviews live under `docs/architecture/`.

## Python — `src/sccs/`

| Module | Page | Public symbols |
| --- | --- | --- |
| `sccs` | (top-level) | `__version__` |

(Modules are added as they are implemented.)

## Firmware — `firmware/hccd/`

| File | Page |
| --- | --- |
| `hccd.ino` (entry sketch) | [`firmware/overview.md`](firmware/overview.md) |

(Modules are added as they are implemented.)

## Architecture

| Document | Topic |
| --- | --- |
| [`architecture/overview.md`](architecture/overview.md) | System architecture and dataflow |

## See also

- Repository [`README.md`](../README.md)
- Software design spec (in the parent VKR repository): `docs/superpowers/specs/2026-05-12-sccs-software-design.md`
- Implementation plan: `docs/superpowers/plans/2026-05-12-sccs-implementation.md`
