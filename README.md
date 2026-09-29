
# Command & Conquer: Red Alert — macOS Native Port

This repository contains the original C&C Red Alert source code (preserved for historical purposes) plus a **native macOS port** of four Command & Conquer games:

| Game | Engine | Status |
|------|--------|--------|
| **Tiberian Dawn** (C&C 1) | [Vanilla-Conquer](https://github.com/klab-mao/Vanilla-Conquer) | ✅ Working |
| **Red Alert 1** | [Vanilla-Conquer](https://github.com/klab-mao/Vanilla-Conquer) | ✅ Working |
| **Red Alert 2** | [OpenRA/ra2](https://github.com/OpenRA/ra2) | ✅ Working |
| **Yuri's Revenge** | [klab-mao/Yuris-Revenge](https://github.com/klab-mao/Yuris-Revenge) | ✅ Working |

All games run **natively** on macOS (Apple Silicon + Intel) — no Wine, no Rosetta.

## Quick Start

```bash
# Launch any game (auto-builds if needed)
port/run.sh td       # Tiberian Dawn
port/run.sh ra       # Red Alert 1
port/run.sh ra2      # Red Alert 2
port/run.sh yuri     # Yuri's Revenge
port/run.sh          # Interactive menu
```

Games run windowed at 1280×800 with OpenGL rendering.

## Prerequisites

- macOS 12+ (Apple Silicon or Intel)
- Xcode Command Line Tools
- [Mono](https://www.mono-project.com/) (for RA2/YR)
- [SDL2](https://www.libsdl.org/) + OpenAL (for TD/RA1, installed via Homebrew)
- Game data files (RA2/YR require original `.mix` files from a legal copy)

## Repository Structure

```
CODE/              Original C&C Red Alert source (Watcom/TASM, Win32)
port/
  run.sh           Unified launcher (td|ra|ra2|yuri)
  build_macos.sh   TD/RA1 build script (Vanilla-Conquer)
  vanilla-conquer/ TD + RA1 engine (gitignored, cloned on first run)
  openra-ra2/      RA2 mod — OpenRA/ra2 (gitignored, cloned on first run)
  openra-yr/       YR mod — klab-mao/Yuris-Revenge fork (gitignored, cloned on first run)
  game-data/       Game data files (gitignored)
  patch-save.py    YR save file editor (objectives, cash)
  fix-map-uid.py   Save file map UID patcher
```

## Yuri's Revenge — Notable Fixes

The YR fork (`klab-mao/Yuris-Revenge`) includes extensive fixes:

- **10 coop campaign missions** enabled for single-player (Allied, Soviet, Yuri, World Alliance)
- **Bot AI** auto-created for coop maps (server-side fix in `LobbyCommands.ClientJoined`)
- **Faction locking** per campaign type (Allied→Allies, Soviet→Soviets, Yuri→Yuri)
- **F12 cheat key** — adds 50,000 credits (single-player only)
- **Snapshot save/load** — custom engine patch for mid-mission saves
- **Victory fix** — `WinState` enum not exposed to Lua; replaced with boolean flag
- **Crash fixes** — BunkerCargo, GrantConditionOnCapture, GrantExternalConditionPower, Sound.cs
- **UI fixes** — pause flicker, observer sidebar 花屏, music (thememd.mix workaround)

Engine C# patches live in `port/openra-yr/engine/` (gitignored by the YR repo — local-only).

## Forks

| Upstream | Fork |
|----------|------|
| `electronicarts/CnC_Red_Alert` | [`klab-mao/CnC_Red_Alert`](https://github.com/klab-mao/CnC_Red_Alert) |
| `OpenRA/Vanilla-Conquer` | [`klab-mao/Vanilla-Conquer`](https://github.com/klab-mao/Vanilla-Conquer) |
| `cookgreen/Yuris-Revenge` | [`klab-mao/Yuris-Revenge`](https://github.com/klab-mao/Yuris-Revenge) |

## Original Source Code

The `CODE/` directory contains the original C&C Red Alert source code released by Electronic Arts under GPL v3. It requires Watcom C/C++ v10.6 and Borland TASM v4.0 to compile (Win32 only). See [LICENSE.md](LICENSE.md) for details.

## License

Original source code: GPL v3 with additional EA terms — see [LICENSE.md](LICENSE.md).
Port scripts (`port/`): GPL v3.
