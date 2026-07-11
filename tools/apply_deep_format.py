#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8", newline="\n")


def replace_once(path: str, old: str, new: str) -> None:
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old[:80]!r}")
    write(path, text.replace(old, new, 1))


def regex_replace_once(path: str, pattern: str, replacement: str) -> None:
    text = read(path)
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"{path}: expected one regex anchor, found {count}: {pattern!r}")
    write(path, updated)


# Long-only option query.
h = read("src/lib/bp_args/bp_cmd.h")
if "bp_cmd_find_long_flag" not in h:
    replace_once(
        "src/lib/bp_args/bp_cmd.h",
        "bool bp_cmd_find_flag(const bp_command_def_t *def, char flag);\n",
        '''bool bp_cmd_find_flag(const bp_command_def_t *def, char flag);

/**
 * @brief Check whether an exact named long option is present.
 * @param def        Command definition used to identify and skip option values.
 * @param long_name  Long option name without the leading "--".
 * @return true if the exact long option is present.
 */
bool bp_cmd_find_long_flag(const bp_command_def_t *def,
                           const char *long_name);
''',
    )

c = read("src/lib/bp_args/bp_cmd.c")
if "bool bp_cmd_find_long_flag" not in c:
    replace_once(
        "src/lib/bp_args/bp_cmd.c",
        '''bool bp_cmd_find_flag(const bp_command_def_t *def, char flag) {
    const char *val;
    size_t val_len;
    return cmd_scan_flag(def, flag, &val, &val_len);
}
''',
        '''bool bp_cmd_find_flag(const bp_command_def_t *def, char flag) {
    const char *val;
    size_t val_len;
    return cmd_scan_flag(def, flag, &val, &val_len);
}

bool bp_cmd_find_long_flag(const bp_command_def_t *def,
                           const char *long_name) {
    if (!def || !long_name || !*long_name) {
        return false;
    }

    const char *p = ln_cmdln_current();
    const char *end = p + ln_cmdln_remaining();

    p = skip_ws(p, end);
    p = skip_tok(p, end);

    while (p < end) {
        p = skip_ws(p, end);
        if (p >= end || *p == '\0') {
            break;
        }

        if (*p == '-' && p + 1 < end && p[1] == '-') {
            p += 2;
            const char *name_start = p;
            while (p < end && *p != '=' && *p != ' ' &&
                   *p != '\t' && *p != '\0') {
                p++;
            }
            const size_t name_len = (size_t)(p - name_start);
            const bp_command_opt_t *opt =
                find_opt_by_long_name(def, name_start, name_len);
            const bool match = opt &&
                tok_eq(name_start, name_len, long_name);

            if (match && opt->arg_type == BP_ARG_NONE &&
                !(p < end && *p == '=')) {
                return true;
            }

            if (p < end && *p == '=') {
                p = skip_tok(p, end);
            } else if (opt && opt->arg_type != BP_ARG_NONE) {
                p = skip_ws(p, end);
                if (p < end && *p != '-' && *p != '\0') {
                    p = skip_tok(p, end);
                }
            }
            continue;
        }

        if (*p == '-' && p + 1 < end && p[1] != '-' &&
            p[1] != ' ' && p[1] != '\0') {
            const char opt_char = p[1];
            p += 2;
            const bp_command_opt_t *opt =
                find_opt_in_def(def, opt_char | 0x20);
            if (!opt) {
                opt = find_opt_in_def(def, opt_char);
            }
            if (opt && opt->arg_type != BP_ARG_NONE) {
                p = skip_ws(p, end);
                if (p < end && *p != '-' && *p != '\0') {
                    p = skip_tok(p, end);
                }
            }
            continue;
        }

        p = skip_tok(p, end);
    }

    return false;
}
''',
    )

