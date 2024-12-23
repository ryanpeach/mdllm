import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree

HASH_WIKILINK_RE = r"(\s|^)\#\[\[([^\]]+)\]\]"


class HashWikiLinkInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("a")
        tag = m.group(2).strip()
        el.set("href", f"/tags/{tag}/")
        el.set("class", "tag")
        el.text = f"#[[{tag}]]"
        return el, m.start(0), m.end(0)


class HashWikiLinkExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        hash_wikilink_pattern = HashWikiLinkInlineProcessor(HASH_WIKILINK_RE, md)
        md.inlinePatterns.register(hash_wikilink_pattern, "hash_wikilink", 175)


TAG_RE = r"(\s|^)#(\w+)\b"


class TagInlineProcessor(InlineProcessor):
    def handleMatch(self, m, data):
        el = etree.Element("a")
        tag = m.group(2)
        el.set("href", f"/tags/{tag}/")
        el.set("class", "tag")
        el.text = f"#{tag}"
        return el, m.start(0), m.end(0)


class TagExtension(markdown.extensions.Extension):
    def extendMarkdown(self, md):
        tag_pattern = TagInlineProcessor(TAG_RE, md)
        md.inlinePatterns.register(tag_pattern, "tag", 175)


MD = markdown.Markdown(
    extensions=[WikiLinkExtension(), TagExtension(), HashWikiLinkExtension()]
)
