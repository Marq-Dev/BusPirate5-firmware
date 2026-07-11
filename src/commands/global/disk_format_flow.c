#include "commands/global/disk_format_flow.h"

static disk_format_deep_result_t result_with_status(
    disk_format_deep_status_t status) {
    return (disk_format_deep_result_t) {
        .status = status,
        .reset_stage = 0,
        .reset_status = 0,
        .fatfs_status = 0,
    };
}

static bool ops_are_complete(const disk_format_deep_ops_t *ops) {
    return ops && ops->eject_usb && ops->unmount_storage &&
           ops->reset_storage && ops->format_storage &&
           ops->mount_storage && ops->insert_usb;
}

disk_format_deep_result_t disk_format_deep_run(
    bool supported,
    const disk_format_deep_ops_t *ops) {
    if (!supported || !ops_are_complete(ops)) {
        return result_with_status(DISK_FORMAT_DEEP_UNSUPPORTED);
    }

    disk_format_deep_result_t result =
        result_with_status(DISK_FORMAT_DEEP_OK);

    ops->eject_usb();
    ops->unmount_storage();

    if (!ops->reset_storage(&result.reset_stage,
                            &result.reset_status)) {
        result.status = DISK_FORMAT_DEEP_RESET_FAILED;
        return result;
    }

    result.fatfs_status = ops->format_storage();
    if (result.fatfs_status != 0) {
        result.status = DISK_FORMAT_DEEP_FORMAT_FAILED;
        return result;
    }

    result.fatfs_status = ops->mount_storage();
    if (result.fatfs_status != 0) {
        result.status = DISK_FORMAT_DEEP_MOUNT_FAILED;
        return result;
    }

    ops->insert_usb();
    return result;
}
