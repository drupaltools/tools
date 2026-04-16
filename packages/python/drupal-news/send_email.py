#!/usr/bin/env python3
"""
Send email from an existing run without re-running the pipeline.

Usage:
    ./send_email.py 2025-10-25
    ./send_email.py 2025-10-25 --to another@email.com
    ./send_email.py --latest
"""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
import os

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from email_sender import send_report, write_email_log
from utils.io_safe import safe_read_json
from pdf_generator import generate_summary_pdf
from utils.timebox import get_period_label


def find_latest_run(runs_root: Path) -> Path:
    """Find the most recent run directory."""
    run_dirs = sorted(runs_root.glob("*"), reverse=True)
    for run_dir in run_dirs:
        if run_dir.is_dir() and (run_dir / "summary.md").exists():
            return run_dir
    return None


def main():
    parser = argparse.ArgumentParser(description="Send email from existing run")
    parser.add_argument("date", nargs="?", help="Run date (YYYY-MM-DD) or --latest")
    parser.add_argument("--latest", action="store_true", help="Use latest run")
    parser.add_argument("--to", help="Override recipient email")
    parser.add_argument("--days", type=int, default=7, help="Timeframe days (for label)")
    parser.add_argument("--config", default="config.yml", help="Config file path")
    parser.add_argument("--env", default=".env", help="Environment file path")
    parser.add_argument("--runs-dir", default="./runs", help="Runs directory")

    args = parser.parse_args()

    # Load environment
    load_dotenv(args.env)

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"Error: Config file not found: {args.config}")
        sys.exit(1)

    config = safe_read_json(config_path)
    if not config:
        print(f"Error: Could not load config from {args.config}")
        sys.exit(1)

    # Get run directory
    runs_root = Path(args.runs_dir)

    if args.latest or args.date == "--latest":
        run_dir = find_latest_run(runs_root)
        if not run_dir:
            print(f"Error: No runs found in {runs_root}")
            sys.exit(1)
        run_date = run_dir.name
    else:
        if not args.date:
            print("Error: Please specify a date or use --latest")
            parser.print_help()
            sys.exit(1)

        run_date = args.date
        run_dir = runs_root / run_date

    # Check if run exists
    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        print(f"\nAvailable runs:")
        for d in sorted(runs_root.glob("*"), reverse=True)[:10]:
            if d.is_dir():
                print(f"  - {d.name}")
        sys.exit(1)

    summary_path = run_dir / "summary.md"
    if not summary_path.exists():
        print(f"Error: Summary file not found: {summary_path}")
        sys.exit(1)

    print(f"Using run: {run_date}")
    print(f"Summary: {summary_path}")

    # Get period label
    period_label = get_period_label(args.days)

    # Check if PDF exists, generate if needed and configured
    pdf_path = run_dir / "summary.pdf"
    attachment_format = config.get("email", {}).get("attachment_format", "pdf")

    if attachment_format == "pdf" and not pdf_path.exists():
        print(f"PDF not found, generating...")
        pdf_path = generate_summary_pdf(run_dir, period_label=period_label)
        if pdf_path:
            print(f"✓ PDF generated: {pdf_path.name}")
        else:
            print(f"✗ PDF generation failed, will send markdown instead")

    # Build env dict
    env = {
        "TIMEZONE": os.getenv("TIMEZONE", "Europe/Athens"),
        "SMTP_HOST": os.getenv("SMTP_HOST"),
        "SMTP_PORT": os.getenv("SMTP_PORT", "587"),
        "SMTP_TIMEOUT": os.getenv("SMTP_TIMEOUT", "30"),
        "SMTP_USER": os.getenv("SMTP_USER"),
        "SMTP_PASS": os.getenv("SMTP_PASS"),
        "MAIL_TO": args.to or os.getenv("MAIL_TO"),
        "MAIL_FROM": os.getenv("MAIL_FROM"),
    }

    # Validate SMTP config
    missing = [k for k in ["SMTP_HOST", "SMTP_USER", "SMTP_PASS", "MAIL_TO", "MAIL_FROM"]
               if not env.get(k)]
    if missing:
        print(f"Error: Missing SMTP configuration: {', '.join(missing)}")
        print(f"Please check your {args.env} file")
        sys.exit(1)

    print(f"Sending email to: {env['MAIL_TO']}")
    print(f"Period: {period_label}")

    # Send email
    email_sent = send_report(
        config=config,
        env=env,
        run_date=run_date,
        summary_path=summary_path,
        timezone=env["TIMEZONE"],
        period_label=period_label
    )

    if email_sent:
        print(f"✓ Email sent successfully!")

        # Write email log
        attachment_name = pdf_path.name if pdf_path and pdf_path.exists() else "summary.md"
        write_email_log(
            run_dir / "email.txt",
            f"{config['email']['subject_prefix']} {run_date}",
            f"Drupal {period_label} for {run_date}",
            env["MAIL_TO"],
            email_sent,
            attachment_name
        )

        sys.exit(0)
    else:
        print(f"✗ Email sending failed")
        print(f"\nTroubleshooting:")
        print(f"1. Check your SMTP credentials in {args.env}")
        print(f"2. For Gmail, use an App Password: https://support.google.com/accounts/answer/185833")
        print(f"3. Check SMTP_HOST and SMTP_PORT settings")
        print(f"4. Try increasing SMTP_TIMEOUT if connection is slow")
        sys.exit(1)


if __name__ == "__main__":
    main()
