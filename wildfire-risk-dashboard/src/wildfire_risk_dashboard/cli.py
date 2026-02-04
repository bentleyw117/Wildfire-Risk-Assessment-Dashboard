"""Console script for wildfire_risk_dashboard."""

import typer
from rich.console import Console

from wildfire_risk_dashboard import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for wildfire_risk_dashboard."""
    console.print("Replace this message by putting your code into "
               "wildfire_risk_dashboard.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
