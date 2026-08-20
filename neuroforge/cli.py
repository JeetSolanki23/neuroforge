from __future__ import annotations

import typer

from neuroforge.config import config

app = typer.Typer(name="neuroforge", help="NeuroForge AI Software Company")


def _ensure_initialized() -> bool:
    """Checks if system is initialized. If not, seeds bootstrap agents.

    Returns True if ready to proceed, False if init failed.
    """
    from neuroforge.agents.registry import is_initialized, seed_bootstrap_agents

    if not is_initialized():
        typer.echo("First run detected — initializing NeuroForge...")
        count = seed_bootstrap_agents()
        if count == 0:
            typer.echo("Initialization failed. Check your config and try again.")
            return False
        typer.echo(f"NeuroForge initialized. {count} bootstrap agents seeded.")
    return True


@app.command()
def run(goal: str = typer.Argument(..., help="Goal for the AI team to build")):
    """Run NeuroForge with a goal."""
    if not _ensure_initialized():
        raise typer.Exit(1)
    typer.echo(f"NeuroForge starting — goal: {goal}")
    typer.echo("Orchestration layer not yet implemented (Phase 3).")


@app.command()
def init(
    force: bool = typer.Option(
        False, "--force", help="Re-seed even if already initialized"
    )
):
    """Initialize NeuroForge — seeds bootstrap agents to registry."""
    from neuroforge.agents.registry import is_initialized, seed_bootstrap_agents

    if is_initialized() and not force:
        typer.echo("Already initialized. Use --force to re-seed.")
        return
    typer.echo("Seeding bootstrap agents...")
    count = seed_bootstrap_agents()
    typer.echo(f"Done. {count} agents seeded to registry and vault.")


@app.command()
def health():
    """Check system health (ChromaDB, LLM provider, registry)."""
    from neuroforge.agents.registry import is_initialized
    from neuroforge.memory.chroma import health_check

    db_ok = health_check()
    reg_ok = is_initialized()
    typer.echo(f"ChromaDB:    {'✓' if db_ok else '✗'}")
    typer.echo(
        f"Registry:    {'✓ initialized' if reg_ok else '✗ not initialized'}"
    )
    typer.echo(f"Provider:    {config.NEUROFORGE_PROVIDER}")
    typer.echo(f"Model:       {config.NEUROFORGE_MODEL}")


if __name__ == "__main__":
    app()