# Compile the pure flow into all firmware variants.
cmake = read("src/CMakeLists.txt")
if "commands/global/disk_format_flow.c" not in cmake:
    replace_once(
        "src/CMakeLists.txt",
        "        commands/global/disk.c\n        commands/global/disk.h\n",
        "        commands/global/disk.c\n        commands/global/disk.h\n        commands/global/disk_format_flow.c\n        commands/global/disk_format_flow.h\n",
    )

# NAND/Dhara deep reset.
h = read("src/nand/nand_ftl_diskio.h")
if "diskio_deep_reset_result_t" not in h:
    replace_once(
        "src/nand/nand_ftl_diskio.h",
        "#define __NAND_FTL_DISKIO_H\n\n",
        '#define __NAND_FTL_DISKIO_H\n\n#include <stdbool.h>\n#include "fatfs/diskio.h"\n\n',
    )
    replace_once(
        "src/nand/nand_ftl_diskio.h",
        "DSTATUS diskio_initialize(BYTE drv);\n",
        '''typedef enum {
    DISKIO_DEEP_RESET_STAGE_NONE = 0,
    DISKIO_DEEP_RESET_STAGE_INVALID_DRIVE,
    DISKIO_DEEP_RESET_STAGE_NAND_INIT,
    DISKIO_DEEP_RESET_STAGE_NAND_ERASE,
    DISKIO_DEEP_RESET_STAGE_FTL_INIT,
} diskio_deep_reset_stage_t;

typedef struct {
    diskio_deep_reset_stage_t stage;
    int status;
} diskio_deep_reset_result_t;

bool diskio_deep_reset(BYTE drv,
                       diskio_deep_reset_result_t *result);

DSTATUS diskio_initialize(BYTE drv);
''',
    )

c = read("src/nand/nand_ftl_diskio.c")
if "#include <string.h>" not in c:
    replace_once(
        "src/nand/nand_ftl_diskio.c",
        "#include <stdint.h>\n",
        "#include <stdint.h>\n#include <string.h>\n",
    )
if "bool diskio_deep_reset(BYTE drv" not in read("src/nand/nand_ftl_diskio.c"):
    replace_once(
        "src/nand/nand_ftl_diskio.c",
        "DSTATUS diskio_status(BYTE drv) {\n",
        '''static void set_deep_reset_result(
    diskio_deep_reset_result_t *result,
    diskio_deep_reset_stage_t stage,
    int status) {
    if (result) {
        result->stage = stage;
        result->status = status;
    }
}

bool diskio_deep_reset(BYTE drv,
                       diskio_deep_reset_result_t *result) {
    set_deep_reset_result(result,
                          DISKIO_DEEP_RESET_STAGE_NONE,
                          SPI_NAND_RET_OK);

    if (drv) {
        set_deep_reset_result(result,
                              DISKIO_DEEP_RESET_STAGE_INVALID_DRIVE,
                              STA_NOINIT);
        return false;
    }

    if (!mutex_is_initialized(&diskio_mutex)) {
        mutex_init(&diskio_mutex);
    }

    mutex_enter_blocking(&diskio_mutex);
    initialized = false;

    memset(&dhara_nand_parameters, 0,
           sizeof(dhara_nand_parameters));
    memset(&map, 0, sizeof(map));
    memset(page_buffer, 0xff, sizeof(page_buffer));

    int status = spi_nand_init(&dhara_nand_parameters);
    if (status != SPI_NAND_RET_OK) {
        set_deep_reset_result(result,
                              DISKIO_DEEP_RESET_STAGE_NAND_INIT,
                              status);
        mutex_exit(&diskio_mutex);
        return false;
    }

    status = spi_nand_clear();
    if (status != SPI_NAND_RET_OK) {
        set_deep_reset_result(result,
                              DISKIO_DEEP_RESET_STAGE_NAND_ERASE,
                              status);
        mutex_exit(&diskio_mutex);
        return false;
    }

    dhara_map_init(&map,
                   &dhara_nand_parameters,
                   page_buffer,
                   4);

    if (dhara_map_capacity(&map) == 0) {
        set_deep_reset_result(result,
                              DISKIO_DEEP_RESET_STAGE_FTL_INIT,
                              -1);
        mutex_exit(&diskio_mutex);
        return false;
    }

    initialized = true;
    mutex_exit(&diskio_mutex);
    return true;
}

DSTATUS diskio_status(BYTE drv) {
''',
    )

