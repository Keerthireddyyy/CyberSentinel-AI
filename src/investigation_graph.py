
"""
CyberSentinel AI
LangGraph Investigation Workflow

Version 2:
Rule-based evidence analysis and local knowledge retrieval.
"""

from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from src.investigation_engine import build_investigation
from src.semantic_retriever import retrieve_semantic_knowledge
from src.llm_investigator import generate_llm_assessment


class InvestigationState(TypedDict):
    alert: Dict[str, Any]
    findings: List[Dict[str, str]]
    knowledge: List[Dict[str, Any]]
    assessment: str
    report: Dict[str, Any]


# Node 1: Analyze behavioral evidence
def evidence_analysis_node(state: InvestigationState):
    findings = build_investigation(state["alert"])

    return {"findings": findings}


# Node 2: Retrieve cybersecurity knowledge

def knowledge_retrieval_node(state: InvestigationState):
    findings = state["findings"]

    query = " ".join(
        (
            finding["category"].replace("_", " ")
            + ". "
            + finding["observation"]
            + " "
            + finding["interpretation"]
        )
        for finding in findings
    )

    if not query.strip():
        return {"knowledge": []}

    knowledge = retrieve_semantic_knowledge(
        query,
        top_k=3
    )

    return {"knowledge": knowledge}


# Node 3: Produce a cautious assessment
def assessment_node(state: InvestigationState):
    findings = state["findings"]
    knowledge = state["knowledge"]

    if findings:
        assessment = (
            f"{len(findings)} behavioral observations "
            "require analyst review. "
            f"{len(knowledge)} knowledge sections were retrieved "
            "for additional context. "
            "These findings do not confirm malicious activity."
        )
    else:
        assessment = (
            "No investigation rules were triggered. "
            "The ML anomaly still requires contextual review."
        )

    return {"assessment": assessment}


# Node 4: Generate investigation report
def report_generation_node(state: InvestigationState):
    alert = state["alert"]

    report = {
        "alert_id": alert["alert_id"],
        "source_computer": alert["source_computer"],
        "dataset_day": alert["dataset_day"],
        "severity": alert["severity"],
        "anomaly_score": alert["anomaly_score"],
        "investigation_type": "LANGGRAPH_KNOWLEDGE_AUGMENTED",
        "findings_count": len(state["findings"]),
        "findings": state["findings"],
        "knowledge_count": len(state["knowledge"]),
        "retrieved_knowledge": state["knowledge"],
        "assessment": state["assessment"]
    }

    return {"report": report}



# LLM-powered cybersecurity assessment
def llm_analysis_node(state: InvestigationState):
    assessment = generate_llm_assessment(
        alert=state["alert"],
        findings=state["findings"],
        knowledge=state["knowledge"]
    )
    return {"assessment": assessment}


# Build the workflow
workflow = StateGraph(InvestigationState)

workflow.add_node("evidence_analysis", evidence_analysis_node)
workflow.add_node("knowledge_retrieval", knowledge_retrieval_node)
workflow.add_node("assessment", assessment_node)
workflow.add_node("llm_analysis", llm_analysis_node)
workflow.add_node("report_generation", report_generation_node)

workflow.add_edge(START, "evidence_analysis")
workflow.add_edge("evidence_analysis", "knowledge_retrieval")
workflow.add_edge("knowledge_retrieval", "assessment")
workflow.add_edge("assessment", "llm_analysis")
workflow.add_edge("llm_analysis", "report_generation")
workflow.add_edge("report_generation", END)

investigation_graph = workflow.compile()
