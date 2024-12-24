import networkx as nx
import yaml
from enum import Enum
from typing import Sequence, Tuple, List, Dict
from marko import Markdown, MarkoExtension, block, inline, element
from marko.md_renderer import MarkdownRenderer
from copy import deepcopy


class Relationship(Enum):
    ALIAS = "alias"
    CHILDOF = "childof"
    LINKSTO = "linksto"


class WikiLink(inline.InlineElement):
    pattern = r"\[\[([^\]]+)\]\]"
    parse_children = True


class Tag(inline.InlineElement):
    pattern = r"#(\w+)"
    parse_children = True


class _WikiRendererMixin(object):
    def render_wiki_link(self, element):
        return "[[{}]]".format(element.children[0].children[0])


class _TagMixin(object):
    def render_tag(self, element):
        return "#{}".format(element.children[0].children[0])


_WIKILINK_EXT = MarkoExtension(elements=[Tag], renderer_mixins=[_TagMixin])

_WIKILINKEXT = MarkoExtension(elements=[WikiLink], renderer_mixins=[_WikiRendererMixin])

_PARSER = Markdown(extensions=[_WIKILINKEXT, _WIKILINK_EXT], renderer=MarkdownRenderer)


def _parse_front_matter(file_content: str) -> Tuple[Dict[str, List[str]], str]:
    front_matter, content = file_content.split("---\n", 2)[1:]
    metadata = yaml.safe_load(front_matter)
    aliases = []
    if "alias" in metadata:
        for alias in metadata["alias"].split(","):
            aliases.append(alias.strip())
        metadata["alias"] = aliases
    return metadata, content.strip()


def _render_element(element: inline.InlineElement | block.BlockElement) -> str:
    # No not render sublists
    element = deepcopy(element)
    new_children = []
    for child in list(element.children):
        if not isinstance(child, block.List):
            new_children.append(child)
    element.children = new_children

    # Actual rendering
    doc = block.Document()
    doc.children = [element]
    return _PARSER.render(doc).strip()


def _traverse_list_items(
    items: Sequence[element.Element], graph: nx.DiGraph, parent_node: str
) -> None:
    for item in items:
        # This is non-blocking, they should not be part of the if-else chain below this
        if isinstance(item, WikiLink):
            # Add a linksto relationship
            target = item.children[0]
            if isinstance(target, inline.InlineElement) or isinstance(
                target, block.BlockElement
            ):
                target = target.children[0]
                graph.add_edge(
                    parent_node, target, relationship=Relationship.LINKSTO.value
                )
            else:
                raise ValueError(
                    "WikiLink target must be an InlineElement or BlockElement"
                )
        elif isinstance(item, Tag):
            target = item.children[0]
            if isinstance(target, inline.InlineElement) or isinstance(
                target, block.BlockElement
            ):
                target = target.children[0]
                graph.add_edge(
                    parent_node, target, relationship=Relationship.LINKSTO.value
                )
            else:
                raise ValueError(
                    "WikiLink target must be an InlineElement or BlockElement"
                )
        # These call traverse_list_items recursively or render the child node
        if isinstance(item, block.List):
            # Recursively process nested lists, keeping the same parent
            _traverse_list_items(item.children, graph, parent_node)
        elif isinstance(item, block.ListItem):
            # Render the current item as a new node
            child_node = _render_element(item)

            # Avoid self-loops by checking that the child and parent are different
            if child_node != parent_node:
                graph.add_edge(
                    child_node, parent_node, relationship=Relationship.CHILDOF.value
                )

            # Recursively process child elements of this list item
            _traverse_list_items(item.children, graph, child_node)
        elif isinstance(item, block.Paragraph):
            # For non-list children, render and connect to the parent
            child_node = _render_element(item)

            # Avoid self-loops here as well
            if child_node != parent_node:
                graph.add_edge(
                    child_node, parent_node, relationship=Relationship.CHILDOF.value
                )

            # Recursively process child elements of this list item
            _traverse_list_items(item.children, graph, child_node)


def parse_markdown_to_graph(
    graph: nx.DiGraph, alias: str, file_content: str
) -> nx.DiGraph:
    # Parse YAML front matter
    metadata, content = _parse_front_matter(file_content)

    # Add alias relationships
    for alias in metadata.get("alias", []):
        graph.add_edge(alias, alias, relationship=Relationship.ALIAS.value)

    # Configure Markdown parser with custom extensions
    parsed = _PARSER.parse(content)

    # Traverse the parsed AST to process list items
    for elem in parsed.children:
        if isinstance(elem, block.List):
            _traverse_list_items(elem.children, graph, alias)
        else:
            raise ValueError("Only list items are supported in body after frontmatter")

    return graph
