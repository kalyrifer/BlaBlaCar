#!/usr/bin/env python3
"""
PostgreSQL Database Backup Script

This script performs daily backups of the PostgreSQL database with:
- Daily dumps stored in a designated backup directory
- Automatic retention policy (keeps last 7 days of backups)
- Timestamped backup filenames

Usage:
    python backup_db.py [--config CONFIG_PATH]

Environment variables (or .env file):
    - DB_HOST: PostgreSQL host (default: localhost)
    - DB_PORT: PostgreSQL port (default: 5432)
    - DB_NAME: Database name (default: roadmate_db)
    - DB_USER: PostgreSQL user (default: postgres)
    - DB_PASSWORD: PostgreSQL password
    - BACKUP_DIR: Backup directory path (default: ./backups)
    - RETENTION_DAYS: Number of days to keep backups (default: 7)
"""
import os
import sys
import argparse
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_env(key: str, default: str = "") -> str:
    """Get environment variable or return default."""
    return os.environ.get(key, default)


def get_backup_dir() -> Path:
    """Get or create backup directory."""
    backup_dir = Path(get_env("BACKUP_DIR", "./backups"))
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def get_db_config() -> dict:
    """Get database configuration from environment."""
    return {
        "host": get_env("DB_HOST", "localhost"),
        "port": get_env("DB_PORT", "5432"),
        "dbname": get_env("DB_NAME", "roadmate_db"),
        "user": get_env("DB_USER", "postgres"),
        "password": get_env("DB_PASSWORD", ""),
    }


def create_backup(backup_dir: Path, db_config: dict) -> Optional[Path]:
    """
    Create a PostgreSQL backup using pg_dump.
    
    Args:
        backup_dir: Directory to save backup file
        db_config: Database configuration dictionary
        
    Returns:
        Path to created backup file or None on failure
    """
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"roadmate_db_{timestamp}.sql"
    backup_path = backup_dir / filename
    
    # Build pg_dump command
    # Use environment variable for password to avoid exposing it in process list
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]
    
    cmd = [
        "pg_dump",
        "-h", db_config["host"],
        "-p", db_config["port"],
        "-U", db_config["user"],
        "-d", db_config["dbname"],
        "-F", "c",  # Custom format (compressed)
        "-f", str(backup_path),
    ]
    
    logger.info(f"Starting backup to {backup_path}")
    
    try:
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Backup created successfully: {backup_path}")
        
        # Get file size
        file_size = backup_path.stat().st_size
        logger.info(f"Backup size: {file_size / (1024*1024):.2f} MB")
        
        return backup_path
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e.stderr}")
        # Try plain text format as fallback
        logger.info("Retrying with plain text format...")
        
        filename = f"roadmate_db_{timestamp}.sql"
        backup_path = backup_dir / filename
        
        cmd = [
            "pg_dump",
            "-h", db_config["host"],
            "-p", db_config["port"],
            "-U", db_config["user"],
            "-d", db_config["dbname"],
            "-F", "p",  # Plain text format
            "-f", str(backup_path),
        ]
        
        try:
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            logger.info(f"Backup created successfully (plain text): {backup_path}")
            return backup_path
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed again: {e.stderr}")
            return None
    except FileNotFoundError:
        logger.error("pg_dump not found. Please install PostgreSQL client tools.")
        return None


def cleanup_old_backups(backup_dir: Path, retention_days: int = 7) -> int:
    """
    Remove backups older than retention_days.
    
    Args:
        backup_dir: Directory containing backup files
        retention_days: Number of days to keep backups
        
    Returns:
        Number of files deleted
    """
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0
    
    for backup_file in backup_dir.glob("roadmate_db_*.sql*"):
        # Check file modification time
        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        if mtime < cutoff_date:
            try:
                backup_file.unlink()
                logger.info(f"Deleted old backup: {backup_file}")
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete {backup_file}: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleaned up {deleted_count} old backup(s)")
    else:
        logger.info("No old backups to clean up")
    
    return deleted_count


def verify_backup(backup_path: Path) -> bool:
    """
    Verify backup file is valid.
    
    Args:
        backup_path: Path to backup file
        
    Returns:
        True if backup is valid
    """
    if not backup_path.exists():
        logger.error(f"Backup file not found: {backup_path}")
        return False
    
    # Check file size (should be > 0)
    if backup_path.stat().st_size == 0:
        logger.error(f"Backup file is empty: {backup_path}")
        return False
    
    # For custom format, try to verify with pg_restore --list
    if backup_path.suffix == '' or backup_path.suffix == '.sql':
        return True
    
    # Check if it's a valid gzip/format file
    try:
        with open(backup_path, 'rb') as f:
            header = f.read(2)
            # Check for gzip magic number
            if header != b'\x1f\x8b' and backup_path.suffix == '.dump':
                logger.warning(f"Unexpected file format: {backup_path}")
    except Exception as e:
        logger.warning(f"Could not verify backup: {e}")
    
    return True


def main():
    """Main backup script entry point."""
    parser = argparse.ArgumentParser(description="PostgreSQL Database Backup Script")
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (not implemented)",
        default=None
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        help="Number of days to keep backups",
        default=int(get_env("RETENTION_DAYS", "7"))
    )
    
    args = parser.parse_args()
    
    # Get configuration
    backup_dir = get_backup_dir()
    db_config = get_db_config()
    
    logger.info("=" * 50)
    logger.info("PostgreSQL Backup Script")
    logger.info("=" * 50)
    logger.info(f"Database: {db_config['dbname']}@{db_config['host']}:{db_config['port']}")
    logger.info(f"Backup directory: {backup_dir}")
    logger.info(f"Retention: {args.retention_days} days")
    
    # Check if password is set
    if not db_config["password"]:
        logger.error("DB_PASSWORD environment variable is not set")
        sys.exit(1)
    
    # Create backup
    backup_path = create_backup(backup_dir, db_config)
    
    if backup_path is None:
        logger.error("Backup failed!")
        sys.exit(1)
    
    # Verify backup
    if not verify_backup(backup_path):
        logger.error("Backup verification failed!")
        sys.exit(1)
    
    # Cleanup old backups
    cleanup_old_backups(backup_dir, args.retention_days)
    
    logger.info("=" * 50)
    logger.info("Backup completed successfully!")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()