# Hardware Security Attacks - Setup and Execution Guide

This document provides step-by-step instructions to set up and execute various hardware security attack PoCs.

---

## 1. **Setup**
Below is a general outline of how you can disable KASLR and KPTI (by adding **nokaslr nopti** to the kernel’s command line) and then run your test program on a specific hyperthread.

---

### 1. Edit the Kernel Command Line

You will need to modify your bootloader’s configuration so that it passes the `nopti` and `nokaslr` parameters to the kernel on boot.

#### On systems with GRUB (typical for many Linux distros)

1. **Open** the GRUB configuration file (for example, on Ubuntu/Debian):

   ```bash
   sudo nano /etc/default/grub
   ```

2. **Find** the line that starts with `GRUB_CMDLINE_LINUX_DEFAULT`. It might look something like this (your actual parameters may vary):
   
   ```bash
   GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
   ```

3. **Add** `nopti nokaslr` to that line (you can keep other parameters as they are). For example:

   ```bash
   GRUB_CMDLINE_LINUX_DEFAULT="quiet splash nopti nokaslr"
   ```

4. **Save** the file and **update** GRUB. On Ubuntu/Debian:

   ```bash
   sudo update-grub
   ```

5. **Reboot** your system to apply the changes.

   ```bash
   sudo reboot
   ```

#### Verifying the Command Line Parameters

After reboot, you can verify that `nopti` and `nokaslr` took effect by running:

```bash
cat /proc/cmdline
```

You should see something similar to:

```
BOOT_IMAGE=/boot/vmlinuz-... root=UUID=... ro quiet splash nopti nokaslr ...
```
---

## 2. **Execute**
After following the instructions above, run in HardSec file the script:
```bash
./run.sh
```
and the application will execute with root privilages (needed for physical addresses).

### ⚠️ **Disclaimer**
These repositories contain proof-of-concept (PoC) code demonstrating vulnerabilities in hardware. Executing these attacks may be illegal depending on your jurisdiction. Use this guide for educational and research purposes only.