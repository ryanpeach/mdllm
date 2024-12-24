import pytest
from mdllm.markdown import parse_markdown_to_graph, Relationship

file_content = """---
alias: a, b, c
---

- asdf [[a]]
  - lorem ipsum #b
"""


# Pytest tests
@pytest.mark.parametrize(
    "edge, expected_relationship",
    [
        (("a", "foo"), Relationship.ALIAS.value),
        (("b", "foo"), Relationship.ALIAS.value),
        (("c", "foo"), Relationship.ALIAS.value),
        (("lorem ipsum #b", "asdf [[a]]"), Relationship.CHILDOF.value),
        (("lorem ipsum #b", "b"), Relationship.LINKSTO.value),
        (("asdf [[a]]", "a"), Relationship.LINKSTO.value),
    ],
)
def test_graph_structure(edge: tuple[str, str], expected_relationship: str) -> None:
    graph = parse_markdown_to_graph("foo", file_content)
    source, target = edge
    assert graph.has_edge(source, target), graph[source]
    assert (
        rel := graph.edges[source, target]["relationship"]
    ) == expected_relationship, rel
