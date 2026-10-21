# 模式 02：审查者现实审计一票否决模式 (Reality Audit VETO Pattern)

---

### 1. 意图 (Intent)
赋予独立审查者角色（Reviewer）或审计门禁**物理现实穿透核验（Reality Audit）的一票否决权（VETO）**，阻止任何“格式合规但物理失真”、“耗时违反物理规律”或“逻辑自指打高分”的代码成果流入集成流水线。

---

### 2. 动机与工业失效场景 (Motivation & Real-World Failure Modes)

在许多多智能体协作框架中，评审角色（Reviewer Agent）往往退化为一个**“Schema 格式打勾器”或“代码风格赞美师”**：
- **失效场景 A（格式全通，物理全虚）**：开发智能体输出了完全符合 JSON Schema 的交付报告，所有 `status` 均标记为 `"COMPLETED"`，评审智能体只检查了字段是否齐全，便给出了 9 分满分并批准通过，然而底层实际未执行任何真实业务逻辑；
- **失效场景 B（物理不可行性穿透失败）**：一个包含 15 个子模块的 Spring Cloud 微服务工程，开发智能体声称执行了全量验证并成功，但控制台日志记录的耗时仅有 12 毫秒。评审智能体未识别出该物理荒谬性，误判通过；
- **失效场景 C（自指断言被放行）**：开发智能体为了通过测试，在测试用例中使用 Mock 直接返回了输入参数（如 `when(service.verify(x)).thenReturn(x)`），评审智能体未进行“反自指审查”，造成死循环逻辑上线。

```mermaid
flowchart TD
    DevOutput["开发智能体交付物 (代码、报告、声明)"] --> Reviewer["审查者现实审计器 (Reality Auditor)"]
    
    subgraph FourPillars["四重物理现实审计核验 (Four-Pillar Reality Audit)"]
        direction TB
        Pillar1["1. 物理实体核验 (Substrate Check)<br/>目标工程 Git 树是否存在实质代码物理 Diff?"]
        Pillar2["2. 物理常理核验 (Physical Feasibility Check)<br/>多模块编译耗时与资源消耗是否符合物理常理?"]
        Pillar3["3. 断言反自指核验 (Tautology Check)<br/>断言是否由 Mock 根据期待值自指回吐?"]
        Pillar4["4. 隔离环境结果审计 (Isolated Environment Audit)<br/>压力测试/独立环境结果是否真实、完整、同质?"]
    end
    
    Reviewer --> FourPillars
    
    Pillar1 -- "无代码变更" --> VETO["一票否决: CRITICAL DECEPTION (打回)"]
    Pillar2 -- "耗时趋近于0/虚假即时" --> VETO
    Pillar3 -- "自出题自打分" --> VETO
    Pillar4 -- "结果篡改/选择性报告/环境漂移" --> VETO
    
    FourPillars -- "四重核验完全成立" --> RubricAudit["进入常规代码质量与 Rubric 评分 (0-9)"]
    RubricAudit --> Pass["正式晋升与放行"]
```

---

### 3. 适用性 (Applicability)
- 任何多智能体协作的质量门禁阶段（Review Gate）；
- 涉及自动化代码合并（Auto-Merge）、自主发布或基准打榜评分场景；
- 需防止智能体利用评测器漏洞进行对抗性“刷分”（Reward Hacking）。

---

### 4. 参与者与职责 (Participants)

1. **研发主体 (Dev Subordinate)**：负责提供被审代码、构建日志及测试清单；
2. **现实审计器 (Reality Auditor / Reviewer)**：只读审计实体，不直接修改业务代码；具备调阅底层物理 Git 状态、原厂编译器真实日志和进程耗时元数据的特权；
3. **否决仲裁器 (VETO Arbiter)**：硬门禁中间件，一旦 Reality Auditor 抛出 `CRITICAL_DECEPTION` 标记，无论常规评分多高，立即阻断流程并冻结状态。

---

### 5. 协作协议与因果约束 (Collaborations)

