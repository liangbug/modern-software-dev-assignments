"""Builds minimal arXiv Atom XML feeds so tests never touch the network."""

from __future__ import annotations

ATOM_NS = 'xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom"'


def make_entry(
    arxiv_id: str = "2301.00001v1",
    title: str = "Sample Paper Title",
    summary: str = "This is the abstract.",
    authors: tuple[str, ...] = ("Jane Doe", "John Smith"),
    published: str = "2023-01-01T00:00:00Z",
    updated: str = "2023-01-02T00:00:00Z",
    primary_category: str = "cs.AI",
    categories: tuple[str, ...] = ("cs.AI", "cs.LG"),
    comment: str | None = None,
    journal_ref: str | None = None,
    doi: str | None = None,
) -> str:
    author_xml = "".join(f"<author><name>{a}</name></author>" for a in authors)
    category_xml = "".join(
        f'<category term="{c}" scheme="http://arxiv.org/schemas/atom"/>' for c in categories
    )
    extra = ""
    if comment is not None:
        extra += f"<arxiv:comment>{comment}</arxiv:comment>"
    if journal_ref is not None:
        extra += f"<arxiv:journal_ref>{journal_ref}</arxiv:journal_ref>"
    if doi is not None:
        extra += f"<arxiv:doi>{doi}</arxiv:doi>"

    return f"""
    <entry>
      <id>http://arxiv.org/abs/{arxiv_id}</id>
      <updated>{updated}</updated>
      <published>{published}</published>
      <title>{title}</title>
      <summary>{summary}</summary>
      {author_xml}
      <arxiv:primary_category term="{primary_category}" scheme="http://arxiv.org/schemas/atom"/>
      {category_xml}
      <link href="http://arxiv.org/abs/{arxiv_id}" rel="alternate" type="text/html"/>
      <link title="pdf" href="http://arxiv.org/pdf/{arxiv_id}" rel="related" type="application/pdf"/>
      {extra}
    </entry>
    """


def make_error_entry(arxiv_id: str, reason: str) -> str:
    return f"""
    <entry>
      <id>http://arxiv.org/api/errors#incorrect_id_format_for_{arxiv_id}</id>
      <title>Error</title>
      <summary>{reason}</summary>
    </entry>
    """


def make_feed(entries: list[str] = ()) -> bytes:
    body = "".join(entries)
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
    <feed {ATOM_NS}>
      <title>ArXiv Query</title>
      {body}
    </feed>
    """
    return xml.encode("utf-8")
