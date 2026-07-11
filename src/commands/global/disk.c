/**
 * @file disk.c
 * @author
 * @brief implements all the disk cli commands
 * @version 0.1
 * @date 2024-05-11
 *
 * @copyright Copyright (c) 2024
 * Modified by Lior Shalmay Copyright (c) 2024
 */
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "pico/stdlib.h"
#include "pirate.h"
#include "system_config.h"
#include "command_struct.h"
#include "fatfs/ff.h"
#include "ui/ui_term.h"
#include "ui/ui_help.h"
#include "pirate/storage.h"
#include "pirate/mem.h"
#include "lib/bp_args/bp_cmd.h"
#include "pirate/file.h"
#include "commands/global/disk_format_flow.h"
#include "msc_disk.h"
#ifdef BP_HW_STORAGE_NAND
#include "fatfs/diskio.h"
#include "nand/nand_ftl_diskio.h"
#endif

static const char* const cat_usage[] = {
    "cat <file>",
    "Print file contents:%s cat example.txt",
};

static const bp_command_positional_t disk_cat_positionals[] = {
    { "file", NULL, T_HELP_GCMD_DISK_CAT_FILE, true },
    { 0 }
};

const bp_command_def_t disk_cat_def = {
    .name         = "cat",
    .description  = T_HELP_DISK_CAT,
    .actions      = NULL,
    .action_count = 0,
    .opts         = NULL,
    .positionals      = disk_cat_positionals,
    .positional_count = 1,
    .usage        = cat_usage,
    .usage_count  = count_of(cat_usage),
};

void disk_cat_handler(struct command_result* res) {
    // check help
    if (bp_cmd_help_check(&disk_cat_def, res->help_flag)) {
        return;
    }

    FIL fil;    /* File object needed for each open file */
    FRESULT fr; /* FatFs return code */
    char file[512];
    char location[32];
    if(!bp_file_get_name_positional(&disk_cat_def, 1, location, sizeof(location))){
        res->error = true;
        return;
    }
    fr = f_open(&fil, location, FA_READ);
    if (fr != FR_OK) {
        storage_file_error(fr);
        res->error = true;
        return;
    }
    /* Read every line and display it */
    while (f_gets(file, sizeof(file), &fil)) {
        printf(file);
        printf("\r"); // usually this comes first, but hopefully makes text files display better
    }
    printf("\r\n");
    /* Close the file */
    f_close(&fil);
}

static const char* const mkdir_usage[] = {
    "mkdir <dir>",
    "Create directory:%s mkdir dir",
};

static const bp_command_positional_t disk_mkdir_positionals[] = {
    { "dir", NULL, T_HELP_GCMD_DISK_MKDIR_DIR, true },
    { 0 }
};

const bp_command_def_t disk_mkdir_def = {
    .name         = "mkdir",
    .description  = T_HELP_DISK_MKDIR,
    .actions      = NULL,
    .action_count = 0,
    .opts         = NULL,
    .positionals      = disk_mkdir_positionals,
    .positional_count = 1,
    .usage        = mkdir_usage,
    .usage_count  = count_of(mkdir_usage),
};

void disk_mkdir_handler(struct command_result* res) {
    // check help
    if (bp_cmd_help_check(&disk_mkdir_def, res->help_flag)) {
        return;
    }

    FRESULT fr;
    char location[32];
    if(!bp_file_get_name_positional(&disk_mkdir_def, 1, location, sizeof(location))){
        res->error = true;
        return;
    }
    fr = f_mkdir(location);
    if (fr != FR_OK) {
        storage_file_error(fr);
        res->error = true;
    }
}

static const char* const cd_usage[] = {
    "cd <dir>",
    "Change directory:%s cd dir",
};

static const bp_command_positional_t disk_cd_positionals[] = {
    { "dir", NULL, T_HELP_GCMD_DISK_CD_DIR, true },
    { 0 }
};

const bp_command_def_t disk_cd_def = {
    .name         = "cd",
    .description  = T_HELP_DISK_CD,
    .actions      = NULL,
    .action_count = 0,
    .opts         = NULL,
    .positionals      = disk_cd_positionals,
    .positional_count = 1,
    .usage        = cd_usage,
    .usage_count  = count_of(cd_usage),
};

void disk_cd_handler(struct command_result* res) {
    // check help
    if (bp_cmd_help_check(&disk_cd_def, res->help_flag)) {
        return;
    }

    FRESULT fr;
    char location[32];
    if(!bp_file_get_name_positional(&disk_cd_def, 1, location, sizeof(location))){
        res->error = true;
        return;
    }
    fr = f_chdir(location);
    if (fr != FR_OK) {
        storage_file_error(fr);
        res->error = true;
        return;
    }

    TCHAR str[128];
    fr = f_getcwd(str, 128); /* Get current directory path */
    printf("%s\r\n", str);
}

