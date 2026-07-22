# x-rag 检索流水线文档

本文档详细描述 x-rag 项目中三阶段检索流水线的设计、算法原理和使用方法。

## 目录

- [概述](#概述)
- [架构设计](#架构设计)
- [Stage 1: 查询理解](#stage-1-查询理解)
- [Stage 2: 候选召回](#stage-2-候选召回)
- [Stage 3: 排序筛选](#stage-3-排序筛选)
- [使用指南](#使用指南)
- [自定义 Provider](#自定义-provider)

---

## 概述

检索是 RAG（检索增强生成）系统的核心组件。x-rag 实现了一个**三阶段检索流水线**，采用可插拔的 Provider 架构，支持灵活配置和扩展。

### 设计目标

1. **模块化**：每个阶段职责单一，可独立测试和替换
2. **可扩展**：通过 Provider 机制支持多种算法
3. **可配置**：运行时动态调整策略参数
4. **高性能**：支持批量处理和并行执行

---

## 架构设计

### 流水线架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户查询 (Query)                               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 1: 查询理解 (Query Understanding)                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │QueryRewrite │  │QueryExpand │  │   HyDE     │  │SubqueryDecomp│   │
│  │ (并行执行)   │  │ (并行执行)   │  │ (并行执行)   │  │ (并行执行)   │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                      │                                     │
│                                      ▼ merge()                              │
│                      ┌───────────────────────────────────────┐             │
│                      │   QueryUnderstandingResult            │             │
│                      │  • processed_query (处理后的查询)    │             │
│                      │  • sub_queries (子查询列表)          │             │
│                      │  • expanded_terms (扩展词)           │             │
│                      │  • hypothetical_doc (假设文档)        │             │
│                      └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 2: 候选召回 (Candidate Retrieval)                                    │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐           │
│  │ ChromaVectorRetrieval      │  │   BM25KeywordRetrieval    │           │
│  │    (向量 ANN 检索)         │  │    (关键词 BM25 检索)      │           │
│  └─────────────────────────────┘  └─────────────────────────────┘           │
│                                      │                                     │
│                                      ▼ dedup()                             │
│                      ┌───────────────────────────────────────┐             │
│                      │   候选文档集合 (去重合并)            │             │
│                      └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Stage 3: 排序筛选 (Ranking & Filtering)                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │MMRReranker │→ │RRFReranker │→ │Semantic    │→ │ScoreFilter │   │
│  │ (多样性)    │  │ (排名融合)  │  │Reranker   │  │ (阈值过滤)  │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                      │                                     │
│                                      ▼                                     │
│                      ┌───────────────────────────────────────┐             │
│                      │   最终 Top-K 检索结果               │             │
│                      └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              增强 → 生成                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 代码结构

```
retrieval/
├── pipeline.py              # 流水线编排器
├── understanding/
│   ├── base.py             # 查询理解抽象基类
│   ├── rewrite.py          # 查询重写
│   ├── expansion.py        # 查询扩展
│   ├── hyde.py            # HyDE 假设文档
│   └── subquery.py        # 子查询分解
├── candidate/
│   ├── base.py            # 候选召回抽象基类
│   ├── vector_retrieval.py # 向量检索
│   └── keyword_retrieval.py # BM25 检索
└── ranking/
    ├── base.py            # 排序抽象基类
    ├── mmr.py             # MMR 多样性重排
    ├── rrf.py             # RRF 排名融合
    ├── semantic.py         # 语义重排
    └── score_filter.py    # 阈值过滤
```

---

## Stage 1: 查询理解

### 设计理念

查询理解是检索系统的"大脑"，负责将用户的原始查询转换为更精确、更丰富的检索表达。

### 查询理解结果

```python
@dataclass
class QueryUnderstandingResult:
    original_query: str          # 原始查询
    processed_query: str          # 处理后的查询
    intent: str | None           # 查询意图
    sub_queries: list[str]       # 子查询列表
    hypothetical_doc: str | None  # HyDE 假设文档
    expanded_terms: list[str]     # 扩展词列表
    metadata: dict[str, Any]      # 附加元数据
```

### 提供的 Provider

#### 1. SimpleQueryRewriter (简单查询重写)

基于规则的重写，无需 LLM 调用：

```python
class SimpleQueryRewriter(BaseQueryUnderstandingProvider):
    name = "simple_rewrite"

    def process(self, query, context=None):
        # 规则处理：
        # 1. 去除停用词
        # 2. 修正拼写（可选）
        # 3. 规范化表达
        return QueryUnderstandingResult(...)
```

#### 2. LLMQueryRewriter (LLM 查询重写)

使用 LLM 进行语义级别的重写：

```python
class LLMQueryRewriter(BaseQueryUnderstandingProvider):
    name = "llm_rewrite"

    def process(self, query, context=None):
        # 1. 识别查询意图
        # 2. 扩展查询表达
        # 3. 生成多个检索查询
        return QueryUnderstandingResult(...)
```

#### 3. SynonymExpander (同义词扩展)

基于同义词词典扩展查询词：

```python
class SynonymExpander(BaseQueryUnderstandingProvider):
    name = "synonym_expander"

    def process(self, query, context=None):
        # 1. 分词
        # 2. 查找同义词
        # 3. 生成扩展查询
        return QueryUnderstandingResult(
            expanded_terms=["RAG", "检索增强", "retrieval-augmented"]
        )
```

#### 4. EmbeddingExpander (向量扩展)

使用 Embedding 模型查找语义相似的词：

```python
class EmbeddingExpander(BaseQueryUnderstandingProvider):
    name = "embedding_expander"

    def process(self, query, context=None):
        # 1. 查询词向量化
        # 2. 在词向量空间中找相似词
        # 3. 扩展查询
        return QueryUnderstandingResult(...)
```

#### 5. HyDE (假设文档)

生成假设性答案/文档，用于检索：

```python
class HyDEProvider(BaseQueryUnderstandingProvider):
    name = "hyde"

    def process(self, query, context=None):
        # 1. 让 LLM 生成假设性答案
        # 2. 用假设答案进行检索
        return QueryUnderstandingResult(
            hypothetical_doc="RAG 是一种结合检索和生成的技术..."
        )
```

#### 6. SubqueryDecomposer (子查询分解)

将复杂查询分解为简单子查询：

```python
class SubqueryDecomposer(BaseQueryUnderstandingProvider):
    name = "subquery_decomposer"

    def process(self, query, context=None):
        # 1. 分析查询结构
        # 2. 识别子主题
        # 3. 生成独立子查询
        return QueryUnderstandingResult(
            sub_queries=[
                "RAG 的定义是什么",
                "RAG 有哪些应用场景",
                "RAG 如何实现"
            ]
        )
```

### 结果合并

并行执行多个 Provider 后，使用 `merge()` 方法合并结果：

```python
merged = result1.merge(result2)
# processed_query: 取最长的（信息量最丰富）
# sub_queries: 并集去重
# expanded_terms: 并集去重
# hypothetical_doc: 用换行合并
```

---

## Stage 2: 候选召回

### 设计理念

候选召回是检索系统的"引擎"，负责从向量数据库和索引中快速召回候选文档。

### 向量检索原理

```
查询向量 ──ANN 索引──→ Top-K 最近邻
                        │
                        ├── 优点：语义相似度高
                        └── 缺点：可能遗漏字面相关
```

### 提供的 Provider

#### 1. ChromaVectorRetrieval (向量检索)

基于 Chroma 的 ANN 检索：

```python
class ChromaVectorRetrieval(BaseRetrievalProvider):
    name = "chroma_vector"

    def search(self, query, top_k=10, **kwargs):
        # 1. 查询向量化
        embedding = self.embedding_model.encode_single(query)

        # 2. ANN 检索
        results = self.vector_store.search(
            query_embedding=embedding,
            top_k=top_k,
            where=kwargs.get("metadata_filter")
        )

        return results
```

**支持的度量方式**：
- `cosine`: 余弦相似度
- `euclidean`: 欧氏距离
- `dot`: 点积

#### 2. BM25KeywordRetrieval (关键词检索)

基于 BM25 的传统关键词检索：

```python
class BM25KeywordRetrieval(BaseRetrievalProvider):
    name = "bm25_keyword"

    def __init__(self, k1=1.5, b=0.75):
        self._k1 = k1
        self._b = b

    def search(self, query, top_k=10, **kwargs):
        # 1. 分词
        tokens = self._tokenize(query)

        # 2. BM25 计算
        scores = {}
        for doc_id, doc_tokens in self._index.items():
            score = self._bm25_score(tokens, doc_tokens)
            scores[doc_id] = score

        # 3. 排序取 Top-K
        return self._get_top_k(scores, top_k)
```

**BM25 公式**：

$$
\text{score}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}
$$

其中：
- $f(q_i, D)$: 词 $q_i$ 在文档 $D$ 中的频率
- $|D|$: 文档 $D$ 的长度
- $\text{avgdl}$: 平均文档长度
- $k_1$, $b$: 可调参数

### 多路召回

Stage 2 支持多路并行召回，然后去重合并：

```python
# 流水线配置
pipeline = RetrievalPipeline(
    candidate_providers=[
        ChromaVectorRetrieval(),
        BM25KeywordRetrieval(),
    ],
)

# 执行时：
# 1. 并行执行两个检索器
# 2. 合并结果并按 score 排序
# 3. 去重（相同 ID 只保留一个）
```

---

## Stage 3: 排序筛选

### 设计理念

排序筛选是检索系统的"裁判"，负责从候选文档中选出最相关的结果。

### 提供的 Provider

#### 1. MMRReranker (MMR 多样性重排)

**原理**：平衡相关性与多样性

**公式**：

$$
\text{MMR} = \arg\max_{D_i \in R \setminus S} \left[
    \lambda \cdot \text{Sim}(D_i, Q) - (1 - \lambda) \cdot \max_{D_j \in S} \text{Sim}(D_i, D_j)
\right]
$$

其中：
- $Q$: 查询
- $R$: 候选集合
- $S$: 已选择集合
- $\lambda$: 权衡参数

**代码实现**：

```python
class MMRReranker:
    def rerank(self, query, candidates, lambda_param=0.5, top_k=None):
        query_vector = self._get_query_vector(query)
        doc_vectors = [self._get_doc_vector(doc) for doc in candidates]

        selected = []
        remaining = list(range(len(candidates)))

        while remaining:
            best_score = float('-inf')
            best_idx = None

            for idx in remaining:
                relevance = self._similarity(query_vector, doc_vectors[idx])

                # 计算与已选文档的最大相似度
                max_sim = max(
                    self._similarity(doc_vectors[idx], doc_vectors[s])
                    for s in selected
                ) if selected else 0

                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx

            selected.append(best_idx)
            remaining.remove(best_idx)

        return [candidates[i] for i in selected[:top_k]]
```

**参数说明**：
- `lambda_param`:
  - `1.0`: 完全相关性优先
  - `0.5`: 平衡
  - `0.0`: 完全多样性优先

#### 2. RRFReranker (RRF 排名融合)

**原理**：融合多个排名列表

**公式**：

$$
\text{RRF} = \sum_{i=1}^{k} \frac{1}{r_i + c}
$$

其中：
- $r_i$: 文档在第 $i$ 个列表中的排名
- $c$: 常数（默认 60）

**代码实现**：

```python
class RRFReranker:
    def __init__(self, k=60):
        self._k = k

    def rerank(self, query, candidates, ranked_lists=None, top_k=None):
        rrf_scores = {}

        for ranked_list in ranked_lists:
            for rank, doc in enumerate(ranked_list):
                doc_id = doc["id"]
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                rrf_scores[doc_id] += 1.0 / (self._k + rank + 1)

        # 按 RRF 分数排序
        sorted_docs = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [doc_map[doc_id] for doc_id, _ in sorted_docs][:top_k]
```

#### 3. SemanticReranker (语义重排)

使用 LLM 进行语义相关性评分：

```python
class SemanticReranker:
    def rerank(self, query, candidates, top_k=None):
        scored_docs = []

        for doc in candidates:
            # 让 LLM 评分
            score = self._llm_score(query, doc["text"])
            scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored_docs][:top_k]
```

#### 4. ScoreFilter (分值过滤)

基于阈值的简单过滤：

```python
class ScoreFilter:
    def rerank(self, query, candidates, threshold=0.7, top_k=None):
        filtered = [
            doc for doc in candidates
            if doc.get("score", 0) >= threshold
        ]
        filtered.sort(key=lambda x: x.get("score", 0), reverse=True)
        return filtered[:top_k]
```

### 排序流水线

Stage 3 支持链式调用多个排序器：

```python
pipeline = RetrievalPipeline(
    reranking_providers=[
        MMRReranker(),           # 1. 多样性重排
        SemanticReranker(),      # 2. 语义重排
        ScoreFilter(threshold=0.7),  # 3. 阈值过滤
    ],
)
```

---

## 使用指南

### 基础用法

```python
from retrieval.pipeline import RetrievalPipeline
from retrieval.candidate.vector_retrieval import ChromaVectorRetrieval
from retrieval.ranking.mmr import MMRReranker
from retrieval.ranking.score_filter import ScoreFilter

# 创建流水线
pipeline = RetrievalPipeline(
    understanding_providers=[
        SynonymExpander(),
    ],
    candidate_providers=[
        ChromaVectorRetrieval(),
    ],
    reranking_providers=[
        MMRReranker(),
        ScoreFilter(threshold=0.7),
    ],
    default_top_k=5,
)

# 初始化
pipeline.initialize()

# 执行检索
results = pipeline.retrieve(
    query="RAG 技术是什么",
    top_k=5,
    use_mmr=True,
    mmr_lambda=0.5,
)
```

### 高级用法

```python
# 动态添加 Provider
pipeline.add_understanding_provider(HyDEProvider())
pipeline.add_candidate_provider(BM25KeywordRetrieval())

# 获取统计信息
stats = pipeline.get_stats()
print(stats)
# {
#     "type": "retrieval_pipeline",
#     "stages": {
#         "understanding": ["synonym_expander", "hyde"],
#         "candidate": ["chroma_vector", "bm25_keyword"],
#         "reranking": ["mmr_reranker", "score_filter"]
#     },
#     "defaults": {"top_k": 5, "threshold": 0.7}
# }
```

---

## 自定义 Provider

### 自定义查询理解 Provider

```python
from retrieval.understanding.base import (
    BaseQueryUnderstandingProvider,
    QueryUnderstandingResult
)

class MyQueryRewriter(BaseQueryUnderstandingProvider):
    name = "my_rewrite"
    description = "自定义查询重写"

    def process(self, query: str, context=None) -> QueryUnderstandingResult:
        # 实现你的逻辑
        return QueryUnderstandingResult(
            original_query=query,
            processed_query=query.upper(),  # 示例：转为大写
            sub_queries=[query],  # 示例：生成子查询
        )

    def supports(self) -> list[str]:
        return ["rewrite"]
```

### 自定义候选召回 Provider

```python
from retrieval.candidate.base import BaseRetrievalProvider

class MyVectorRetrieval(BaseRetrievalProvider):
    name = "my_vector"
    description = "自定义向量检索"

    @property
    def vector_store(self):
        return self._vector_store

    @property
    def embedding_model(self):
        return self._embedding_model

    def __init__(self, vector_store, embedding_model):
        self._vector_store = vector_store
        self._embedding_model = embedding_model

    def search(self, query, top_k=10, **kwargs):
        # 实现检索逻辑
        return []
```

### 自定义排序 Provider

```python
from retrieval.ranking.base import BaseRerankingProvider

class MyReranker(BaseRerankingProvider):
    name = "my_reranker"
    description = "自定义排序"

    def rerank(self, query, candidates, **kwargs):
        # 实现排序逻辑
        return candidates
```

### 注册自定义 Provider

```python
# 创建流水线时注入
pipeline = RetrievalPipeline(
    understanding_providers=[MyQueryRewriter()],
    candidate_providers=[MyVectorRetrieval(...)],
    reranking_providers=[MyReranker()],
)
```

---

## 性能优化

### 1. 批量处理

```python
# 批量检索
queries = ["RAG 是什么", "RAG 的应用", "RAG 实现"]
results = [pipeline.retrieve(q) for q in queries]
```

### 2. 批量检索

```python
# 批量检索
queries = ["RAG 是什么", "RAG 的应用", "RAG 实现"]
results = [pipeline.retrieve(q) for q in queries]
```

### 3. 异步执行

```python
import asyncio

async def batch_retrieve(queries):
    tasks = [pipeline.retrieve(q) for q in queries]
    results = await asyncio.gather(*tasks)
    return results
```

---

## 最佳实践

### 1. 选择合适的 Provider 组合

| 场景 | 推荐配置 |
|------|----------|
| 通用问答 | SynonymExpander → ChromaVectorRetrieval → MMR + ScoreFilter |
| 精确搜索 | SimpleQueryRewriter → BM25 → ScoreFilter |
| 学术问答 | LLMQueryRewriter + SubqueryDecomposer → Chroma + BM25 → SemanticReranker |

### 2. 参数调优

```python
# MMR 参数
results = pipeline.retrieve(
    query="...",
    use_mmr=True,
    mmr_lambda=0.7,  # 提高相关性权重
)

# 阈值参数
results = pipeline.retrieve(
    query="...",
    similarity_threshold=0.8,  # 提高精度
)
```

### 3. 监控和调优

```python
# 获取统计信息
stats = pipeline.get_stats()
print(f"检索结果数: {len(results)}")
print(f"候选文档数: {stats['candidate_stats']}")
```

---

## 相关文档

- [架构设计文档](architecture.md) - 整体架构说明
- [API 参考文档](api-reference.md) - 接口使用说明
- [配置指南](configuration.md) - 配置项详解
