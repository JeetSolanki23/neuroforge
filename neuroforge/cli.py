from __future__ import annotations

import typer

from neuroforge.config import config

app = typer.Typer(name="neuroforge", help="NeuroForge AI Software Company")


@app.command()
def run(goal: str = typer.Argument(..., help="Goal for the AI team to build")):
    """Run NeuroForge with a goal."""
    typer.echo(f"NeuroForge starting — goal: {goal}")
    typer.echo("System not yet fully implemented. Phase 1 foundation complete.")


@app.command()
def health():
    """Check system health (config, ChromaDB, LLM provider)."""
    from neuroforge.memory.chroma import health_check

    ok = health_check()
    typer.echo(f"ChromaDB: {'✓' if ok else '✗'}")
    typer.echo(f"Provider: {config.NEUROFORGE_PROVIDER}")
    typer.echo(f"Model: {config.NEUROFORGE_MODEL}")


if __name__ == "__main__":
    app()
