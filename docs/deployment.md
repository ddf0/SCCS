# Deployment on Raspberry Pi 3B

End-to-end instructions for putting SCCS onto a clean Raspberry Pi 3B
and bringing it up under systemd.

## 1. Base OS

1. Flash **Raspberry Pi OS Lite (64-bit, bookworm)** to a microSD using
   Raspberry Pi Imager. In the imager's advanced options:
   - Set hostname `sccs`.
   - Enable SSH, set the username, paste an SSH public key.
   - Configure Wi-Fi if Ethernet is not available.
2. Boot, SSH in: `ssh pi@sccs.local`.
3. Update: `sudo apt update && sudo apt -y upgrade`.

## 2. Hardware enablement

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
sudo reboot
```

After reboot, check that the I²C bus appears:

```bash
i2cdetect -y 1
# expect the HCCD (0x10) and MMC5983MA (0x30) to show once wired
```

## 3. Software install

```bash
sudo apt -y install python3-pip git
sudo git clone https://github.com/ddf0/SCCS /opt/sccs
cd /opt/sccs
sudo pip install -e . --break-system-packages
```

The `--break-system-packages` flag is required on Debian 12 (PEP 668)
because we are deliberately installing into the system Python; a venv
would complicate the systemd unit for no real benefit on a
single-purpose device.

## 4. Configuration

Edit `/opt/sccs/config/default.yaml` if any of the addresses or PID
defaults differ for this board. Calibration results are written to
`/opt/sccs/config/calibration.yaml` and excluded from version control.

A non-default config can be passed via the systemd unit's `ExecStart`
line — copy `sccs.service` to a `.service.d/override.conf` rather
than editing the file in `/etc/systemd/system/`.

## 5. systemd

```bash
sudo cp deploy/sccs.service /etc/systemd/system/sccs.service
sudo systemctl daemon-reload
sudo systemctl enable --now sccs
```

Verify:

```bash
sudo systemctl status sccs           # active (running)
sudo journalctl -u sccs -f           # follow logs
```

## 6. Smoke test

From any device on the LAN:

```
http://sccs.local:8080
```

The Control tab should render with three graphs (initially at zero
when no HCCD is connected), the temperature row, and the three
gain sliders.

## 7. Sanity-check workflow (no hardware)

On a dev workstation:

```bash
python -m sccs.app --no-hw --validate
# OK — configuration valid, components constructed

python -m sccs.app --no-hw
# starts the server with mock drivers; visit http://localhost:8080
```

## 8. Troubleshooting

| Symptom | Probable cause | Fix |
| --- | --- | --- |
| `Permission denied: '/dev/i2c-1'` | User not in `i2c` group, or I²C not enabled. | `sudo usermod -aG i2c $USER` and `raspi-config`. |
| `OSError: [Errno 121] Remote I/O error` | HCCD not responding at 0x10. | Check wiring, then `i2cdetect -y 1`. |
| Service flapping in `journalctl` | Config validation error. | Run `python -m sccs.app --validate` to see the pydantic message. |
| Web UI loads but graphs are flat | Control loop never advanced. | `journalctl -u sccs` for tracebacks; verify magnetometer responds. |

## 9. Updating

```bash
cd /opt/sccs
sudo git pull
sudo pip install -e . --break-system-packages
sudo systemctl restart sccs
```
