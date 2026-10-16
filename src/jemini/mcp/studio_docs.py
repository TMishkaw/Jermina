"""Jemini Studio MCP Docs Engine & Knowledge Navigator.

Provides structured, low-latency search and retrieval across Studio architectural
specifications, Live API protocols, kinematic standards, and publishing guidelines.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DocSearchResult:
    """Search hit in Studio documentation."""
    section: str
    doc_name: str
    file_path: Path
    title: str
    snippet: str
    relevance_score: float


class StudioDocsEngine:
    """Manages indexing, searching, and chunk retrieval from docs/studio_knowledge/."""

    def __init__(self, docs_root: Path | str | None = None):
        base = (
            Path(docs_root)
            if docs_root
            else Path(__file__).resolve().parent.parent.parent.parent / "docs" / "studio_knowledge"
        )
        self.docs_root = base

    def list_sections(self) -> list[str]:
        """Lists all document sections (e.g. DevDocs, LiveAPIDocs, VideoProductionDocs, PublishingDocs)."""
        if not self.docs_root.exists():
            return []
        return sorted([d.name for d in self.docs_root.iterdir() if d.is_dir()])

    def list_documents(self, section: str | None = None) -> list[dict[str, Any]]:
        """Lists metadata for all markdown documents in the knowledge base."""
        docs = []
        if not self.docs_root.exists():
            return docs

        target_dirs = (
            [self.docs_root / section]
            if section and (self.docs_root / section).is_dir()
            else [d for d in self.docs_root.iterdir() if d.is_dir()]
        )

        for s_dir in target_dirs:
            sec_name = s_dir.name
            for file_path in s_dir.glob("*.md"):
                content = file_path.read_text(encoding="utf-8")
                first_line = content.splitlines()[0] if content.splitlines() else file_path.stem
                title = first_line.lstrip("#").strip() if first_line.startswith("#") else file_path.stem
                docs.append({
                    "section": sec_name,
                    "doc_name": file_path.stem,
                    "title": title,
                    "file_path": str(file_path),
                    "size_bytes": file_path.stat().st_size,
                })

        return sorted(docs, key=lambda x: (x["section"], x["doc_name"]))

    def get_document(self, doc_identifier: str) -> str | None:
        """Retrieves full text of a document by name, stem, or relative path."""
        if not self.docs_root.exists():
            return None

        # 1. Direct path attempt
        direct = self.docs_root / doc_identifier
        if direct.is_file():
            return direct.read_text(encoding="utf-8")

        # 2. Append .md if omitted
        if not doc_identifier.endswith(".md"):
            direct_md = self.docs_root / f"{doc_identifier}.md"
            if direct_md.is_file():
                return direct_md.read_text(encoding="utf-8")

        # 3. Search across all sections
        clean_name = Path(doc_identifier).stem.lower()
        for md_file in self.docs_root.rglob("*.md"):
            if md_file.stem.lower() == clean_name:
                return md_file.read_text(encoding="utf-8")

        return None

    def search_docs(self, query: str, section: str | None = None) -> list[DocSearchResult]:
        """Performs token-based relevance search across studio documents."""
        tokens = [t.lower().strip() for t in query.split() if len(t.strip()) > 1]
        results: list[DocSearchResult] = []

        all_docs = self.list_documents(section=section)
        for doc_meta in all_docs:
            f_path = Path(doc_meta["file_path"])
            content = f_path.read_text(encoding="utf-8")
            lower_content = content.lower()

            match_count = 0
            for token in tokens:
                if token in lower_content:
                    match_count += lower_content.count(token)

            if match_count > 0:
                # Extract first relevant paragraph snippet
                snippet = ""
                paragraphs = content.split("\n\n")
                for p in paragraphs:
                    if any(t in p.lower() for t in tokens):
                        snippet = p.strip()[:240].replace("\n", " ") + "..."
                        break
                if not snippet:
                    snippet = content[:200].replace("\n", " ") + "..."

                score = float(match_count) * (2.0 if any(t in doc_meta["title"].lower() for t in tokens) else 1.0)
                results.append(DocSearchResult(
                    section=doc_meta["section"],
                    doc_name=doc_meta["doc_name"],
                    file_path=f_path,
                    title=doc_meta["title"],
                    snippet=snippet,
                    relevance_score=score,
                ))

        return sorted(results, key=lambda x: x.relevance_score, reverse=True)
