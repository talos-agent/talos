"""
Startup tasks directory - individual task files with hash-based names.

Each task file follows the pattern:
- Filename: {hash}.py (e.g., ec68f0115789.py)
- Contains a create_task() function that returns a StartupTask instance
- Self-contained and easily manageable like Django migrations

Tasks are automatically discovered by StartupTaskManager on daemon startup.
"""
