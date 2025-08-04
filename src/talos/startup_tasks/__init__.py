"""
Startup tasks for Talos daemon.

This module contains startup tasks that are executed when the daemon starts.
Tasks are similar to database migrations - they run once and are tracked for completion.
"""

from .example_tasks import create_example_startup_tasks

__all__ = ["create_example_startup_tasks"]
