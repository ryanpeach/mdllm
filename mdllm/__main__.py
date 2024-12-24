from typing import Annotated
import typer
from typer_config import use_toml_config
from mdllm.logseq import path_to_alias
from mdllm.markdown import parse_markdown_to_graph
from pathlib import Path
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
from tqdm import tqdm
from typer import Argument, Option

app = typer.Typer()


@app.command()
@use_toml_config()
def main(
    dirs: Annotated[list[Path], Argument(help="List of directories to parse")],
    save_graph: Annotated[
        Path | None, Option("-o", help="Output a dot file of the graph used in RAG")
    ] = None,
):
    graph = nx.DiGraph()

    # Flatten all the `.md` paths into a single list for better progress bar
    all_md_files = [path for dir in dirs for path in dir.rglob("*.md")]

    for path in tqdm(all_md_files, desc="Parsing Markdown Files"):
        alias = path_to_alias(path)
        file_content = path.read_text()
        parse_markdown_to_graph(alias=alias, graph=graph, file_content=file_content)

    if save_graph:
        print(f"Saving graph to {save_graph}")
        write_dot(graph, save_graph)


if __name__ == "__main__":
    app()
