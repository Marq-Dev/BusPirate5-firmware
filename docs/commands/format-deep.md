# Deep-format NAND storage

`format` rebuilds the FAT filesystem through the current logical storage map.
It is appropriate when the NAND translation layer is healthy.

`format --deep` is a destructive recovery operation for NAND-backed Bus Pirate
models. It:

1. ejects the USB storage medium;
2. erases every usable physical NAND block while preserving factory bad-block markers;
3. creates fresh Dhara flash-translation state;
4. creates and mounts a new FAT filesystem; and
5. restores the USB storage medium.

Commands:

```text
format
format -y
format --deep
format --deep -y
```

`format --deep` asks for two confirmations. `format --deep -y` skips both.
All files, scripts, captures, and saved configuration on internal NAND are
permanently destroyed.

Deep format is unavailable on TF/microSD-backed models. If raw NAND erase fails,
the firmware leaves storage ejected and does not attempt FAT formatting over a
partially erased device. FAT creation or remount failure also leaves the medium
ejected and unavailable.