# CLI integration.
disk_path = "src/commands/global/disk.c"
disk = read(disk_path)
if "disk_format_flow.h" not in disk:
    replace_once(
        disk_path,
        '#include "pirate/file.h"\n',
        '''#include "pirate/file.h"
#include "commands/global/disk_format_flow.h"
#include "msc_disk.h"
#ifdef BP_HW_STORAGE_NAND
#include "nand/nand_ftl_diskio.h"
#endif
''',
    )

if "disk_deep_reset_adapter" not in read(disk_path):
    replace_once(
        disk_path,
        "uint8_t disk_format(void) {\n",
        '''static bool disk_deep_reset_adapter(int *stage, int *status) {
#ifdef BP_HW_STORAGE_NAND
    diskio_deep_reset_result_t result;
    const bool ok = diskio_deep_reset(0, &result);
    *stage = (int)result.stage;
    *status = result.status;
    return ok;
#else
    *stage = 0;
    *status = 0;
    return false;
#endif
}

static const disk_format_deep_ops_t disk_deep_ops = {
    .eject_usb = eject_usbmsdrive,
    .unmount_storage = storage_unmount,
    .reset_storage = disk_deep_reset_adapter,
    .format_storage = storage_format,
    .mount_storage = storage_mount,
    .insert_usb = insert_usbmsdrive,
};

#ifdef BP_HW_STORAGE_NAND
static const char *disk_deep_reset_stage_name(int stage) {
    switch ((diskio_deep_reset_stage_t)stage) {
        case DISKIO_DEEP_RESET_STAGE_INVALID_DRIVE:
            return "drive validation";
        case DISKIO_DEEP_RESET_STAGE_NAND_INIT:
            return "NAND initialization";
        case DISKIO_DEEP_RESET_STAGE_NAND_ERASE:
            return "physical NAND erase";
        case DISKIO_DEEP_RESET_STAGE_FTL_INIT:
            return "FTL initialization";
        case DISKIO_DEEP_RESET_STAGE_NONE:
        default:
            return "unknown stage";
    }
}
#endif

uint8_t disk_format(void) {
''',
    )

regex_replace_once(
    disk_path,
    r"static const char\* const format_usage\[\] = \{.*?\n\};\n\nstatic const bp_command_opt_t disk_format_opts\[\] = \{.*?\n\};",
    '''static const char* const format_usage[] = {
    "format [-y] [--deep]",
    "Format FAT filesystem:%s format",
    "Format without confirmation:%s format -y",
    "Raw erase NAND, rebuild FTL and FAT:%s format --deep",
    "Deep format without confirmation:%s format --deep -y",
};

static const bp_command_opt_t disk_format_opts[] = {
    { "yes",  'y', BP_ARG_NONE, NULL, T_HELP_FLASH_YES_OVERRIDE },
    { "deep",  0,  BP_ARG_NONE, NULL, T_HELP_DISK_FORMAT_DEEP },
    { 0 }
};''',
)

