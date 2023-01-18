# Discord App Installer

### This script is a command line tool for installing the Discord app on Linux systems. It includes options for specifying the version of Discord to install, as well as options for uninstalling the app.

## Requirements
- Python ^3.6
- Sudo permission

## Usage

To use this script, download latest bin and make sure it has execute permissions. If it does not, run chmod +x <script-name>.

### Installation

To install the latest version of Discord, simply run the script with no arguments:

```bash
./discord_install
```

You can also specify a specific version to install by setting the DISCORD_VERSION environment variable:

```bash
export DISCORD_VERSION=0.0.24 && ./discord_install
```

### Uninstallation

To uninstall Discord, run the script with the `uninstall` flag:

```bash
sudo ./discord_install uninstall
```

## Disclaimer

This script is a only personal purpose. Use at your own risk.

## License

MIT
