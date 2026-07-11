#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "commands/global/disk_format_flow.h"

static char calls[32];
static size_t calls_len;
static bool reset_ok;
static uint8_t format_status;
static uint8_t mount_status;
static int reset_stage;
static int reset_status;

static void push(char c) {
    calls[calls_len++] = c;
    calls[calls_len] = '\0';
}

static void fake_eject(void) { push('E'); }
static void fake_unmount(void) { push('U'); }
static bool fake_reset(int *stage, int *status) {
    push('R');
    *stage = reset_stage;
    *status = reset_status;
    return reset_ok;
}
static uint8_t fake_format(void) { push('F'); return format_status; }
static uint8_t fake_mount(void) { push('M'); return mount_status; }
static void fake_insert(void) { push('I'); }

static const disk_format_deep_ops_t ops = {
    .eject_usb = fake_eject,
    .unmount_storage = fake_unmount,
    .reset_storage = fake_reset,
    .format_storage = fake_format,
    .mount_storage = fake_mount,
    .insert_usb = fake_insert,
};

static void reset_fakes(void) {
    memset(calls, 0, sizeof(calls));
    calls_len = 0;
    reset_ok = true;
    format_status = 0;
    mount_status = 0;
    reset_stage = 0;
    reset_status = 0;
}

int main(void) {
    reset_fakes();
    disk_format_deep_result_t r = disk_format_deep_run(false, &ops);
    assert(r.status == DISK_FORMAT_DEEP_UNSUPPORTED);
    assert(strcmp(calls, "") == 0);

    reset_fakes();
    r = disk_format_deep_run(true, NULL);
    assert(r.status == DISK_FORMAT_DEEP_UNSUPPORTED);
    assert(strcmp(calls, "") == 0);

    reset_fakes();
    reset_ok = false;
    reset_stage = 2;
    reset_status = -9;
    r = disk_format_deep_run(true, &ops);
    assert(r.status == DISK_FORMAT_DEEP_RESET_FAILED);
    assert(r.reset_stage == 2);
    assert(r.reset_status == -9);
    assert(strcmp(calls, "EUR") == 0);

    reset_fakes();
    format_status = 14;
    r = disk_format_deep_run(true, &ops);
    assert(r.status == DISK_FORMAT_DEEP_FORMAT_FAILED);
    assert(r.fatfs_status == 14);
    assert(strcmp(calls, "EURF") == 0);

    reset_fakes();
    mount_status = 13;
    r = disk_format_deep_run(true, &ops);
    assert(r.status == DISK_FORMAT_DEEP_MOUNT_FAILED);
    assert(r.fatfs_status == 13);
    assert(strcmp(calls, "EURFM") == 0);

    reset_fakes();
    r = disk_format_deep_run(true, &ops);
    assert(r.status == DISK_FORMAT_DEEP_OK);
    assert(strcmp(calls, "EURFMI") == 0);

    return 0;
}
