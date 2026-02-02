### 📘 词汇表（Words）— arXiv:2601.14192

#### Nouns（名词）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| agent | /ˈeɪdʒənt/ | 智能体；代理 | actor; assistant | An efficient agent reduces tokens and latency across steps. |
| efficiency | /ɪˈfɪʃənsi/ | 效率 | effectiveness-per-cost; efficiency gain | The survey emphasizes efficiency for real-world deployment. |
| latency | /ˈleɪtənsi/ | 延迟 | response time; lag | Tool calls often increase end-to-end latency. |
| token | /ˈtoʊkən/ | 词元；token | subword; unit | Token consumption compounds across multi-step trajectories. |
| saturation | /ˌsætʃəˈreɪʃən/ | 饱和；（资源/窗口）饱和 | overload; crowding | Context window saturation can hurt long-horizon agents. |
| bottleneck | /ˈbɑːt̬lˌnɛk/ | 瓶颈 | constraint; choke point | Efficiency becomes a deployment bottleneck for agents. |
| deployment | /dɪˈplɔɪmənt/ | 部署 | rollout; release | Latency matters most at deployment time. |
| sustainability | /səˌsteɪnəˈbɪləti/ | 可持续性 | viability; endurance | High cost threatens the sustainability of agentic systems. |
| accessibility | /əkˌsɛsəˈbɪləti/ | 可获得性；可及性 | availability; reach | Lower cost improves equitable accessibility. |
| memory | /ˈmɛməri/ | 记忆模块；存储 | storage; recall | Memory helps agents avoid redundant computation. |
| context | /ˈkɑːntɛkst/ | 上下文 | prompt; surrounding text | Long context may bury relevant evidence. |
| window | /ˈwɪndoʊ/ | （上下文）窗口 | span; limit | The context window is finite. |
| overhead | /ˈoʊvərˌhɛd/ | 额外开销 | extra cost; burden | Retrieval introduces system overhead and latency. |
| trajectory | /trəˈdʒɛktəri/ | （交互）轨迹；多步过程 | rollout; sequence | The agent’s trajectory may include retries and tool calls. |
| retrieval | /rɪˈtriːvəl/ | 检索 | lookup; fetch | Retrieval quality affects both cost and accuracy. |
| compression | /kəmˈprɛʃən/ | 压缩 | shortening; condensing | Compression bounds token growth under a budget. |
| summarization | /ˌsʌmərəˈzeɪʃən/ | 摘要化；总结 | abstraction; synopsis | Summarization turns long histories into manageable memory. |
| taxonomy | /tækˈsɑːnəmi/ | 分类体系 | categorization; framework | The paper proposes a taxonomy of efficiency methods. |
| benchmark | /ˈbɛntʃˌmɑːrk/ | 基准；评测 | evaluation set; yardstick | Benchmarks report both effectiveness and efficiency metrics. |
| protocol | /ˈproʊt̬əˌkɔːl/ | 协议；流程规范 | procedure; standard | MCP-style protocols standardize tool definitions and calls. |
| metric | /ˈmɛtrɪk/ | 指标 | measure; indicator | Token usage is a common efficiency metric. |
| frontier | /frʌnˈtɪr/ | 前沿；边界 | cutting edge; boundary | The Pareto frontier shows cost–quality trade-offs. |
| trade-off | /ˈtreɪdˌɔːf/ | 权衡 | compromise; balance | Compression often trades accuracy for lower cost. |
| budget | /ˈbʌdʒɪt/ | 预算；资源上限 | cap; allowance | Agents can be evaluated under a fixed cost budget. |
| reranker | /ˌriːˈræŋkər/ | 重排器 | ranker; scorer | A reranker can improve top-k tool selection. |
| knapsack | /ˈnæpˌsæk/ | 背包（问题） | packing problem; allocation | Tool calling can be framed as a knapsack problem under budget. |
| reward | /rɪˈwɔːrd/ | 奖励（强化学习） | payoff; return | Efficiency-aware rewards penalize unnecessary tool calls. |
| penalty | /ˈpɛnəlti/ | 惩罚项 | punishment; cost term | A tool-use penalty reduces redundant invocations. |
| distillation | /ˌdɪstəˈleɪʃən/ | 蒸馏；知识提炼 | compression; transfer | Distillation can compress multi-agent coordination into one model. |
| orchestrator | /ˈɔːrkəˌstreɪtər/ | 编排器；调度器 | coordinator; controller | An orchestrator routes subtasks to tools or specialists. |
| retriever | /rɪˈtriːvər/ | 检索器 | fetcher; searcher | External retrievers select tools from large pools. |
| embedding | /ɪmˈbɛdɪŋ/ | 嵌入表示 | vector representation; encoding | Embedding similarity supports memory retrieval. |
| similarity | /ˌsɪməˈlærɪti/ | 相似度 | likeness; affinity | Similarity scores rank memories for retrieval. |
| pruning | /ˈpruːnɪŋ/ | 剪枝 | trimming; cutting | Pruning unproductive branches improves search efficiency. |
| sparsification | /ˌspɑːrsɪfɪˈkeɪʃən/ | 稀疏化 | thinning; sparsity | Communication sparsification reduces multi-agent overhead. |
| topology | /təˈpɑːlədʒi/ | 拓扑结构 | structure; layout | Topology design can reduce communication from \(O(N^2)\) to \(O(N)\). |
| consensus | /kənˈsɛnsəs/ | 共识 | agreement; concord | Consensus protocols may terminate redundant debates early. |
| coordination | /koʊˌɔːrdəˈneɪʃən/ | 协同；协调 | cooperation; orchestration | Coordination quality affects both cost and accuracy. |
| kernel | /ˈkɝːnəl/ | 核（如转移核） | core; nucleus | The transition kernel defines environment dynamics in POMDPs. |
| factor | /ˈfæktər/ | 因子；系数（如折扣因子） | coefficient; term | The discount factor \(\gamma\) controls long-term rewards. |

