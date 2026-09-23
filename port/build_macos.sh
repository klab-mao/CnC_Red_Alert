#!/bin/zsh
# Build C&C Tiberian Dawn + Red Alert on macOS using Vanilla-Conquer.
# Produces port/build/vanillatd.app and port/build/vanillara.app.
set -e
cd "$(dirname "$0")"
VCPATH="vanilla-conquer"
VCURL="https://github.com/klab-mao/Vanilla-Conquer.git"
VCCOMMIT="91196a1"

command -v cmake >/dev/null || { echo "cmake missing: brew install cmake"; exit 1; }
command -v brew >/dev/null && brew list openal-soft >/dev/null 2>&1 || {
  echo "openal-soft missing: brew install openal-soft"; exit 1
}

if [ ! -d "$VCPATH" ]; then
  git clone --depth 1 "$VCURL" "$VCPATH"
  git -C "$VCPATH" fetch --depth 1 origin "$VCCOMMIT" && git -C "$VCPATH" checkout "$VCCOMMIT"
fi

cmake -B build -S "$VCPATH" \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DBUILD_VANILLATD=ON \
  -DBUILD_VANILLARA=ON \
  -DBUILD_REMASTERTD=OFF \
  -DBUILD_REMASTERRA=OFF \
  -DBUILD_TESTS=OFF \
  -DBUILD_TOOLS=OFF \
  -DCMAKE_PREFIX_PATH="/opt/homebrew/opt/openal-soft"

cmake --build build --parallel "$(sysctl -n hw.ncpu)"

echo
echo "Build OK:"
echo "  TD:  build/vanillatd.app/Contents/MacOS/vanillatd"
echo "  RA:  build/vanillara.app/Contents/MacOS/vanillara"
echo "Run: ./port/run.sh [td|ra]"
