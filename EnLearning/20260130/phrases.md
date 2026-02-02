### 📗 短语表（Phrases）— arXiv:2601.14192

#### Efficiency & metrics（效率与指标）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| cost-performance trade-off | /kɔːst pərˈfɔːrməns ˈtreɪdˌɔːf/ | 成本-性能权衡 | cost–quality trade-off; efficiency–effectiveness trade-off | The paper frames efficiency as a cost-performance trade-off. |
| cost budget | /kɔːst ˈbʌdʒɪt/ | 成本预算；资源上限 | budget cap; spending limit | Compare effectiveness under a fixed cost budget. |
| token consumption | /ˈtoʊkən kənˈsʌmpʃən/ | token 消耗 | token usage; token spend | Token consumption often dominates agent cost. |
| inference latency | /ˈɪnfərəns ˈleɪtənsi/ | 推理延迟 | serving latency; response time | Tool calls can increase inference latency dramatically. |
| computational cost | /ˌkɑːmpjəˈteɪʃənəl kɔːst/ | 计算成本 | compute cost; processing cost | Efficiency aims to reduce computational cost without losing accuracy. |
| end-to-end latency | /ˌɛnd tə ˈɛnd ˈleɪtənsi/ | 端到端延迟 | overall latency; total delay | Measure end-to-end latency including retrieval and tool time. |
| runtime cost | /ˈrʌnˌtaɪm kɔːst/ | 运行时成本 | runtime overhead; execution cost | Some benchmarks report runtime cost alongside accuracy. |
| step efficiency | /stɛp ɪˈfɪʃənsi/ | 步数效率（更少步骤达成目标） | step economy; trajectory efficiency | Memory can improve step efficiency by avoiding retries. |
| cost-of-pass | /kɔːst əv pæs/ | 每次成功的期望成本 | expected cost per success; economic success cost | Use cost-of-pass to link completion rate with cost. |
| Pareto frontier | /pəˈreɪtoʊ frʌnˈtɪr/ | 帕累托前沿 | efficient frontier; trade-off curve | Methods lie on a Pareto frontier between cost and success. |

#### Agent formulation & loop（建模与循环）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| plan–act–observe loop | /plæn ækt əbˈzɝːv luːp/ | 计划-行动-观察循环 | iterative loop; agent loop | Agents repeatedly run a plan–act–observe loop to solve tasks. |
| memory–planning–tool learning cycle | /ˈmɛməri ˈplænɪŋ tuːl ˈlɝːnɪŋ ˈsaɪkəl/ | 记忆-规划-工具学习循环 | agent pipeline; interaction cycle | The survey decomposes cost sources by this cycle. |
| partially observable Markov decision process | /ˌpɑːrʃəli əbˈzɝːvəbəl ˈmɑːrkɔːv dɪˈsɪʒən ˈproʊsɛs/ | 部分可观测马尔可夫决策过程（POMDP） | POMDP; stochastic control model | The agent is modeled as a POMDP with tools and memory. |
| transition kernel | /trænˈzɪʃən ˈkɝːnəl/ | 转移核 | transition function; dynamics kernel | The transition kernel defines environment dynamics. |
| reward function | /rɪˈwɔːrd ˈfʌŋkʃən/ | 奖励函数 | payoff function; utility function | RL optimizes a reward function that can include cost terms. |
| discount factor | /ˈdɪskaʊnt ˈfæktər/ | 折扣因子 | gamma; discount rate | The discount factor \(\gamma\) weighs future rewards. |
| tool interface | /tuːl ˈɪntərˌfeɪs/ | 工具接口 | API interface; tool API | A tool interface specifies how calls and outputs are handled. |
| memory update rule | /ˈmɛməri ˈʌpˌdeɪt ruːl/ | 记忆更新规则 | update policy; write rule | A memory update rule controls what to store and when. |