#### Verbs（动词）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| augment | /ɔːɡˈmɛnt/ | 增强；扩充 | enhance; enrich | Agents augment a base LLM with memory and tools. |
| compress | /kəmˈprɛs/ | 压缩 | shrink; condense | We compress long histories to bound token usage. |
| retrieve | /rɪˈtriːv/ | 检索；取回 | fetch; recall | The agent retrieves only the most relevant memories. |
| curate | /kjʊˈreɪt/ | 筛选；精心整理 | filter; select | Curate memory entries to avoid noise and bloat. |
| externalize | /ɪkˈstɝːnəˌlaɪz/ | 外置；外显化 | offload; outsource | Externalize knowledge into a retrievable store. |
| invoke | /ɪnˈvoʊk/ | 调用（工具/接口） | call; trigger | The model decides when to invoke a search tool. |
| allocate | /ˈæləˌkeɪt/ | 分配（预算/计算） | assign; apportion | Allocate compute adaptively under a token budget. |
| prune | /pruːn/ | 剪枝；裁剪 | trim; cut | Prune expensive branches early in search. |
| distill | /dɪˈstɪl/ | 提炼；蒸馏 | extract; condense | Distill successful trajectories into reusable skills. |
| route | /raʊt/ | 路由；分派 | dispatch; direct | Route subtasks to tools to reduce reasoning tokens. |
| decompose | /ˌdiːkəmˈpoʊz/ | 分解（任务） | break down; split | Decompose a complex task into smaller subtasks. |
| integrate | /ˈɪntəˌɡreɪt/ | 集成；融合 | combine; merge | Integrate retrieved snippets into a compact prompt block. |
| optimize | /ˈɑːptəˌmaɪz/ | 优化 | improve; refine | Optimize the cost–success trade-off along the trajectory. |
| mitigate | /ˈmɪt̬əˌɡeɪt/ | 缓解；减轻 | alleviate; reduce | Memory helps mitigate costly retries. |
| amortize | /ˈæməˌrtaɪz/ | 摊销；均摊 | spread; distribute | Reusing memory amortizes planning cost over episodes. |
| converge | /kənˈvɝːdʒ/ | 收敛 | stabilize; settle | Tool policies converge after RL fine-tuning. |
| penalize | /ˈpiːnəˌlaɪz/ | 惩罚 | punish; dock | Penalize redundant tool calls in the RL objective. |
| evaluate | /ɪˈvæljuˌeɪt/ | 评估 | assess; measure | Evaluate success rates under fixed cost budgets. |
| saturate | /ˈsætʃəˌreɪt/ | 使饱和；充满 | overload; fill | Long contexts can saturate the window and degrade accuracy. |
| consolidate | /kənˈsɑːlɪˌdeɪt/ | 合并；巩固 | merge; unify | Consolidate memories offline to reduce serving latency. |

#### Adjectives（形容词）

| 英文 | 美式音标 | 中文含义 | 近义词 | 示例 |
|------|----------|----------|--------|------|
| efficient | /ɪˈfɪʃənt/ | 高效的 | cost-effective; streamlined | Efficient agents maximize success with minimal resources. |
| agentic | /ˌeɪdʒənˈtɪk/ | 智能体式的；代理式的 | autonomous; agent-based | Agentic workflows require planning, tools, and memory. |
| recursive | /rɪˈkɝːsɪv/ | 递归的 | iterative; self-referential | The loop is recursive: each step feeds the next. |
| prohibitive | /prəˈhɪbətɪv/ | （成本/门槛）高得难以承受的 | excessive; too costly | Prohibitive latency blocks real-time applications. |
| unbounded | /ʌnˈbaʊndɪd/ | 无界的；无限制的 | limitless; unconstrained | Memory must manage unbounded histories efficiently. |
| hierarchical | /ˌhaɪəˈrɑːrkɪkəl/ | 分层的 | multi-level; tiered | Hierarchical memory enables coarse-to-fine retrieval. |
| graph-based | /ˈɡræf beɪst/ | 基于图的 | graph-structured; network-based | Graph-based retrieval supports multi-hop evidence chaining. |
| cost-aware | /ˈkɔːst əˈwɛr/ | 成本感知的 | budget-aware; cost-sensitive | Cost-aware planning trades depth for lower expense. |
| task-agnostic | /tæsk æɡˈnɑːstɪk/ | 任务无关的 | generic; non-specific | Task-agnostic rules may drop critical memories. |
| deployment-aware | /dɪˈplɔɪmənt əˈwɛr/ | 面向部署的 | production-oriented; practical | Deployment-aware designs report end-to-end latency. |
