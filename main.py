import argparse
import sys
import os

def main():
    # Force UTF-8 encoding for Windows consoles
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")

    """LazyLLMs - CLI entry point"""
    parser = argparse.ArgumentParser(description="LazyLLMs - Manage and Monitor AI Models")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # CLI Commands
    subparsers.add_parser("list", help="List running AI models")
    subparsers.add_parser("tui", help="Launch interactive terminal UI")

    args = parser.parse_args()

    if args.command == "list":
        from cli.commands import list_models
        list_models()
    elif args.command == "tui":
        from cli.tui import show_tui
        show_tui()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()