static const char* const rm_usage[] = {
    "rm <file|dir>",
    "Delete file:%s rm example.txt",
    "Delete directory:%s rm dir",
};

static const bp_command_positional_t disk_rm_positionals[] = {
    { "path", "file", T_HELP_GCMD_DISK_RM_PATH, false },
    { 0 }
};

const bp_command_def_t disk_rm_def = {
    .name         = "rm",
    .description  = T_HELP_DISK_RM,
    .actions      = NULL,
    .action_count = 0,
    .opts         = NULL,
    .positionals      = disk_rm_positionals,
    .positional_count = 1,
    .usage        = rm_usage,
    .usage_count  = count_of(rm_usage),
};

void disk_rm_handler(struct command_result* res) {
    // check help
    if (bp_cmd_help_check(&disk_rm_def, res->help_flag)) {
        return;
    }

    FRESULT fr;
    char location[32];
    if(!bp_file_get_name_positional(&disk_rm_def, 1, location, sizeof(location))){
        res->error = true;
        return;
    }
    fr = f_unlink(location);
    if (fr != FR_OK) {
        storage_file_error(fr);
        res->error = true;
    }
}

static const char* const ls_usage[] = {
    "ls [-la] [dir]",
    "List current directory:%s ls",
    "Long listing with dates:%s ls -l",
    "Show hidden/system files:%s ls -a",
    "Long listing of a directory:%s ls -l /dir",
    "Combine flags:%s ls -la",
};

static const bp_command_opt_t disk_ls_opts[] = {
    { "long", 'l', BP_ARG_NONE, NULL, T_HELP_DISK_LS_LONG },
    { "all",  'a', BP_ARG_NONE, NULL, T_HELP_DISK_LS_ALL },
    { 0 }
};

static const bp_command_positional_t disk_ls_positionals[] = {
    { "dir", NULL, T_HELP_GCMD_DISK_LS_DIR, false },
    { 0 }
};

const bp_command_def_t disk_ls_def = {
    .name         = "ls",
    .description  = T_HELP_DISK_LS,
    .actions      = NULL,
    .action_count = 0,
    .opts         = disk_ls_opts,
    .positionals      = disk_ls_positionals,
    .positional_count = 1,
    .usage        = ls_usage,
    .usage_count  = count_of(ls_usage),
};

void disk_ls_handler(struct command_result* res) {
    // check help
    if (bp_cmd_help_check(&disk_ls_def, res->help_flag)) {
        return;
    }

    // is there a trailing path to ls?
    char location[32];
    bp_cmd_get_positional_string(&disk_ls_def, 1, location, sizeof(location));

    // build flags from options
    uint8_t flags = LS_FILES | LS_DIRS | LS_SUMM;

    if (bp_cmd_find_flag(&disk_ls_def, 'l')) {
        flags |= LS_LONG | LS_SIZE;
    }
    if (bp_cmd_find_flag(&disk_ls_def, 'a')) {
        flags |= LS_HIDDEN;
    }

    if (!storage_ls(location, NULL, flags)) {
        res->error = true;
        return;
    }
}

static bool disk_deep_reset_adapter(int *stage, int *status) {
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
    // make the file system
    FRESULT fr = storage_format();
    if (fr == FR_NOT_ENOUGH_CORE) {
        printf("Error: Buffer not available. Is the scope or logic analyzer running?\r\n");
    }

    if (FR_OK != fr) {
        storage_file_error(fr);
        printf("Error: Format failed...\r\n", fr); // fs make failure
        return fr;
    }
    printf("Format success!\r\n"); // fs make success

    // retry mount
    fr = storage_mount();
    if (fr != FR_OK) {
        storage_file_error(fr);
        printf("Mount error %d\r\n", system_config.storage_mount_error);
        return fr;
    }
    printf("Storage mounted: %7.2f GB %s\r\n\r\n",
           system_config.storage_size,
           storage_fat_type_labels[system_config.storage_fat_type - 1]);
    return fr;
}

static const char* const format_usage[] = {
    "format [-y] [--deep]",
    "Format FAT filesystem:%s format",
    "Format without confirmation:%s format -y",
    "Raw erase NAND, rebuild FTL and FAT:%s format --deep",
    "Deep format without confirmation:%s format --deep -y",
};

static const bp_command_opt_t disk_format_opts[] = {
    { "yes",  'y', BP_ARG_NONE, NULL, T_HELP_FLASH_YES_OVERRIDE },
    { "deep",  0,  BP_ARG_NONE, NULL, T_HELP_DISK_FORMAT },
    { 0 }
};

const bp_command_def_t disk_format_def = {
    .name         = "format",
    .description  = T_HELP_DISK_FORMAT,
    .actions      = NULL,
    .action_count = 0,
    .opts         = disk_format_opts,
    .usage        = format_usage,
    .usage_count  = count_of(format_usage),
};

