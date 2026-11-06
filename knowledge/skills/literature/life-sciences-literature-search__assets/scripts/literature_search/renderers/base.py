"""Shared rendering options and localization helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..schema import OBJECT_COLLECTIONS


LANGUAGES = ("zh", "en", "bilingual")
CITATION_STYLES = ("vancouver", "nature", "ama")


@dataclass(frozen=True)
class RenderOptions:
    format: str = "table"
    language: str = "zh"
    citation_style: str = "vancouver"
    view: str | None = None
    include_abstract: bool = False

    def validate(self) -> None:
        if self.language not in LANGUAGES:
            raise ValueError(f"unsupported output language: {self.language}")
        if self.citation_style not in CITATION_STYLES:
            raise ValueError(f"unsupported citation style: {self.citation_style}")
        if self.format not in {"table", "review", "bibtex", "ris", "csl-json"}:
            raise ValueError(f"unsupported output format: {self.format}")
        if self.format in {"bibtex", "ris", "csl-json"} and self.view not in {
            None,
            "papers",
        }:
            raise ValueError("bibliography exports accept only the papers view")


MESSAGES: dict[str, dict[str, str]] = {
    "search_results": {"zh": "生命科学证据检索结果", "en": "Life-science evidence search"},
    "query": {"zh": "问题", "en": "Question"},
    "scope": {"zh": "检索范围", "en": "Search scope"},
    "bounded": {"zh": "有界检索，不代表系统综述", "en": "Bounded retrieval; not a systematic review"},
    "source_failures": {"zh": "失败或降级来源", "en": "Failed or degraded sources"},
    "retrieval_not_performed": {
        "zh": "检索尚未执行；以下仅为计划或空结果",
        "en": "Retrieval was not performed; this is only a plan or empty result",
    },
    "coverage_gaps": {
        "zh": "未成功执行的证据维度",
        "en": "Evidence dimensions not successfully executed",
    },
    "zero_result_dimensions": {
        "zh": "已执行但零结果的证据维度",
        "en": "Executed evidence dimensions with zero results",
    },
    "budget_limited_operations": {
        "zh": "因预算跳过的来源操作",
        "en": "Source operations skipped by budget",
    },
    "audit_detail": {
        "zh": "详情见审计 JSON",
        "en": "See the audit JSON for details",
    },
    "not_assessed": {"zh": "未评估", "en": "Not assessed"},
    "not_available": {"zh": "不可用", "en": "Unavailable"},
    "translation_missing_zh": {"zh": "中文译文不可用", "en": "Chinese translation unavailable"},
    "translation_missing_en": {"zh": "英文译文不可用", "en": "English translation unavailable"},
    "no_results": {"zh": "本次检索没有返回该类型对象。", "en": "No objects of this type were returned."},
    "review": {"zh": "证据综述", "en": "Evidence review"},
    "synthesis_not_generated": {
        "zh": "尚未生成证据综合；以下仅展示本次真实检索所得对象与书目信息。",
        "en": "No evidence synthesis was generated; only objects and bibliographic facts from this retrieval are shown.",
    },
    "reading_order": {"zh": "建议阅读顺序", "en": "Suggested reading order"},
    "research_groups": {"zh": "关键研究组", "en": "Key research groups"},
    "research_gaps": {"zh": "研究空白", "en": "Research gaps"},
    "not_provided": {"zh": "本次综合未提供。", "en": "Not provided by this synthesis."},
    "references": {"zh": "参考文献", "en": "References"},
    "model_background": {
        "zh": "模型背景知识（非本次检索证据）",
        "en": "Model background (not evidence from this retrieval)",
    },
    "limitations": {"zh": "局限性", "en": "Limitations"},
}


def message(key: str, language: str) -> str:
    values = MESSAGES[key]
    if language == "bilingual":
        return f"{values['zh']} / {values['en']}"
    return values[language]


def localized_text(value: Any, language: str, *, inline: bool = False) -> str:
    """Select existing localized text without translating it."""

    if isinstance(value, str):
        return value
    if not isinstance(value, Mapping):
        return ""
    zh = " ".join(str(value.get("zh") or "").split())
    en = " ".join(str(value.get("en") or "").split())
    if language == "zh":
        if zh:
            return zh
        return f"[{MESSAGES['translation_missing_zh']['zh']}] {en}" if en else ""
    if language == "en":
        if en:
            return en
        return f"[{MESSAGES['translation_missing_en']['en']}] {zh}" if zh else ""
    separator = "<br>" if inline else "\n\n"
    if zh and en:
        return f"{zh}{separator}{en}"
    if zh:
        return f"{zh}{separator}*{MESSAGES['translation_missing_en']['en']}*"
    if en:
        return f"*{MESSAGES['translation_missing_zh']['en']}*{separator}{en}"
    return ""


def object_index(bundle: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        object_["id"]: object_
        for collection in OBJECT_COLLECTIONS
        for object_ in bundle["objects"][collection]
    }


def select_result_set(
    bundle: Mapping[str, Any], view: str | None
) -> Mapping[str, Any] | None:
    result_sets = bundle.get("result_sets") or []
    if view:
        for result_set in result_sets:
            if result_set.get("id") == view or result_set.get("object_type") == view.removesuffix("s"):
                return result_set
        return None
    return result_sets[0] if result_sets else None
