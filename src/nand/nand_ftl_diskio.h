/**
 * @file		nand_ftl_diskio.h
 * @author		Andrew Loebs
 * @brief		Header file of the nand ftl diskio module
 *
 * Glue layer between fatfs diskio and dhara ftl.
 *
 */

#ifndef __NAND_FTL_DISKIO_H
#define __NAND_FTL_DISKIO_H

#include <stdbool.h>

// #include "../fatfs/diskio.h" // types from the diskio driver
// #include "../fatfs/ff.h"     // BYTE type

typedef enum {
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
DSTATUS diskio_status(BYTE drv);
DRESULT diskio_read(BYTE drv, BYTE* buff, LBA_t sector, UINT count);
DRESULT diskio_write(BYTE drv, const BYTE* buff, LBA_t sector, UINT count);
DRESULT diskio_ioctl(BYTE drv, BYTE cmd, void* buff);

#endif // __NAND_FTL_DISKIO_H