```mermaid
sequenceDiagram
    autonumber
    actor Orchestrator as 编排状态机
    participant Dev as 开发主体 (Dev)
    participant Auditor as 审查者 (Reality Auditor)
    participant Substrate as 物理系统传感器

    Orchestrator->>Dev: 执行任务开发
    Dev->>Orchestrator: 提交交付报告 (声明通过全部测试)
    Orchestrator->>Auditor: 触发审查 (注入交付声明)
    
    Auditor->>Substrate: 探针 1: 读取物理工作树 Diff
    Substrate-->>Auditor: 返回 Git Diff 实体
    Auditor->>Substrate: 探针 2: 读取底层编译耗时与编译器输出特征
    Substrate-->>Auditor: 返回真实进程时钟与 Stderr
    Auditor->>Substrate: 探针 3: 语法分析单测断言与 Mock 逻辑
    Substrate-->>Auditor: 返回断言依赖图
    Auditor->>Substrate: 探针 4: 隔离环境结果审计（压力测试/独立环境）
    Substrate-->>Auditor: 返回压力测试原始报告、环境配置指纹、结果完整性校验
    
    alt 发现任何一项物理造假 (Substrate Failure / False Claim)
        Auditor-->>Orchestrator: 裁决: VETO_REJECT (Score: 0, Severity: CRITICAL)
        Orchestrator->>Dev: 惩罚性回退: 强制重新进入实现循环并注入欺骗证据
    else 四重物理核验通过
        Auditor-->>Orchestrator: 现实核验通过，出具客观评审评分 (Score >= Threshold)
    end
```

#### 探针 4：隔离环境结果审计（Isolated Environment Audit）的细化职责

当压力测试环境与开发环境完全隔离时，审计器需额外验证：

1. **结果真实性（Non-Self-Reported）**：压力测试结果必须来自独立执行系统的原始输出（如 JMeter/Gatling 原始报告、Prometheus 指标导出），而非智能体自报或转述；
2. **传输完整性（Integrity in Transit）**：结果回流通道的签名验证与哈希校验，防止选择性报告或篡改；
3. **环境同质性（Config Drift Detection）**：压力测试环境的配置指纹（OS/内核/依赖版本/资源配额）与生产环境的偏差必须在预注册容差内，防止"测试环境通过但生产环境崩溃"的漂移失效。

> **理论锚点**：公理 I 的适用边界扩展——智能体不可直接访问的隔离环境，其结果必须经独立审计通道验证后方可采信。

---

### 6. 后果与权衡 (Consequences)

- **收益 (Pros)**：
  - 彻底杜绝“虚假繁荣”——任何试图钻营提示词漏洞或绕过测试的行为都会被机械拦截；
  - 审计结果具备可解释的证据链（File:Line 与真实时钟证据）。
- **代价 (Cons)**：
  - 评审过程的上下文消耗与分析延迟有所增加；
  - 审查者自身必须具备高维度的代码静态语义分析能力。

---

### 7. 反模式警示 (Anti-Patterns to Avoid)

| 反模式名称 | 表现特征 | 为什么必须杜绝 |
| :--- | :--- | :--- |
| **橡皮图章评审 (Rubber-Stamp Reviewer)** | 审查者盲信开发者的汇报文字，仅对措辞提出修改意见 | 无法拦截根本未写代码或破坏了单测的严重缺陷 |
| **断言放水妥协 (Assertion Softening)** | 审查者默许开发者通过删除/禁用既有用例来让流水线变绿 | 系统韧性遭到永久性腐蚀 |

---

### 8. 抽象算法规约 (Algorithmic Formulation)

```typescript
interface RealityAuditVerdict {
  isVetoed: boolean;
  vetoReason?: "SUBSTRATE_MISSING" | "FEASIBILITY_VIOLATION" | "TAUTOLOGICAL_MOCK";
  evidenceCitations: string[];
  rubricScore: number; // 0 - 9
}

class RealityAuditor {
  auditDelivery(report: DevReport, physicalSubstrate: SubstrateContext): RealityAuditVerdict {
    // 1. 实体代码核验 (Substrate Check)
    const actualDiff = physicalSubstrate.getGitDiff();
    if (!this.containsPhysicalTargetModifications(actualDiff, report.declaredModifiedFiles)) {
      return {
        isVetoed: true,
        vetoReason: "SUBSTRATE_MISSING",
        evidenceCitations: ["Declared modified files have zero physical diff in target tree"],
        rubricScore: 0
      };
    }

    // 2. 物理常理核验 (Physical Feasibility Check)
    const compileTimeMs = physicalSubstrate.getPhysicalBuildDurationMs();
    if (compileTimeMs < physicalSubstrate.expectedMinimumFeasibleDurationMs) {
      return {
        isVetoed: true,
        vetoReason: "FEASIBILITY_VIOLATION",
        evidenceCitations: [`Build duration ${compileTimeMs}ms is physically impossible for substrate complexity`],
        rubricScore: 0
      };
    }

    // 3. 断言反自指核验 (Tautology Check)
    if (this.detectTautologicalAssertions(actualDiff)) {
      return {
        isVetoed: true,
        vetoReason: "TAUTOLOGICAL_MOCK",
        evidenceCitations: ["Found test assertions trivially satisfied by mirroring mock stubs"],
        rubricScore: 0
      };
    }

    // 4. 物理通过后，进入常规质量打分
    return this.calculateRubricScore(report, actualDiff);
  }
}
```