regex_replace_once(
    disk_path,
    r"void disk_format_handler\(struct command_result\* res\) \{.*?\n\}\n\nstatic const char\* const label_usage",
    '''void disk_format_handler(struct command_result* res) {
    if (bp_cmd_help_check(&disk_format_def, res->help_flag)) {
        return;
    }

    const bool deep =
        bp_cmd_find_long_flag(&disk_format_def, "deep");

#ifndef BP_HW_STORAGE_NAND
    if (deep) {
        printf("Error: Deep format is only supported on NAND-backed Bus Pirate models.\\r\\n");
        res->error = true;
        return;
    }
#endif

    if (deep) {
        if (!bp_cmd_confirm(&disk_format_def,
                            "Deep format raw NAND storage?")) {
            return;
        }
        if (!bp_cmd_confirm(
                &disk_format_def,
                "Are you sure? ALL STORAGE DATA AND MAPPING STATE WILL BE ERASED.")) {
            return;
        }
    } else {
        if (!bp_cmd_confirm(&disk_format_def,
                            "Erase the internal storage?")) {
            return;
        }
        if (!bp_cmd_confirm(
                &disk_format_def,
                "Are you sure? ALL DATA WILL BE ERASED.")) {
            return;
        }
    }

    if (deep) {
        printf("\\r\\n\\r\\nDeep formatting NAND storage...\\r\\n");
        printf("[1/4] Ejecting and unmounting storage\\r\\n");
        printf("[2/4] Erasing physical NAND blocks\\r\\n");

        const disk_format_deep_result_t result =
            disk_format_deep_run(true, &disk_deep_ops);

        switch (result.status) {
            case DISK_FORMAT_DEEP_OK:
                printf("[3/4] Reinitialized flash translation layer\\r\\n");
                printf("[4/4] Created and mounted FAT filesystem\\r\\n");
                printf("Storage mounted: %7.2f GB %s\\r\\n",
                       system_config.storage_size,
                       storage_fat_type_labels[
                           system_config.storage_fat_type - 1]);
                printf("Deep format success!\\r\\n\\r\\n");
                return;

            case DISK_FORMAT_DEEP_RESET_FAILED:
#ifdef BP_HW_STORAGE_NAND
                printf("Error: Deep reset failed during %s (status %d).\\r\\n",
                       disk_deep_reset_stage_name(result.reset_stage),
                       result.reset_status);
#else
                printf("Error: Deep reset failed (status %d).\\r\\n",
                       result.reset_status);
#endif
                break;

            case DISK_FORMAT_DEEP_FORMAT_FAILED:
                storage_file_error(result.fatfs_status);
                printf("\\r\\nError: FAT creation failed after NAND reset.\\r\\n");
                break;

            case DISK_FORMAT_DEEP_MOUNT_FAILED:
                storage_file_error(result.fatfs_status);
                printf("\\r\\nError: Mount failed after deep format.\\r\\n");
                break;

            case DISK_FORMAT_DEEP_UNSUPPORTED:
            default:
                printf("Error: Deep format is unavailable.\\r\\n");
                break;
        }

        system_config.storage_available = false;
        res->error = true;
        return;
    }

    printf("\\r\\n\\r\\nFormatting...\\r\\n");
    const uint8_t format_status = disk_format();
    if (format_status != FR_OK) {
        storage_file_error(format_status);
        res->error = true;
    }
}

static const char* const label_usage''',
)

# Help text source; generated language files are rebuilt by the workflow.
en_path = "src/translation/en-us.h"
en = read(en_path)
if "T_HELP_DISK_FORMAT_DEEP" not in en:
    updated, count = re.subn(
        r'(?m)^(\s*\[T_HELP_DISK_FORMAT\]\s*=\s*"[^"]*",\s*)$',
        r'\1\n\t[T_HELP_DISK_FORMAT_DEEP]="Raw erase NAND, rebuild the flash translation layer, then create FAT",',
        en,
        count=1,
    )
    if count != 1:
        raise RuntimeError("src/translation/en-us.h: T_HELP_DISK_FORMAT anchor not found")
    write(en_path, updated)

# CI host-test gate.
workflow_path = ".github/workflows/build.yaml"
workflow = read(workflow_path)
if "host-tests:" not in workflow:
    replace_once(
        workflow_path,
        "jobs:\n  build:\n",
        '''jobs:
  host-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run host and contract tests
        run: |
          python3 -m unittest tests/test_deep_format_contract.py -v
          bash tests/host/run_host_tests.sh

  build:
    needs: host-tests
''',
    )

print("Existing firmware files updated")
