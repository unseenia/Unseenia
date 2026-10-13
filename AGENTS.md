# Unseenia™ — Agent Instructions

## Kanban board

This project belongs to the **Unseenia** organization; its Kanban board slug is `unseenia` (see `~/Unseenia/AGENTS.md`). Always target `unseenia` explicitly (`--board unseenia` / `board="unseenia"`). Never rely on the current-board pointer. If a task's assigned board differs, report the mismatch before acting — do not silently switch.

## Project

C++17 console application built with **MSBuild / Visual Studio** (VC++ v142). Windows-only.
No package manager, no CI, no test framework.

**Entry point:** `_Seams/main.cpp` → `kabuki::press::Client(args, arg_count).Run()`

## Build

Open `__unseenia.vcxproj` in Visual Studio or:

```
msbuild __unseenia.vcxproj /p:Configuration=Debug|x64
msbuild __unseenia.vcxproj /p:Configuration=Release|x64
```

Output lands in `Debug/` or `Release/` under the solution root.

## Dependencies

This repo is a cookbook application under the [Kabuki Toolkit](https://github.com/KabukiStarship) ecosystem.
`_Seams/main.cpp` includes `../kabuki.press/client.inl` — the Kabuki framework lives in a **sibling directory** (`../kabuki.press/`). The project's include path in the vcxproj adds the parent directory (`$(ProjectDir).\..\..\`).

## Architecture

- `_Seams/*.inl` — software seams and framework bootstrap. Each `.inl` includes a sibling from `../../script2/` (e.g. `_release.inl` → `../../script2/_release.inl`). These are scaffolding stubs from the AStartup Cookbook template.
- `GDD/` — game design document. The authoritative source for game mechanics, story, levels, and technical specs.
- `Docs/` — operational notes (training plan, etc.).
- `resources/` — game assets (images, models, etc.).
- `Models/` — ML training scripts (`Models/v1/DiffTrans.py`).
- `Curator/` — Flask app for rating AI-generated assets (see `Curator/app.py`).
- `Debug/`, `x64/`, `.vs/` — build artifacts and IDE cache. Git-ignored; never commit them.

## Workflow

1. Read `GDD/Overview/game_concept.md` and `GDD/Overview/game_flow_summary.md` to understand the game before writing code.
2. The game is a **retro voxel-based title** where players create worlds from physical graph paper + toys. Menus use pixel art; the game world is 3D voxel models.
3. All source code goes under `_Seams/`. The Kabuki framework provides the engine infrastructure.
4. There are no automated tests or linters. Verify builds manually in Visual Studio.

## Gotchas

- **Precompiled headers** are enabled (`pch.h`). New `.cpp` files must include the pch first.
- **Include paths** in the vcxproj reference `$(ProjectDir).\..\..\` — Kabuki library headers live in sibling repos.
- **Duplicate files** exist in `GDD/` (e.g. `target_hardware.md` and `TargetHardware.md`). The lowercase versions are the active ones (Git-tracked); uppercase are VS-generated duplicates.
- Most GDD sections are largely empty templates — the game is in early design.

## Code Style — Chimera+ (AStarship Standard)

All **code and filenames** in the AStarship ecosystem follow the **Chimera+** style guide
(`~/AStarStarship/ASCIICrabs/__ChimeraPlus.md`). The naming philosophy applies to code
identifiers and filenames fleet-wide.

### Core Rule: immutable vs mutable
- **Immutable** (can't change after init) → **CamelCase**
- **Mutable** (changes at runtime) → **lower_snake_case**

### Naming Summary
| Element | Convention | Example |
|---|---|---|
| Type aliases (fixed-width) | 3-letter CAPS codes | `CHA` char8, `ISC` int32, `IUD` uint64, `BOL` bool, `FPC` float32, `FPD` double64 |
| Structs / classes | CamelCase + T(POD)/A(utoject) prefix | `TArray`, `AMap`, `Crabs` |
| Struct members (mutable) | lower_snake_case | `socket_bytes`, `header_bytes` |
| Struct members (immutable) | CamelCase | `StackTotalMin`, `ColumnWidth` |
| Free functions / methods | CamelCase, type-prefixed | `CrabsInit`, `TArrayBytes`, `TMapFind` |
| Function suffixes | `_NC` (no-check), `C` (const/count), `T` (POD), `A` (autoject) | `TArrayInsert_NC`, `CSizeMin` |
| Local variables | lower_snake_case (always) | `bytes_data`, `read_cursor` |
| Macros / #define | UPPER_SNAKE_CASE | `CRABS_RUN_TESTS`, `CPU_X64` |
| Private/protected members | trailing underscore | `aobj_`, `array_` |
| Namespaces | `namespace _ { ... }` | single shared underscore namespace |
| DB names / tables / columns | lower_snake_case (mutable) | `user_sessions`, `order_items` |
| Client-facing API / headers | CamelCase (immutable contract) | `OrderService`, `PaymentGateway` |
| Filenames (client contract) | CamelCase | `OrderService.h` |
| Filenames (host/storage) | lower_snake_case | `user_sessions.py` |

### Header Boilerplate (C/C++)
```
// Copyright AStarship <https://astarship.net>.
#pragma once
#ifndef CRABS_<NAME>_<H|HPP>
#define CRABS_<NAME>_<H|HPP>
#include "..."
#if SEAM >= CRABS_<NAME>
... body ...
#endif
#endif
```

### Formatting
- 2-space indent
- Opening brace same line (functions/control), next line (structs/classes)
- `D_ASSERT()`, `D_COUT()`, `D_RETURNT(type, val)` for debug/assert/return
- `NILP` = nullptr
- `alignas(ACPUCacheLineSize)` for hot structs
- Doxygen `/** @param @return @pre @link @see @code */` comments

### The One-Sentence Version
**Immutable → CamelCase, mutable → lower_snake_case; macros UPPER_SNAKE; private/protected
get a trailing `_`; types are short CAPS width-codes (CHA/ISC/IUD/BOL); structs are
CamelCase with T(POD)/A(utoject) prefix; functions are CamelCase with T/A kind prefixes
and _NC/C markers; locals are snake_case; everything lives in `namespace _`; every file
starts with AStarship copyright, `#pragma once`, a `CRABS_*` guard, and `#if SEAM >= CRABS_*`
gating.** The name tells you the kind, width, access level, and mutability — before you
read the body.