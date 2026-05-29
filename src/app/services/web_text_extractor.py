import re
from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class ExtractedWebText:
    title: str | None
    text: str


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(
        self,
        tag: str,
        _attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag in {'script', 'style', 'noscript', 'svg'}:
            self._skip_depth += 1
        elif tag == 'title':
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {'script', 'style', 'noscript', 'svg'} and self._skip_depth:
            self._skip_depth -= 1
        elif tag == 'title':
            self._in_title = False
        elif tag in {'p', 'div', 'li', 'section', 'article', 'br', 'h1', 'h2', 'h3'}:
            self.parts.append('\n')

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        self.parts.append(text)

    @property
    def text(self) -> str:
        return _normalize_text(' '.join(self.parts))

    @property
    def title(self) -> str | None:
        title = _normalize_text(' '.join(self.title_parts))
        return title or None


def extract_web_text(html: str) -> ExtractedWebText | None:
    extractor = _TextExtractor()
    extractor.feed(html)
    if not extractor.text:
        return None
    return ExtractedWebText(title=extractor.title, text=extractor.text)


def split_text_into_chunks(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:
    """Split text with overlap so facts near chunk borders stay searchable."""
    if chunk_size <= 0:
        return []

    overlap = min(max(chunk_overlap, 0), chunk_size // 2)
    step = max(chunk_size - overlap, 1)
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + chunk_size].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def _normalize_text(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()
