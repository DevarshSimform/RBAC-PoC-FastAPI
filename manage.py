"""
Django-style management script for Alembic migrations and permission seeding

Usage:
    python manage.py makemigrations -m "migration message"
    python manage.py migrate
    python manage.py seed_permissions
    python manage.py help

Commands:
    makemigrations  - Create new migration (calls alembic revision --autogenerate)
    migrate         - Apply migrations and sync permissions (calls alembic upgrade head + seed_permissions.py)
    seed_permissions- Run permission seeding script only
    help            - Show this help message
"""

import argparse
import os  # nosec
import subprocess  # nosec
import sys  # nosec


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def print_colored(message, color=Colors.ENDC):
    """Print colored message"""
    print(f"{color}{message}{Colors.ENDC}")


def run_command(command, description, cwd=None):
    """Run a shell command and handle errors"""
    print_colored(f"🔧 {description}...", Colors.OKCYAN)
    print_colored(f"   Command: {' '.join(command)}", Colors.OKBLUE)

    try:
        result = subprocess.run(
            command, cwd=cwd, check=True, capture_output=True, text=True  # nosec B603
        )

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print_colored(result.stderr, Colors.WARNING)

        print_colored(f"✅ {description} completed successfully!", Colors.OKGREEN)
        return True

    except subprocess.CalledProcessError as e:
        print_colored(f"❌ {description} failed!", Colors.FAIL)
        print_colored(f"Exit code: {e.returncode}", Colors.FAIL)
        if e.stdout:
            print_colored("STDOUT:", Colors.WARNING)
            print(e.stdout)
        if e.stderr:
            print_colored("STDERR:", Colors.FAIL)
            print(e.stderr)
        return False
    except FileNotFoundError:
        print_colored(f"❌ Command not found: {command[0]}", Colors.FAIL)
        print_colored("Make sure Alembic is installed and in your PATH", Colors.WARNING)
        return False


def check_alembic_installed():
    """Check if Alembic is installed"""
    try:
        result = subprocess.run(
            ["alembic", "--version"],
            capture_output=True,
            text=True,
            check=True,  # nosec B607 B603
        )
        print_colored(f"✅ Alembic found: {result.stdout.strip()}", Colors.OKGREEN)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_colored("❌ Alembic not found!", Colors.FAIL)
        print_colored("Please install Alembic: pip install alembic", Colors.WARNING)
        return False


def check_project_structure():
    """Check if we're in the correct project structure"""
    required_files = ["seed_permissions.py", "migrations/env.py", "app/main.py", ".env"]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print_colored("❌ Invalid project structure!", Colors.FAIL)
        print_colored("Missing files/directories:", Colors.WARNING)
        for file_path in missing_files:
            print_colored(f"   - {file_path}", Colors.WARNING)
        return False

    print_colored("✅ Project structure verified", Colors.OKGREEN)
    return True


def makemigrations(message):
    """Create new migration using Alembic"""
    print_colored("🚀 Creating new migration...", Colors.HEADER)

    if not message:
        print_colored("❌ Migration message is required!", Colors.FAIL)
        print_colored(
            'Usage: python manage.py makemigrations -m "your message"', Colors.WARNING
        )
        return False

    command = ["alembic", "revision", "--autogenerate", "-m", message]
    return run_command(command, "Creating migration")


def migrate():
    """Apply migrations and sync permissions"""
    print_colored("🚀 Running migrations and syncing permissions...", Colors.HEADER)

    # Step 1: Apply migrations
    print_colored("\n" + "=" * 60, Colors.HEADER)
    print_colored("STEP 1: Applying database migrations", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)

    upgrade_command = ["alembic", "upgrade", "head"]
    if not run_command(upgrade_command, "Applying migrations"):
        return False

    # Step 2: Sync permissions
    print_colored("\n" + "=" * 60, Colors.HEADER)
    print_colored("STEP 2: Syncing permissions", Colors.HEADER)
    print_colored("=" * 60, Colors.HEADER)

    seed_command = [sys.executable, "seed_permissions.py"]
    if not run_command(seed_command, "Syncing permissions"):
        return False

    print_colored(
        "\n🎉 Migration and permission sync completed successfully!", Colors.OKGREEN
    )
    return True


def seed_permissions():
    """Run permission seeding script only"""
    print_colored("🚀 Running permission seeding...", Colors.HEADER)

    if not os.path.exists("seed_permissions.py"):
        print_colored("❌ seed_permissions.py not found!", Colors.FAIL)
        return False

    command = [sys.executable, "seed_permissions.py"]
    return run_command(command, "Running permission seeding")


def show_help():
    """Show help message"""
    print_colored("📚 Django-style Management Script for Alembic", Colors.HEADER)
    print_colored("=" * 50, Colors.HEADER)
    print()
    print_colored("Available Commands:", Colors.OKBLUE)
    print()
    print_colored("  makemigrations", Colors.OKGREEN)
    print("    Create new migration using Alembic")
    print_colored(
        '    Usage: python manage.py makemigrations -m "migration message"',
        Colors.OKCYAN,
    )
    print()
    print_colored("  migrate", Colors.OKGREEN)
    print("    Apply migrations and sync permissions")
    print_colored("    Usage: python manage.py migrate", Colors.OKCYAN)
    print()
    print_colored("  seed_permissions", Colors.OKGREEN)
    print("    Run permission seeding script only")
    print_colored("    Usage: python manage.py seed_permissions", Colors.OKCYAN)
    print()
    print_colored("  help", Colors.OKGREEN)
    print("    Show this help message")
    print_colored("    Usage: python manage.py help", Colors.OKCYAN)
    print()
    print_colored("Examples:", Colors.WARNING)
    print_colored(
        '  python manage.py makemigrations -m "add user table"', Colors.OKCYAN
    )
    print_colored("  python manage.py migrate", Colors.OKCYAN)
    print_colored("  python manage.py seed_permissions", Colors.OKCYAN)


def main():
    """Main function"""
    # Check if we're in the right directory
    if not check_project_structure():
        sys.exit(1)

    # Check if Alembic is installed
    if not check_alembic_installed():
        sys.exit(1)

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Django-style management script for Alembic migrations",
        add_help=False,  # We'll handle help ourselves
    )

    parser.add_argument("command", nargs="?", help="Command to run")
    parser.add_argument("-m", "--message", help="Migration message")
    parser.add_argument("-h", "--help", action="store_true", help="Show help")

    args = parser.parse_args()

    # Handle help
    if args.help or not args.command:
        show_help()
        sys.exit(0)

    # Handle commands
    if args.command == "makemigrations":
        success = makemigrations(args.message)
    elif args.command == "migrate":
        success = migrate()
    elif args.command == "seed_permissions":
        success = seed_permissions()
    elif args.command == "help":
        show_help()
        sys.exit(0)
    else:
        print_colored(f"❌ Unknown command: {args.command}", Colors.FAIL)
        print_colored(
            "Run 'python manage.py help' for available commands", Colors.WARNING
        )
        sys.exit(1)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
