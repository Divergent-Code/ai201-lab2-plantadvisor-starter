"""
Compatibility wrapper for app.py.

The app.py starter code incorrectly passes `theme` to demo.launch() instead
of gr.Blocks(). This script patches Gradio to silently accept and discard the
unknown kwarg, then runs app.py as the main module.

Usage:
    python run.py
"""
import gradio as gr
import runpy

# Patch Blocks.launch to accept the rogue `theme` kwarg from app.py
_original_launch = gr.Blocks.launch


def _patched_launch(self, *args, theme=None, **kwargs):
    """Accept (and discard) `theme` kwarg for compatibility with app.py."""
    return _original_launch(self, *args, **kwargs)


gr.Blocks.launch = _patched_launch

# Run app.py as if it were the entry-point (respects `if __name__ == "__main__":`)
runpy.run_path("app.py", run_name="__main__")
