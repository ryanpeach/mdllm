import typer
from typer_config import use_toml_config

app = typer.Typer()


@app.command()
@use_toml_config()  # MUST BE AFTER @app.command()
def main():
    raise NotImplementedError("This function is not implemented yet.")


if __name__ == "__main__":
    app()
