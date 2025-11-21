#!/usr/bin/env python3
import psutil
import sys
import os
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import box


def print_help(console: Console):
    help_text = """[bold cyan]pdsk-util[/bold cyan] - A beautiful disk usage viewer in python

[bold]Usage:[/bold]
  pdsk-util [OPTIONS] [VOLUME]

[bold]Arguments:[/bold]
  [cyan]VOLUME[/cyan]    Optional. Specific volume/mount point to check (e.g., C:\\ or /home)

[bold]Options:[/bold]
  [cyan]-h, --help[/cyan]    Show this help message and exit

[bold]Examples:[/bold]
  pdsk-util              Show all volumes
  pdsk-util C:\\          Show only C: drive (Windows)
  pdsk-util /home        Show only /home mount point (Linux/Mac)
"""
    console.print(help_text)

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

    for part in psutil.disk_partitions(all=False):
        norm_mountpoint = os.path.normpath(part.mountpoint)

        # If specific mount is requested, skip others
        if specific_mount:
            if specific_mount and norm_mountpoint.lower() != specific_mount.lower() and part.device != specific_mount:
                continue
        
        # Skip obvious noise
        if part.fstype in ('tmpfs', 'devtmpfs', 'squashfs', 'overlay', 'efivarfs', 'vfat'):
            continue
        if part.mountpoint.startswith(('/sys', '/proc', '/dev', '/run', '/snap')):
            continue

        try:
            usage = psutil.disk_usage(part.mountpoint)
            found_any = True
        except PermissionError:
            continue
        except OSError as e:
            continue

        total = usage.total // (1024**3)
        used  = usage.used  // (1024**3)
        free  = usage.free  // (1024**3)
        percent = usage.used / usage.total * 100 if usage.total > 0 else 0

        bar_length = 20
        filled = int(percent / 100 * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)

        color = "red" if percent >= 90 else "yellow" if percent >= 70 else "green"

        table.add_row(
            part.device or "—",
            part.fstype,
            f"{total}G",
            f"{used}G",
            f"{free}G",
            f"[{color}]{percent:5.1f}% {bar}[/{color}]",
            part.mountpoint
        )

    if found_any:
        console.print(table)
    else:
        console.print("[bold red]No readable filesystems found![/] Probably running with strict permissions.")
        console.print("Try running with sudo: [bold]sudo python3 pdsk_util.py[/]")

def main():
    console = Console()
    # Check for help flag
    if len(sys.argv) > 1 and sys.argv[1] in ('-h', '--help'):
        print_help(console)
        return
    # Check if a specific volume was provided as argument
    specific_mount = sys.argv[1] if len(sys.argv) > 1 else None
    if specific_mount:
        console.print(f"[dim]Checking volume: {specific_mount}[/dim]\n")

    print_disk_usage(console=console, specific_mount=specific_mount)

if __name__ == "__main__":
    main()