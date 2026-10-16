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
    """Manages indexing, searching, and chunk retrieval from the entire docs/ tree."""

    def __init__(self, docs_root: Path | str | None = None):
        base = (
            Path(docs_root)
            if docs_root
            else Path(__file__).resolve().parent.parent.parent.parent / "docs"
        )
        self.docs_root = base

    def _determine_section(self, file_path: Path) -> str:
        """Determines logical section name for a markdown file."""
        try:
            rel = file_path.relative_to(self.docs_root)
            parts = rel.parts
            if len(parts) >= 3 and parts[0] == "studio_knowledge":
                return parts[1]
            if len(parts) >= 2:
                return parts[0]
            return "general"
        except ValueError:
            return file_path.parent.name

    def list_sections(self) -> list[str]:
        """Lists all document sections (e.g. DevDocs, LiveAPIDocs, VideoProductionDocs, PublishingDocs, wiki, guidelines)."""
        if not self.docs_root.exists():
            return []
        sections = set()
        for md_file in self.docs_root.rglob("*.md"):
            sections.add(self._determine_section(md_file))
        return sorted(list(sections))

    def list_documents(self, section: str | None = None) -> list[dict[str, Any]]:
        """Lists metadata for all markdown documents in the knowledge base."""
        docs = []
        if not self.docs_root.exists():
            return docs

        sec_filter = section.lower().strip() if section else None

        for file_path in self.docs_root.rglob("*.md"):
            doc_section = self._determine_section(file_path)
            rel_str = str(file_path.relative_to(self.docs_root)).replace("\\", "/").lower()

            if sec_filter:
                # Match section name or directory substring
                if doc_section.lower() != sec_filter and sec_filter not in rel_str:
                    continue

            content = file_path.read_text(encoding="utf-8")
            first_line = content.splitlines()[0] if content.splitlines() else file_path.stem
            title = first_line.lstrip("#").strip() if first_line.startswith("#") else file_path.stem
            docs.append({
                "section": doc_section,
                "doc_name": file_path.stem,
                "title": title,
                "file_path": str(file_path),
                "relative_path": str(file_path.relative_to(self.docs_root)).replace("\\", "/"),
                "size_bytes": file_path.stat().st_size,
            })

        return sorted(docs, key=lambda x: (x["section"], x["doc_name"]))

    def get_document(self, doc_identifier: str) -> str | None:
        """Retrieves full text of a document by name, stem, or relative path."""
        if not self.docs_root.exists():
            return None

        clean_id = doc_identifier.replace("\\", "/").strip().lower()

        # 1. Direct or relative path attempt
        direct = self.docs_root / doc_identifier
        if direct.is_file():
            return direct.read_text(encoding="utf-8")

        if not doc_identifier.endswith(".md"):
            direct_md = self.docs_root / f"{doc_identifier}.md"
            if direct_md.is_file():
                return direct_md.read_text(encoding="utf-8")

        # 2. Search across all markdown files by relative path or stem
        for md_file in self.docs_root.rglob("*.md"):
            rel = str(md_file.relative_to(self.docs_root)).replace("\\", "/").lower()
            if rel == clean_id or rel == f"{clean_id}.md":
                return md_file.read_text(encoding="utf-8")
            if md_file.stem.lower() == clean_id or md_file.name.lower() == clean_id:
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