void disk_format_handler(struct command_result* res) {
    if (bp_cmd_help_check(&disk_format_def, res->help_flag)) {
        return;
    }

    const bool deep =
        bp_cmd_find_long_flag(&disk_format_def, "deep");

#ifndef BP_HW_STORAGE_NAND
    if (deep) {
        printf("Error: Deep format is only supported on NAND-backed Bus Pirate models.\r\n");
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
        printf("\r\n\r\nDeep formatting NAND storage...\r\n");
        printf("[1/4] Ejecting and unmounting storage\r\n");
        printf("[2/4] Erasing physical NAND blocks\r\n");

        const disk_format_deep_result_t result =
            disk_format_deep_run(true, &disk_deep_ops);

        switch (result.status) {
            case DISK_FORMAT_DEEP_OK:
                printf("[3/4] Reinitialized flash translation layer\r\n");
                printf("[4/4] Created and mounted FAT filesystem\r\n");
                printf("Storage mounted: %7.2f GB %s\r\n",
                       system_config.storage_size,
                       storage_fat_type_labels[
                           system_config.storage_fat_type - 1]);
                printf("Deep format success!\r\n\r\n");
                return;

            case DISK_FORMAT_DEEP_RESET_FAILED:
#ifdef BP_HW_STORAGE_NAND
                printf("Error: Deep reset failed during %s (status %d).\r\n",
                       disk_deep_reset_stage_name(result.reset_stage),
                       result.reset_status);
#else
                printf("Error: Deep reset failed (status %d).\r\n",
                       result.reset_status);
#endif
                break;

            case DISK_FORMAT_DEEP_FORMAT_FAILED:
                storage_file_error(result.fatfs_status);
                printf("\r\nError: FAT creation failed after NAND reset.\r\n");
                break;

            case DISK_FORMAT_DEEP_MOUNT_FAILED:
                storage_file_error(result.fatfs_status);
                printf("\r\nError: Mount failed after deep format.\r\n");
                break;

            case DISK_FORMAT_DEEP_UNSUPPORTED:
            default:
                printf("Error: Deep format is unavailable.\r\n");
                break;
        }

        system_config.storage_available = false;
        res->error = true;
        return;
    }

    printf("\r\n\r\nFormatting...\r\n");
    const uint8_t format_status = disk_format();
    if (format_status != FR_OK) {
        storage_file_error(format_status);
        res->error = true;
    }
}

static const char* const label_usage[] = { "label [get|set] [label]",
                                           "Get flash storage label name:%s label get",
                                           "Set flash storage label name:%s label set [label]" };

typedef enum label_sub_commands {
    GET_LABEL,
    SET_LABEL,
    INVALID_LABEL_CMD,
} label_sub_cmd_e;

static const bp_command_action_t label_actions[] = {
    { GET_LABEL, "get", T_HELP_DISK_LABEL_GET },
    { SET_LABEL, "set", T_HELP_DISK_LABEL_SET },
};

static const bp_command_positional_t disk_label_positionals[] = {
    { "label",    NULL,      T_HELP_GCMD_DISK_LABEL_NAME, false },
    { 0 }
};

const bp_command_def_t disk_label_def = {
    .name         = "label",
    .description  = T_HELP_DISK_LABEL,
    .actions      = label_actions,
    .action_count = count_of(label_actions),
    .opts         = NULL,
    .positionals      = disk_label_positionals,
    .positional_count = 1,
    .usage        = label_usage,
    .usage_count  = count_of(label_usage),
};

#define MAX_LABEL_LENGTH (11)

void disk_label_handler(struct command_result* res) {
    // check help
    if (bp_cmd_help_check(&disk_label_def, res->help_flag)) {
        return;
    }

    char command_string[4];
    char label_string[MAX_LABEL_LENGTH + 2]; // maximum label length for fat12/16 is 11 characters
    FRESULT f_result;
    uint32_t command = INVALID_LABEL_CMD;
    DWORD label_id;
    res->error = true;

    if (!bp_cmd_get_action(&disk_label_def, &command)) {
        printf("Missing command argument, please provide either get or set commands\r\n");
        return;
    }

    switch (command) {
        case GET_LABEL:
            f_result = f_getlabel("", label_string, &label_id);
            if (f_result == FR_OK) {
                printf("disk label: %s", label_string);
            } else {
                storage_file_error(f_result);
                return;
            }
            break;

        case SET_LABEL:
            if (!bp_cmd_get_positional_string(&disk_label_def, 2, label_string, sizeof(label_string))) {
                printf("Missing label argument, please provide a name to set the label to\r\n");
                return;
            }
            if (strlen(label_string) > MAX_LABEL_LENGTH) {
                printf("label is too long, maximum label length is %d characters\r\n", MAX_LABEL_LENGTH);
                return;
            }
            f_result = f_setlabel(label_string);
            if (f_result != FR_OK) {
                storage_file_error(f_result);
                return;
            }
            break;

        default:
            printf("Invalid command: '%s'\r\n", command_string);
            return;
    }

    res->error = false;
    return;
}
