"""API key storage utility for Streamlit session and local storage."""

import json
import os
from pathlib import Path
from typing import Optional

import streamlit as st

# Local storage file path
STORAGE_FILE = Path.home() / ".sora_video_generator" / "config.json"


class APIKeyStorage:
    """Handles API key storage in session state and local file."""

    @staticmethod
    def _ensure_storage_dir() -> None:
        """Ensure the storage directory exists."""
        STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def save_to_local(api_key: str) -> bool:
        """Save API key to local storage file.

        Args:
            api_key: The OpenAI API key to save.

        Returns:
            True if saved successfully, False otherwise.
        """
        try:
            APIKeyStorage._ensure_storage_dir()
            config = APIKeyStorage._load_config()
            config["api_key"] = api_key
            with open(STORAGE_FILE, "w") as f:
                json.dump(config, f)
            return True
        except Exception as e:
            st.error(f"Failed to save API key: {e}")
            return False

    @staticmethod
    def load_from_local() -> Optional[str]:
        """Load API key from local storage file.

        Returns:
            The stored API key or None if not found.
        """
        try:
            if STORAGE_FILE.exists():
                config = APIKeyStorage._load_config()
                return config.get("api_key")
        except Exception:
            pass
        return None

    @staticmethod
    def _load_config() -> dict:
        """Load configuration from local file.

        Returns:
            Configuration dictionary.
        """
        if STORAGE_FILE.exists():
            try:
                with open(STORAGE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    @staticmethod
    def clear_local() -> bool:
        """Clear API key from local storage.

        Returns:
            True if cleared successfully, False otherwise.
        """
        try:
            if STORAGE_FILE.exists():
                config = APIKeyStorage._load_config()
                config.pop("api_key", None)
                with open(STORAGE_FILE, "w") as f:
                    json.dump(config, f)
            return True
        except Exception as e:
            st.error(f"Failed to clear API key: {e}")
            return False

    @staticmethod
    def get_api_key() -> Optional[str]:
        """Get API key from session state or local storage.

        Priority: session state > local storage > environment variable

        Returns:
            The API key or None if not found.
        """
        # Check session state first
        if "api_key" in st.session_state and st.session_state.api_key:
            return st.session_state.api_key

        # Check local storage
        local_key = APIKeyStorage.load_from_local()
        if local_key:
            st.session_state.api_key = local_key
            return local_key

        # Check environment variable as fallback
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            st.session_state.api_key = env_key
            return env_key

        return None

    @staticmethod
    def set_api_key(api_key: str, save_locally: bool = False) -> None:
        """Set API key in session state and optionally save locally.

        Args:
            api_key: The OpenAI API key.
            save_locally: Whether to also save to local storage.
        """
        st.session_state.api_key = api_key
        if save_locally:
            APIKeyStorage.save_to_local(api_key)

    @staticmethod
    def is_api_key_set() -> bool:
        """Check if API key is available.

        Returns:
            True if API key is set, False otherwise.
        """
        return bool(APIKeyStorage.get_api_key())
