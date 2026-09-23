---
name: redalert-macos-port
description: Verified procedure for building/running C&C TD, RA1, RA2, and Yuri's Revenge on macOS (all native, no Wine)
type: skill
---

# Skill: Build & Run C&C (TD + RA1 + RA2 + YR) on macOS

Verified on Apple Silicon (arm64), macOS 27.0, cmake 4.4.3, Apple clang, .NET 9.0, Mono 6.12.
All four games confirmed launching and rendering on 2026-09-22.

## Context

This repo is the original EA source drop of Command & Conquer Red Alert (Win95/DirectX 5 codebase, Watcom C++ 10.6 + TASM 4.0). It cannot compile on macOS directly: it depends on DirectX 5, DirectX Media, GCL, HMI SOS audio, and Borland/Watcom toolchains.

## Research summary (2026-09-22)

| Path | Verdict |
|---|---|
| [Vanilla-Conquer](https://github.com/TheAssemblyArmada/Vanilla-Conquer) / [klab-mao fork](https://github.com/klab-mao/Vanilla-Conquer) | Proven. Same source, modernized: DirectDraw/HMI/Win32 → SDL2 + OpenAL, ASM/IPX removed, CMake. Supports macOS. Fork adds `SDL_WINDOW_RESIZABLE`. **Used for TD + RA1.** |
| [OpenRA/ra2](https://github.com/OpenRA/ra2) | RA2 mod for OpenRA engine. 1.1k stars, actively maintained (last commit Nov 2025). Runs natively on macOS via .NET + SDL2. **Used for RA2.** |
| [cookgreen/Yuris-Revenge](https://github.com/cookgreen/Yuris-Revenge) | Yuri's Revenge mod for OpenRA. 180 stars. Runs natively via Mono + SDL2. **Used for YR.** |
| Whisky/Wine | Whisky server (`data.getwhisky.app`) is permanently down (404). App archived May 2025. **Not viable.** |
| In-repo native port from scratch | Equivalent to re-doing Vanilla-Conquer. Multi-week effort. |

## Quick start (verified working)

```zsh
# TD + RA1 (Vanilla-Conquer)
brew install cmake openal-soft
./port/build_macos.sh

# RA2 + YR (OpenRA mods)
git clone --depth 1 https://github.com/OpenRA/ra2.git port/openra-ra2
make -C port/openra-ra2
git clone --depth 1 https://github.com/cookgreen/Yuris-Revenge.git port/openra-yr
make -C port/openra-yr

# Launch
./port/run.sh td     # Tiberian Dawn  (Vanilla-Conquer native)
./port/run.sh ra     # Red Alert      (Vanilla-Conquer native)
./port/run.sh ra2    # Red Alert 2    (OpenRA native, .NET)
./port/run.sh yuri   # Yuri's Revenge (OpenRA native, Mono)
./port/run.sh        # interactive menu
```

## Game data (required to play)

| Game | Engine | Data path | Source |
|---|---|---|---|
| Tiberian Dawn | Vanilla-Conquer (native) | `.../Vanilla-Conquer/vanillatd/` | C&C Gold freeware zip (`command-aand-conquer-gold` on archive.org) |
| Red Alert 1 | Vanilla-Conquer (native) | `.../Vanilla-Conquer/vanillara/` | RA freeware CD ISO (`CommandConquerRedAlertUSA` on archive.org) |
| Red Alert 2 | OpenRA RA2 mod (native) | `.../OpenRA/Content/ra2/` | RA2 no-install package (`red-alert-2_202103` on archive.org) — needs `ra2.mix`, `language.mix`, `theme.mix` |
| Yuri's Revenge | OpenRA YR mod (native) | `.../OpenRA/Content/yr/` | Same package — needs `ra2md.mix`, `langmd.mix`, `thememd.mix` |

### RA2/YR data setup

```zsh
# Download RA2 no-install package from archive.org
curl -sL -o port/game-data/ra2.7z "https://archive.org/download/red-alert-2_202103/Red%20Alert%202.7z"
7zz x -oport/game-data/ra2 port/game-data/ra2.7z -y

# Copy MIX files for OpenRA
RA2DIR="port/game-data/ra2/Red Alert 2"
OPENDIR="$HOME/Library/Application Support/OpenRA"
mkdir -p "$OPENDIR/Content/ra2" "$OPENDIR/Content/yr"
cp "$RA2DIR/ra2.mix" "$RA2DIR/language.mix" "$RA2DIR/theme.mix" "$OPENDIR/Content/ra2/"
cp "$RA2DIR/ra2md.mix" "$RA2DIR/langmd.mix" "$RA2DIR/thememd.mix" "$OPENDIR/Content/yr/"
```

### RA1 data setup

```zsh
brew install sevenzip bchunk
curl -sL -o port/game-data/ra_allied.zip \
  "https://archive.org/download/CommandConquerRedAlertUSA/Command%20%26%20Conquer%20-%20Red%20Alert%20%28USA%29%20%28Allied%20Disc%29.zip"
7zz x -oport/game-data port/game-data/ra_allied.zip -y
bchunk "port/game-data/Command & Conquer - Red Alert (USA) (Allied Disc).bin" \
       "port/game-data/Command & Conquer - Red Alert (USA) (Allied Disc).cue" \
       port/game-data/allied
DATADIR="$HOME/Library/Application Support/Vanilla-Conquer/vanillara"
mkdir -p "$DATADIR"
7zz x port/game-data/allied01.iso -o"$DATADIR" MAIN.MIX INSTALL/REDALERT.MIX SETUP/AUD.MIX -y
mv "$DATADIR/INSTALL/REDALERT.MIX" "$DATADIR/" && mv "$DATADIR/SETUP/AUD.MIX" "$DATADIR/"
```

## Windowed mode (resizable window)

**TD/RA1**: Edit `~/Library/Application Support/Vanilla-Conquer/vanillara/redalert.ini`:
```ini
[Video]
WindowWidth=1280
WindowHeight=800
Windowed=yes
```
The `SDL_WINDOW_RESIZABLE` flag is in the [klab-mao fork](https://github.com/klab-mao/Vanilla-Conquer/commit/91196a1). Toggle fullscreen with Alt+Enter.

**RA2/YR**: `run.sh` passes `Graphics.Mode=Windowed Graphics.Renderer=OpenGL`. The enum value is `Windowed` (not `Window`). Resolution settings available in-game via Settings menu.

## .NET compatibility note

The OpenRA RA2 mod (engine `release-20231010`) targets .NET 6.0 but runs on .NET 8.0/9.0 via `DOTNET_ROLL_FORWARD=Major` (set automatically in `run.sh`). The YR mod (engine `release-20200503`) uses Mono directly.

## Layout

- `port/build_macos.sh` — build TD + RA1 (Vanilla-Conquer)
- `port/run.sh` — game launcher (`./port/run.sh [td|ra|ra2|yuri]`)
- `port/vanilla-conquer/` — cloned Vanilla-Conquer fork (gitignored)
- `port/build/` — CMake build tree + apps (gitignored)
- `port/openra-ra2/` — OpenRA RA2 mod (gitignored)
- `port/openra-yr/` — OpenRA YR mod (gitignored)
- `port/game-data/` — game data archives (gitignored)

## Key debugging notes

- **Data path (TD/RA1)**: `~/Library/Application Support/Vanilla-Conquer/vanillara/` (NOT the parent). Wrong path → SIGSEGV in `Bootstrap()` at `memmove(GamePalette, MFCD::Retrieve("TEMPERAT.PAL"), 768)`.
- **MIX format**: CD mixes use Westwood's encrypted/protected variant (first 4 bytes: `00 00 02 00` → `IsEncrypted` flag). Game decrypts via `PKStraw` with hardcoded public key.
- **OpenRA content**: RA2 needs `ra2.mix` + `language.mix` minimum. YR needs `ra2md.mix` + `langmd.mix`. Content installer checks for these exact filenames.
- **Local Support directory**: OpenRA's `Platform.cs` checks for a local `engine/Support/` directory first. Without it, `--extract ra2.mix` fails with "File not found" even when files are in `~/Library/Application Support/OpenRA/`. `run.sh` auto-creates `engine/Support/Content/ra2/` (and `yr/`) and copies MIX files there.
- **YR music crash**: The YR mod's older engine (release-20200503) can't parse some WAV files (e.g. `drok.wav`), throwing `InvalidDataException`. Fixed by patching `engine/OpenRA.Game/Sound/Sound.cs` line 82: replace `throw new InvalidDataException(...)` with `Log.Write("sound", ...); return default(T);`. The caller already handles `null` gracefully. Must `make` in engine dir after patching.
- **Whisky deprecated**: Whisky's Wine engine server (`data.getwhisky.app/Wine/Libraries.tar.gz`) returns 404. App archived May 2025. Use OpenRA mods instead.
