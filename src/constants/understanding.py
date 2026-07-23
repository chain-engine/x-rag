# -*- coding: utf-8 -*-
"""
Understanding Constants Module

查询理解阶段相关的常量：意图类型枚举、实体类型枚举、
意图/实体识别模式、停用词表。
"""

from typing import Final

from .base import BaseEnum


# ====================================
# 意图类型枚举
# ====================================

class IntentType(BaseEnum):
    """查询意图类型枚举"""
    FACTUAL = "factual", "事实型"
    OPINION = "opinion", "观点型"
    LIST = "list", "列表型"
    DEFINITION = "definition", "定义型"
    COMPARISON = "comparison", "比较型"
    CAUSAL = "causal", "因果型"
    HOWTO = "howto", "操作型"
    UNKNOWN = "unknown", "未知"


# ====================================
# 实体类型枚举
# ====================================

class EntityType(BaseEnum):
    """实体类型枚举"""
    PERSON = "PERSON", "人名"
    LOCATION = "LOCATION", "地名"
    ORGANIZATION = "ORG", "组织/公司"
    TIME = "TIME", "时间表达式"
    NUMBER = "NUMBER", "数字/金额"
    TECH = "TECH", "技术术语"
    PRODUCT = "PRODUCT", "产品名"
    UNKNOWN = "UNKNOWN", "未知"


# ====================================
# 意图识别模式
# ====================================

# (正则模式, 权重)
_IntentPattern = tuple[str, float]

INTENT_PATTERNS: Final[dict[IntentType, list[_IntentPattern]]] = {
    IntentType.FACTUAL: [
        (r"(谁|什么时间|何时|哪一年|哪个|何处|什么)", 0.8),
        (r"(出生|死亡|创立|成立|发明|发现|建于)", 0.6),
        (r"\d{4}年", 0.4),
    ],
    IntentType.OPINION: [
        (r"(觉得|认为|评价|看法|观点|意见|感觉|好不好)", 0.9),
        (r"(优缺点|优势|劣势|值得)", 0.7),
    ],
    IntentType.LIST: [
        (r"(列出|列举|有哪些|包括什么|罗列)", 0.9),
        (r"(组成部分|要素|因素|步骤|流程|特点)", 0.6),
    ],
    IntentType.DEFINITION: [
        (r"(什么是|什么叫|定义|含义|解释一下)", 0.9),
        (r"(是指|指的是|即)", 0.7),
    ],
    IntentType.COMPARISON: [
        (r"(区别|差异|不同|比较|对比)", 0.9),
        (r"(和.*哪个好|.*vs.*|.* versus .*)", 0.8),
        (r"(比.*更好|比.*优秀)", 0.6),
    ],
    IntentType.CAUSAL: [
        (r"(为什么|原因|由于|因为)", 0.9),
        (r"(导致|结果|因此|所以|致使)", 0.7),
    ],
    IntentType.HOWTO: [
        (r"(如何|怎么|怎样|如何实现|如何做)", 0.9),
        (r"(步骤|方法|教程|指南)", 0.5),
    ],
}

# 默认最低置信度
DEFAULT_INTENT_MIN_CONFIDENCE: Final[float] = 0.3


# ====================================
# 实体抽取模式
# ====================================

ENTITY_PATTERNS: Final[dict[EntityType, list[str]]] = {
    EntityType.TIME: [
        r"\d{4}年\d{1,2}月\d{1,2}日",
        r"\d{4}年\d{1,2}月",
        r"\d{4}年",
        r"(去年|今年|明年|上周|下周|今天|明天|昨天|本周|下月)",
        r"第[一二三四五六七八九十百千万\d]+[天周月年]",
        r"(世纪|年代)",
    ],
    EntityType.NUMBER: [
        r"\d+\.?\d*%",
        r"\d+\.?\d*元",
        r"\d+\.?\d*[万千百亿]|\d+\.?\d*亿",
        r"\d+",
    ],
    EntityType.LOCATION: [
        r"[A-Z\u4e00-\u9fa5]+(?:省|市|区|县|州|国)",
        r"(中国|美国|英国|德国|法国|日本|韩国|俄罗斯)",
    ],
}


# ====================================
# 停用词表
# ====================================

DEFAULT_QUERY_STOPWORDS: Final[set[str]] = {
    "的", "了", "在", "是", "我", "有", "和", "就",
    "不", "人", "都", "一", "一个", "上", "也", "很",
    "到", "说", "要", "去", "你", "会", "着", "没有",
    "看", "好", "自己", "这",
}


__all__ = [
    "IntentType",
    "EntityType",
    "INTENT_PATTERNS",
    "ENTITY_PATTERNS",
    "DEFAULT_INTENT_MIN_CONFIDENCE",
    "DEFAULT_QUERY_STOPWORDS",
]
