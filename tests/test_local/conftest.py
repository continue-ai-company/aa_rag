import importlib
import os
import re
import shutil
import sys
import tempfile
from typing import Literal

import pytest
from fastapi.testclient import TestClient


def backup_and_generate_env(env_type: Literal["Production", "Development"], backup_path: str) -> str:
    """Enhanced environment configuration updater with backup capability.

    Features:
    1. Updates existing configuration items (whether commented or not)
    2. Appends new configuration if it doesn't exist

    Args:
        env_type: Environment type to set, either Production or Development
        backup_path: Path to save backup of the original .env file

    Returns:
        Path to the backup file

    Raises:
        FileNotFoundError: If the original .env file is not found
    """
    env_file = ".env"

    if not os.path.exists(env_file):
        raise FileNotFoundError("未找到.env文件")

    # Create backup with original metadata
    shutil.copy2(env_file, backup_path)

    with open(env_file, "r") as f:
        original_content = f.read()

    # Update existing ENVIRONMENT configuration
    env_pattern = re.compile(r"^#?\s*ENVIRONMENT\s*=.*$", flags=re.MULTILINE)
    new_content, substitutions = env_pattern.subn(
        f"ENVIRONMENT={env_type}", original_content
    )

    # Add ENVIRONMENT if not found
    if substitutions == 0:
        # Ensure proper newline formatting
        if new_content and not new_content.endswith("\n"):
            new_content += "\n"
        new_content += f"ENVIRONMENT={env_type}\n"

    # Update DEBUG_MODE based on environment type
    debug_value = str(env_type == "DEV").lower()
    new_content = re.sub(
        r"^#?\s*DEBUG_MODE\s*=.*$",
        f"DEBUG_MODE={debug_value}",
        new_content,
        flags=re.MULTILINE,
    )

    with open(env_file, "w") as f:
        f.write(new_content)

    return backup_path


def restore_env(backup_path: str) -> bool:
    """Restore environment configuration from backup.

    Args:
        backup_path: Path to the backup file created by backup_and_generate_env

    Returns:
        bool: True if restoration succeeded, False otherwise

    Raises:
        FileNotFoundError: If the specified backup file doesn't exist
    """
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup file {backup_path} not found")

    try:
        # Preserve original file metadata during restoration
        shutil.copy2(backup_path, ".env")
        return True
    except Exception as e:
        print(f"Restoration failed: {str(e)}")
        return False


@pytest.fixture(scope="session")
def client():
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        backup_and_generate_env("Development", tmp_file.name)  # 备份当前并生成DEV环境配置
        if 'aa_rag.settings' in sys.modules:
            for module in [_ for _ in sys.modules if _.startswith('aa_rag')]:
                importlib.reload(sys.modules[module])
        from aa_rag.main import app
        client = TestClient(app)
        yield client
        restore_env(tmp_file.name)
        # delete storage dir
        storage_dir = os.path.join(os.getcwd(), "storage")
        if os.path.exists(storage_dir):
            shutil.rmtree(storage_dir)
