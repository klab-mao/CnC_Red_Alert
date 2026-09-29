#!/bin/zsh
# Launch C&C games on macOS.
# Usage: ./port/run.sh [td|ra|ra2|yuri]
#   td   = Tiberian Dawn (1995)      — Vanilla-Conquer native
#   ra   = Red Alert (1996)          — Vanilla-Conquer native
#   ra2  = Red Alert 2 (2000)        — OpenRA RA2 mod (native)
#   yuri = Yuri's Revenge (2001)     — OpenRA YR mod (native)
cd "$(dirname "$0")"

GAME="${1:-}"
if [ -z "$GAME" ]; then
  echo "Select game:"
  echo "  1) Tiberian Dawn"
  echo "  2) Red Alert"
  echo "  3) Red Alert 2"
  echo "  4) Yuri's Revenge"
  printf "Choice [1-4]: "
  read choice
  case "$choice" in
    1) GAME=td ;; 2) GAME=ra ;; 3) GAME=ra2 ;; 4) GAME=yuri ;; *) echo "Invalid"; exit 1 ;;
  esac
fi

# Ensure OpenRA mod content is in local Support dir (engine checks Support/ first)
setup_openra_content() {
  local moddir="$1"
  local ra2data="game-data/ra2/Red Alert 2"
  [ -d "$ra2data" ] || { echo "RA2 game data not found at $ra2data"; exit 1; }
  local support="$moddir/engine/Support"
  if [ ! -d "$support/Content/ra2" ]; then
    mkdir -p "$support/Content/ra2"
    cp "$ra2data/ra2.mix" "$ra2data/language.mix" "$ra2data/theme.mix" "$support/Content/ra2/" 2>/dev/null
  fi
}

case "$GAME" in
  td)
    BIN="build/vanillatd.app/Contents/MacOS/vanillatd"
    [ -x "$BIN" ] || { echo "TD not built. Run ./port/build_macos.sh first."; exit 1; }
    exec "$BIN" ;;
  ra)
    BIN="build/vanillara.app/Contents/MacOS/vanillara"
    [ -x "$BIN" ] || { echo "RA not built. Run ./port/build_macos.sh first."; exit 1; }
    exec "$BIN" ;;
  ra2)
    MODDIR="openra-ra2"
    [ -d "$MODDIR" ] || { echo "RA2 mod not found. Run: git clone https://github.com/OpenRA/ra2.git $MODDIR && cd $MODDIR && make"; exit 1; }
    [ -f "$MODDIR/engine/bin/OpenRA.dll" ] || { echo "RA2 mod not built. Run: cd $MODDIR && make"; exit 1; }
    setup_openra_content "$MODDIR"
    exec env DOTNET_ROLL_FORWARD=Major "$MODDIR/launch-game.sh" Graphics.Renderer=OpenGL Graphics.Mode=Windowed Graphics.WindowedSize=1280,800 ;;
  yuri)
    MODDIR="openra-yr"
    [ -d "$MODDIR" ] || { echo "YR mod not found. Run: git clone git@github.com:klab-mao/Yuris-Revenge.git $MODDIR && cd $MODDIR && make"; exit 1; }
    [ -f "$MODDIR/engine/OpenRA.Game.exe" ] || { echo "YR mod not built. Run: cd $MODDIR && make"; exit 1; }
    setup_openra_content "$MODDIR"
    if [ ! -d "$MODDIR/engine/Support/Content/yr" ]; then
      mkdir -p "$MODDIR/engine/Support/Content/yr"
      cp "game-data/ra2/Red Alert 2/ra2md.mix" "game-data/ra2/Red Alert 2/langmd.mix" "game-data/ra2/Red Alert 2/thememd.mix" "$MODDIR/engine/Support/Content/yr/" 2>/dev/null
    fi
    exec "$MODDIR/launch-game.sh" Graphics.Renderer=OpenGL Graphics.Mode=Windowed Graphics.WindowedSize=1280,800 ;;
  *)
    echo "Usage: $0 [td|ra|ra2|yuri]"; exit 1 ;;
esac
