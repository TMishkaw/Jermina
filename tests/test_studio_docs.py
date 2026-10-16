"""Unit tests for Jemini Studio MCP Docs Engine (JeminiStudioMCPDocs)."""

import pytest

from jemini.mcp.studio_docs import StudioDocsEngine


def test_studio_docs_list_sections():
    engine = StudioDocsEngine()
    sections = engine.list_sections()

    assert "DevDocs" in sections
    assert "LiveAPIDocs" in sections
    assert "VideoProductionDocs" in sections
    assert "PublishingDocs" in sections


def test_studio_docs_list_documents():
    engine = StudioDocsEngine()
    docs = engine.list_documents()

    assert len(docs) == 27
    doc_names = {d["doc_name"] for d in docs}
    assert "ApiReference" in doc_names
    assert "DatabaseKnowledgeBase" in doc_names
    assert "StickmanKinematics" in doc_names
    assert "MotionLibraryPgvector" in doc_names
    assert "RemotionHardwareGPU" in doc_names
    assert "WebSocketStreaming" in doc_names
    assert "ConstraintsAndGotchas" in doc_names
    assert "VisualBlindAudit" in doc_names
    assert "GoldenActingStandard" in doc_names
    assert "VoiceArchetypes" in doc_names
    assert "ShortsKineticLayout" in doc_names
    assert "YouTubeSemanticCategories" in doc_names
    assert "ZeroLeakSanitization" in doc_names
    assert "git_flow" in doc_names
    assert "architecture_audit_checklist" in doc_names

    # Test section filtering
    wiki_docs = engine.list_documents(section="wiki")
    assert len(wiki_docs) == 11
    assert all(d["section"] == "wiki" for d in wiki_docs)

    dev_docs = engine.list_documents(section="DevDocs")
    assert len(dev_docs) == 5
    assert all(d["section"] == "DevDocs" for d in dev_docs)


def test_studio_docs_search():
    engine = StudioDocsEngine()

    # Search for WebSocket close code 1007
    hits = engine.search_docs("WebSocket 1007")
    assert len(hits) > 0
    top_hit = hits[0]
    assert "ConstraintsAndGotchas" in top_hit.doc_name or "WebSocketStreaming" in top_hit.doc_name
    assert top_hit.relevance_score > 0

    # Search for Stickman joint angles
    hits_angles = engine.search_docs("Stickman angles kinematics")
    assert len(hits_angles) > 0
    assert hits_angles[0].doc_name == "StickmanKinematics"


def test_studio_docs_get_document():
    engine = StudioDocsEngine()

    doc_content = engine.get_document("StickmanKinematics")
    assert doc_content is not None
    assert "Coordinate Geometry & Angle Standards" in doc_content
    assert "Symmetrical Two-Handed Poses" in doc_content

    # Non-existent doc returns None
    missing = engine.get_document("NonExistentDocXYZ")
    assert missing is None
