#pragma once

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    DISK_FORMAT_DEEP_OK = 0,
    DISK_FORMAT_DEEP_UNSUPPORTED,
    DISK_FORMAT_DEEP_RESET_FAILED,
    DISK_FORMAT_DEEP_FORMAT_FAILED,
    DISK_FORMAT_DEEP_MOUNT_FAILED,
} disk_format_deep_status_t;

typedef struct {
    void (*eject_usb)(void);
    void (*unmount_storage)(void);
    bool (*reset_storage)(int *stage, int *status);
    uint8_t (*format_storage)(void);
    uint8_t (*mount_storage)(void);
    void (*insert_usb)(void);
} disk_format_deep_ops_t;

typedef struct {
    disk_format_deep_status_t status;
    int reset_stage;
    int reset_status;
    uint8_t fatfs_status;
} disk_format_deep_result_t;

disk_format_deep_result_t disk_format_deep_run(
    bool supported,
    const disk_format_deep_ops_t *ops);
