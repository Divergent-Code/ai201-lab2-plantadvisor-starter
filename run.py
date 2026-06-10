"""
Compatibility wrapper for app.py.

The app.py starter code incorrectly passes `theme` to demo.launch() instead
of gr.Blocks(). This script patches Gradio to silently accept and discard the
unknown kwarg, then runs app.py as the main module.

Usage:
    python run.py
"""
import os
import gradio as gr
import runpy

# Patch Blocks.__init__ to inject custom CSS and theme
_original_init = gr.Blocks.__init__

def _patched_init(self, *args, **kwargs):
    # Load custom CSS
    css_path = os.path.join(os.path.dirname(__file__), "custom_style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            custom_css = f.read()
        existing_css = kwargs.get("css", "")
        kwargs["css"] = (existing_css + "\n" + custom_css) if existing_css else custom_css
    
    # Inject Custom Theme (Organic Editorial)
    kwargs["theme"] = gr.themes.Base(
        primary_hue="emerald",
        neutral_hue="stone",
        font=[gr.themes.GoogleFont("Outfit"), "sans-serif"],
    )
    
    _original_init(self, *args, **kwargs)

gr.Blocks.__init__ = _patched_init

# Patch Blocks.launch to accept the rogue `theme` kwarg from app.py
_original_launch = gr.Blocks.launch


def _patched_launch(self, *args, theme=None, **kwargs):
    """Accept (and discard) `theme` kwarg for compatibility with app.py."""
    return _original_launch(self, *args, **kwargs)


gr.Blocks.launch = _patched_launch

# Run app.py as if it were the entry-point (respects `if __name__ == "__main__":`)
runpy.run_path("app.py", run_name="__main__")
