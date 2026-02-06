import typer
from talos.cli.sophia import sophia_app

app = typer.Typer()
app.add_typer(sophia_app, name="sophia")

if __name__ == "__main__":
    app()
