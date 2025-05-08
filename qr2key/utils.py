"""Utility functions for QR2Key."""

import platform


def get_platform_info():
    """Get platform information.
    
    Returns:
        dict: Platform information
    """
    return {
        'system': platform.system(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'is_windows': platform.system() == 'Windows',
    }
