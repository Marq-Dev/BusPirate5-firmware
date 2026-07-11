#!/usr/bin/env bash
set -euo pipefail

mkdir -p build-host

if cc -std=c11 -Wall -Wextra -Werror \
  tests/host/test_tvbgone_macro_scope.c \
  -o build-host/test_tvbgone_macro_scope-red 2>/dev/null; then
  echo "expected TV-B-Gone macro-scope regression to fail" >&2
  exit 1
fi

cc -std=c11 -Wall -Wextra -Werror \
  -DTEST_WITH_TVBGONE_CLEANUP=1 \
  tests/host/test_tvbgone_macro_scope.c \
  -o build-host/test_tvbgone_macro_scope
./build-host/test_tvbgone_macro_scope

cc -std=c11 -Wall -Wextra -Werror \
  -Isrc \
  tests/host/test_disk_format_flow.c \
  src/commands/global/disk_format_flow.c \
  -o build-host/test_disk_format_flow
./build-host/test_disk_format_flow

echo "Host tests passed"
