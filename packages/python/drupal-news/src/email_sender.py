"""Email sender for Drupal Newsletter."""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Optional
import os


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    mail_from: str,
    mail_to: str,
    subject: str,
    body: str,
    attachment_path: Optional[Path] = None,
    timeout: int = 30
) -> bool:
    """
    Send email with optional attachment.

    Args:
        smtp_host: SMTP server hostname
        smtp_port: SMTP port
        smtp_user: SMTP username
        smtp_pass: SMTP password
        mail_from: From address
        mail_to: To address
        subject: Email subject
        body: Email body
        attachment_path: Optional path to attachment file
        timeout: Connection timeout in seconds (default: 30)

    Returns:
        True if sent successfully, False otherwise
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = mail_from
        msg['To'] = mail_to
        msg['Subject'] = subject

        # Add body
        msg.attach(MIMEText(body, 'plain'))

        # Add attachment if provided
        if attachment_path and Path(attachment_path).exists():
            with open(attachment_path, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename={Path(attachment_path).name}'
                )
                msg.attach(part)

        # Connect and send with timeout
        with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)

        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"Email authentication failed: {e}")
        print("For Gmail, you need to use an App Password: https://support.google.com/accounts/answer/185833")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return False
    except TimeoutError as e:
        print(f"Email timeout after {timeout}s: {e}")
        return False
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False


def send_report(
    config: dict,
    env: dict,
    run_date: str,
    summary_path: Path,
    timezone: str,
    period_label: str = "News"
) -> bool:
    """
    Send Drupal report email.

    Args:
        config: Configuration dictionary
        env: Environment variables dictionary
        run_date: Run date string (YYYY-MM-DD)
        summary_path: Path to summary.md file
        timezone: Timezone name
        period_label: Period label (e.g., "News", "Binews")

    Returns:
        True if sent successfully
    """
    subject_prefix = config.get("email", {}).get("subject_prefix", f"[Drupal {period_label}]")
    subject = f"{subject_prefix} {run_date}"

    body = f"""
        Generation date: {run_date} ({timezone}).
        Agreegator period: {period_label}
    """

    # Get attachment path if enabled
    attachment = None
    if config.get("email", {}).get("attach_summary", True):
        # Check for attachment format preference (pdf or md)
        attachment_format = config.get("email", {}).get("attachment_format", "pdf")

        run_dir = summary_path.parent

        if attachment_format == "pdf":
            # Prefer PDF if it exists
            pdf_path = run_dir / "summary.pdf"
            if pdf_path.exists():
                attachment = pdf_path
            else:
                # Fall back to markdown if PDF doesn't exist
                attachment = summary_path
        else:
            # Use markdown
            attachment = summary_path

    # Get timeout from env or use default
    timeout = int(env.get("SMTP_TIMEOUT", 30))

    return send_email(
        smtp_host=env.get("SMTP_HOST"),
        smtp_port=int(env.get("SMTP_PORT", 587)),
        smtp_user=env.get("SMTP_USER"),
        smtp_pass=env.get("SMTP_PASS"),
        mail_from=env.get("MAIL_FROM"),
        mail_to=env.get("MAIL_TO"),
        subject=subject,
        body=body,
        attachment_path=attachment,
        timeout=timeout
    )


def write_email_log(
    output_path: Path,
    subject: str,
    body: str,
    mail_to: str,
    sent: bool,
    attachment: str = None
):
    """
    Write email log file.

    Args:
        output_path: Path to email.txt
        subject: Email subject
        body: Email body
        mail_to: Recipient address
        sent: Whether email was sent successfully
        attachment: Optional attachment filename
    """
    log_content = f"""Email Log
=========

Subject: {subject}
To: {mail_to}
Status: {"Sent" if sent else "Failed"}
"""

    if attachment:
        log_content += f"Attachment: {attachment}\n"

    log_content += f"""
Body:
{body}
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(log_content)


def get_current_version() -> str:
    """
    Get the current version from git tag.

    Returns:
        String with the current git tag version, or "unknown" if not available
    """
    import subprocess
    from pathlib import Path

    try:
        # Try to get the current git tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            if version.startswith('v'):
                return version[1:]  # Remove 'v' prefix if present
            return version
        else:
            # Fallback to checking the latest tag
            result = subprocess.run(
                ["git", "tag", "--sort=-version:refname"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent
            )
            if result.returncode == 0:
                tags = result.stdout.strip().split('\n')
                if tags and tags[0]:
                    version = tags[0]
                    if version.startswith('v'):
                        return version[1:]  # Remove 'v' prefix if present
                    return version
    except Exception:
        pass

    return "unknown"


def main():
    """Main entry point for drupal-news-email CLI."""
    import argparse
    from pathlib import Path

    parser = argparse.ArgumentParser(description='Send Drupal News email reports')
    parser.add_argument('--latest', action='store_true', help='Send latest report')
    parser.add_argument('--days', type=int, default=7, help='Days back to check (default: 7)')
    parser.add_argument('--run-dir', type=str, help='Specific run directory to send')
    parser.add_argument('--version', action='store_true', help='Show current version and exit')

    args = parser.parse_args()

    # Handle --version flag
    if args.version:
        print(f"drupal-news-email version {get_current_version()}")
        import sys
        sys.exit(0)
    
    print("Email sender CLI")
    print("=" * 60)
    
    # Load environment
    from dotenv import load_dotenv
    import os
    
    env_path = Path.home() / ".drupal-news" / ".env"
    if not env_path.exists():
        env_path = Path(".env")
    
    load_dotenv(env_path)
    env = os.environ
    
    # Determine run directory
    if args.run_dir:
        run_path = Path(args.run_dir)
    elif args.latest:
        runs_dir = Path("runs")
        if not runs_dir.exists():
            print("Error: runs/ directory not found")
            return 1
        
        # Find latest run
        run_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], reverse=True)
        if not run_dirs:
            print("Error: No runs found")
            return 1
        
        run_path = run_dirs[0]
    else:
        print("Error: Specify --latest or --run-dir")
        return 1
    
    print(f"Using run: {run_path}")
    
    # Check for summary
    summary_path = run_path / "summary.md"
    if not summary_path.exists():
        print(f"Error: {summary_path} not found")
        return 1
    
    # Send email
    print("\nSending email...")
    result = send_report(
        run_dir=run_path,
        env=env,
        days=args.days
    )
    
    if result:
        print("✓ Email sent successfully")
        return 0
    else:
        print("✗ Email failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