#### Memory（记忆：构建/管理/访问）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| working memory | /ˈwɝːkɪŋ ˈmɛməri/ | 工作记忆（推理时可直接使用的上下文/状态） | short-term memory; active context | Working memory must stay compact to save tokens. |
| external memory | /ɪkˈstɝːnəl ˈmɛməri/ | 外部记忆（检索式存储） | long-term store; retrieval memory | External memory enables unbounded storage via retrieval. |
| memory construction | /ˈmɛməri kənˈstrʌkʃən/ | 记忆构建 | memory formation; memory building | Memory construction often relies on summarization. |
| memory management | /ˈmɛməri ˈmænɪdʒmənt/ | 记忆管理 | memory maintenance; memory curation | Memory management prevents storage explosion. |
| rule-based management | /ruːl beɪst ˈmænɪdʒmənt/ | 基于规则的管理 | heuristic management; policy-based control | Rule-based management is fast but can be brittle. |
| LLM-based management | /ˌɛl ˌɛl ˈɛm beɪst ˈmænɪdʒmənt/ | 基于 LLM 的管理 | model-driven management; learned management | LLM-based management adds cost but is adaptive. |
| hybrid management | /ˈhaɪbrɪd ˈmænɪdʒmənt/ | 混合式管理 | combined strategy; mixed management | Hybrid management triggers LLM calls only when needed. |
| memory access | /ˈmɛməri ˈæksɛs/ | 记忆访问 | recall; lookup | Memory access decides what to retrieve and how to use it. |
| memory selection | /ˈmɛməri səˈlɛkʃən/ | 记忆选择 | retrieval selection; choosing memories | Memory selection balances relevance and latency. |
| memory integration | /ˈmɛməri ˌɪntəˈɡreɪʃən/ | 记忆整合（注入提示/融合使用） | insertion; incorporation | Memory integration formats retrieved items into a compact block. |
| hierarchical memory | /ˌhaɪəˈrɑːrkɪkəl ˈmɛməri/ | 分层记忆 | tiered memory; multi-level memory | Hierarchical memory supports coarse-to-fine access. |
| graph-based memory | /ˈɡræf beɪst ˈmɛməri/ | 图结构记忆 | KG memory; graph store | Graph-based memory organizes entities and relations. |
| forgetting curve | /fərˈɡɛtɪŋ kɝːv/ | 遗忘曲线 | decay curve; Ebbinghaus curve | A forgetting curve can decay stale memories over time. |
| FIFO replacement | /ˈfaɪfoʊ rɪˈpleɪsmənt/ | 先进先出替换策略 | queue eviction; buffer eviction | FIFO replacement is a cheap rule for bounded buffers. |
| retrieval noise | /rɪˈtriːvəl nɔɪz/ | 检索噪声 | irrelevant hits; retrieval errors | Retrieval noise can waste tokens and hurt accuracy. |
| vector similarity search | /ˈvɛktər ˌsɪməˈlærɪti sɝːtʃ/ | 向量相似度检索 | embedding search; semantic search | Vector similarity search retrieves top-k relevant memories. |

#### Tools & planning（工具学习与规划）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| tool selection | /tuːl səˈlɛkʃən/ | 工具选择 | tool retrieval; tool picking | Tool selection avoids stuffing thousands of tools into the prompt. |
| tool calling | /tuːl ˈkɔːlɪŋ/ | 工具调用 | function calling; API calling | Tool calling adds extra latency beyond generation. |
| tool-integrated reasoning | /tuːl ˈɪntəɡreɪtɪd ˈriːzənɪŋ/ | 工具融合推理 | tool-augmented reasoning; TIR | Tool-integrated reasoning invokes tools only when necessary. |
| in-place parameter filling | /ɪn pleɪs pəˈræmɪtər ˈfɪlɪŋ/ | 原位参数填充 | inline parameterization; direct infilling | In-place parameter filling reduces extra formatting steps. |
| parallel tool calling | /ˈpærəˌlɛl tuːl ˈkɔːlɪŋ/ | 并行工具调用 | concurrent calls; parallel execution | Parallel tool calling reduces wall-clock time for independent queries. |
| cost-aware tool calling | /ˈkɔːst əˈwɛr tuːl ˈkɔːlɪŋ/ | 成本感知的工具调用 | budget-aware calling; economical calling | Cost-aware tool calling trades extra calls for higher confidence. |
| tool-use penalty | /tuːl juːz ˈpɛnəlti/ | 工具使用惩罚项 | call penalty; tool cost term | Add a tool-use penalty to discourage redundant calls. |
| efficiency-aware rewards | /ɪˈfɪʃənsi əˈwɛr rɪˈwɔːrdz/ | 效率感知奖励 | cost-sensitive rewards; parsimonious rewards | Efficiency-aware rewards optimize success per dollar. |
| budget-constrained tool learning | /ˈbʌdʒɪt kənˈstreɪnd tuːl ˈlɝːnɪŋ/ | 预算约束下的工具学习 | budgeted tool use; constrained tooling | Budget-constrained tool learning plans calls under a hard cap. |
| fast–slow thinking | /fæst sloʊ ˈθɪŋkɪŋ/ | 快-慢思考机制 | dual-process; System 1/2 | Fast–slow thinking allocates compute only when needed. |
| adaptive budgeting | /əˈdæptɪv ˈbʌdʒɪtɪŋ/ | 自适应预算分配 | dynamic budgeting; compute allocation | Adaptive budgeting adjusts depth based on difficulty. |
| Monte Carlo tree search | /ˈmɑːnteɪ ˈkɑːrloʊ triː sɝːtʃ/ | 蒙特卡洛树搜索（MCTS） | MCTS; tree search | MCTS can guide exploration but adds overhead. |
| A* search | /ˈeɪ stɑːr sɝːtʃ/ | A* 搜索 | heuristic search; best-first search | A* search prunes branches via a learned cost function. |
| task decomposition | /tæsk ˌdiːkəmˈpoʊzɪʃən/ | 任务分解 | subtasking; breakdown | Task decomposition reduces step-by-step token redundancy. |
| protocol compression | /ˈproʊt̬əˌkɔːl kəmˈprɛʃən/ | 协议/交流压缩 | context compression; message compression | Protocol compression reduces communication tokens in multi-agent systems. |
| topology sparsification | /təˈpɑːlədʒi ˌspɑːrsɪfɪˈkeɪʃən/ | 拓扑稀疏化 | edge pruning; graph sparsification | Topology sparsification cuts quadratic communication overhead. |
