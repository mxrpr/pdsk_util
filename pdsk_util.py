#!/usr/bin/env python3
import argparse
import psutil
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box

__version__ = "0.0.1"

def format_size(num_bytes: int) -> str:
    """Return a human-readable size string, auto-selecting B/K/M/G/T units."""
    for unit in ('B', 'K', 'M', 'G', 'T'):
        if abs(num_bytes) < 1024 or unit == 'T':
            if unit == 'B':
                return f"{num_bytes}{unit}"
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024


def print_disk_usage(console: Console, specific_mount=None):
    table = Table(
        title=f"df -h • {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        box=box.MINIMAL_DOUBLE_HEAD,
        header_style="bold magenta"
    )

    table.add_column("Filesystem", style="bold cyan")
    table.add_column("Type", style="dim")
    table.add_column("Size", justify="right")
    table.add_column("Used", justify="right")
    table.add_column("Avail", justify="right")
    table.add_column("Use%", justify="right")
    table.add_column("Mounted on", style="green")

    found_any = False
    # Normalize the specific_mount path if provided
    if specific_mount:
        specific_mount = os.path.normpath(specific_mount)

    try:
        partitions = psutil.disk_partitions(all=False)
    except OSError as e:
        console.print(f"[bold red]Error:[/] Could not enumerate disk partitions: {e}")
        return

    partitions = sorted(partitions, key=lambda p: p.mountpoint)

    for part in partitions:
        norm_mountpoint = os.path.normpath(part.mountpoint)

        if specific_mount:
            # When a specific mount is requested, skip everything that doesn't match;
            # noise filters are intentionally bypassed so vfat/tmpfs//run mounts work.
            if norm_mountpoint.lower() != specific_mount.lower() and part.device != specific_mount:
                continue
        else:
            # Skip obvious noise when showing all mounts
            if part.fstype in ('tmpfs', 'devtmpfs', 'squashfs', 'overlay', 'efivarfs'):
                continue
            # Linux pseudo-fs paths; on Windows mountpoints start with drive letters
            # so this startswith check is already a no-op there — intentional.
            if part.mountpoint.startswith(('/sys', '/proc', '/dev', '/run', '/snap')):
                continue

        try:
            usage = psutil.disk_usage(part.mountpoint)
            found_any = True
        except PermissionError:
            continue
        except OSError:
            continue

        total = format_size(usage.total)
        used  = format_size(usage.used)
        free  = format_size(usage.free)
        percent = usage.used / usage.total * 100 if usage.total > 0 else 0

        bar_length = 20
        filled = int(percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        color = "red" if percent >= 90 else "yellow" if percent >= 70 else "green"

        table.add_row(
            part.device or "—",
            part.fstype,
            total,
            used,
            free,
            f"[{color}]{percent:5.1f}% {bar}[/{color}]",
            part.mountpoint
        )

    if found_any:
        console.print(table)
    elif specific_mount:
        console.print(f"[bold red]No readable filesystems found:[/] requested mount '[bold]{specific_mount}[/]' not found.")
    else:
        console.print("[bold red]No readable filesystems found![/] Probably running with strict permissions.")
        console.print("Try running with sudo: [bold]sudo python3 pdsk_util.py[/]")

def main():
    parser = argparse.ArgumentParser(
        prog="pdsk-util",
        description="pdsk-util - A beautiful disk usage viewer in python",
        epilog=(
            "Examples:\n"
            "  pdsk-util              Show all volumes\n"
            "  pdsk-util C:\\          Show only C: drive (Windows)\n"
            "  pdsk-util /home        Show only /home mount point (Linux/Mac)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "volume",
        nargs="?",
        default=None,
        metavar="VOLUME",
        help="Optional volume/mount point to check (e.g. C:\\ or /home)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    console = Console()
    specific_mount = args.volume
    if specific_mount:
        console.print(f"[dim]Checking volume: {specific_mount}[/dim]\n")

    try:
        print_disk_usage(console=console, specific_mount=specific_mount)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/] {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()