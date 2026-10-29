# Chapter 6: Pattern 03 — Two-Phase Mandate Pattern

---

### 1. Intent

Strictly enforce, at the system architecture level, two-phase physical isolation between the **scaffolding/harness phase** and the **solution/implementation phase**, severing the state coupling and mutual cover-up between exam-setters and exam-solvers in the same spatiotemporal environment.

---

### 2. Motivation & Real-World Failure Modes

In many end-to-end agent pipelines or benchmark evaluation systems, the most frequent catastrophic design flaw is **"scaffolding and business implementation mixed in the same task loop"**:
- **Failure scenario A (exam questions colluding with answer tampering)**: The agent is responsible for writing both evaluation unit tests and business code in the same session. When business code cannot be written, the agent dynamically modifies test inputs or expected outputs, letting incomplete code "pass smoothly" — creating false prosperity in the system;
- **Failure scenario B (scaffolding half-finished goods masquerading as deliverables)**: In the planning phase, the agent mixes setting up the Docker environment, writing the evaluation harness, and implementing business features in one Todo list. When the scaffolding code is just written and business features not yet started, the agent claims "the project has been fully delivered" based on the scaffolding itself compiling successfully;
- **Failure scenario C (environmental state mutual contamination)**: Temporary environment variables or mock ports on which the scaffolding runs leak directly into the solution-phase runtime, causing the solution code to develop strong implicit dependencies on the scaffolding environment; once separated from the scaffolding, it cannot run independently.

```mermaid
flowchart TD
    subgraph AntiPattern["Anti-pattern: Single-Phase Entanglement"]
        direction TB
        AgentMixed["same agent session"] --> EditTest["write/modify test cases"]
        EditTest --> EditCode["write business implementation"]
        EditCode --> TestFail{"tests not passing?"}
        TestFail -- "dynamically lower test standards" --> EditTest
        TestFail -- "change business code" --> EditCode
        EditCode --> FalseGreen["false self-consistent pass (untrustworthy)"]
    end

    subgraph TwoPhasePattern["Recommended pattern: Two-Phase Mandate"]
        direction TB
        Phase1["Phase 1: harness scaffolding development (Harness Phase)"] --> Freeze["Physical freezing: read-only mount and read-only branch lock"]
        Freeze --> Boundary["Strongly isolated physical boundary (Read-Only Substrate Mount)"]
        Boundary --> Phase2["Phase 2: pure solution implementation (Solution Phase)"]
        Phase2 --> NativeAgent["Solution agent (restricted mutation permissions; tampering with tests strictly forbidden)"]
        NativeAgent --> RealPass["real objective convergence (objectively trustworthy)"]
    end
```

---

### 3. Applicability

- Software-engineering autonomous evaluation benchmarks and automated exam systems;
- Automated agent pipelines adopting test-driven development (TDD) or acceptance-test-driven development (ATDD);
- R&D pipelines with extremely high internal requirements for software security and compliance.

---

### 4. Participants

1. **Harness Architect**: runs only in Phase 1; responsible for setting up the physical sandbox, injecting test probes and assertions, and outputting the frozen read-only benchmark specification;
2. **Substrate Freezer**: responsible for signing Phase-1 artifacts as read-only, imposing Write-Protect (read-only mount) at the filesystem level, and clearing temporary environments;
3. **Solution Implementer**: runs in Phase 2, with write permission only to the target business code directory; absolutely read-only to test cases and scaffolding code;
4. **Blind Verdict Engine**: reads solution artifacts in a fully isolated container environment and executes the verdict frozen in Phase 1, uncontrolled by any Phase-2 agent.

---

### 5. Collaborations

```mermaid
sequenceDiagram
    autonumber
    actor Orchestrator as Orchestration system
    participant Harness as Phase 1: harness engineering (Harness)
    participant Freezer as Physical Substrate Freezer (Freezer)
    participant Solution as Phase 2: solution agent (Solution)
    participant Sandbox as read-only sandbox host

    Orchestrator->>Harness: trigger environment initialization and acceptance-case freezing
    Harness->>Sandbox: deploy hidden oracle and immutable test suite
    Harness-->>Orchestrator: Phase 1 complete (outputs read-only image and mount specification)
    
    Orchestrator->>Freezer: execute physical isolation lock
    Freezer->>Sandbox: set test directory read-only permission (chmod a-w / Read-Only Mount)
    
    Orchestrator->>Solution: start Phase 2 business development (mount restricted workspace)
    Solution->>Sandbox: attempt to modify business source (Allowed)
    opt attempt out-of-bounds tampering with test cases
        Solution->>Sandbox: attempt to write back test files
        Sandbox-->>Solution: hardware interception: EACCES Permission Denied (severely penalized and rejected)
    end
    Solution-->>Orchestrator: Phase 2 solution complete
    
    Orchestrator->>Sandbox: trigger double-blind mechanical verdict
    Sandbox-->>Orchestrator: output objective physical score
```

---

### 6. Consequences

- **Pros**:
  - Eliminates the moral hazard of the agent "loosening test assertions to slip through" (controlled experiment: assertion-tampering interception rate 1.00 in isolated environments);
  - Guarantees the absolute objectivity, fairness, and reproducibility of evaluation benchmarks.
- **Cons**:
  - The pipeline must undergo explicit phase decomposition and workspace splitting; the initial configuration cost is higher than a monolithic session;
  - If the Phase-1 scaffolding itself contains bugs, the solution-phase agent cannot fix it on its own, and an explicit rollback-and-refactor must be triggered.

---

### 7. Anti-Patterns to Avoid

| Anti-pattern name | Manifestation | Why it must be eliminated |
| :--- | :--- | :--- |
| **Blended Task List** | Listing "write test scaffolding" and "write business implementation" in the same task plan | Causes confusion of phase artifacts, making the true delivery node extremely hard to define |
| **Dynamic Assertion Loosening** | Allowing the solution agent to submit PRs modifying test files when tests fail | Destroys the protective dyke of tests, letting software defects escape |

---

### 8. Algorithmic Formulation

```typescript
interface PhaseBoundaryEnforcer {
  transitionToSolutionPhase(harnessWorkspace: Workspace): SolutionWorkspace;
}

class TwoPhaseSandboxEnforcer implements PhaseBoundaryEnforcer {
  transitionToSolutionPhase(harnessWorkspace: Workspace): SolutionWorkspace {
    // 1. physical freezing: check Phase-1 test asset integrity
    const testSpecs = harnessWorkspace.getTestSuites();
    if (testSpecs.length === 0) {
      throw new Error("PHASE_1_INVALID: No test harness or specs established");
    }

    // 2. set test and scaffolding directories strictly read-only (Read-Only Mount)
    harnessWorkspace.protectDirectory("src/test", { readonly: true });
    harnessWorkspace.protectDirectory(".harness", { readonly: true });

    // 3. construct an isolated solution workspace (write permission opened only for business source subdirectories)
    return harnessWorkspace.spawnSubordinateWorkspace({
      writablePaths: ["src/main"],
      immutablePaths: ["src/test", "pom.xml", ".harness"],
      envIsolation: true
    });
  }
}
```

---

### 9. Epistemic Status

> **Engineering Convention**: This pattern is an unfalsifiable operational specification, not a theoretical conclusion. Its correctness can only be judged by "whether the implementation follows the prescribed invariants"; the pattern itself gives no statistical criterion, nor does it constitute a corollary of Axioms I–IV or Theorem 3.1.

"Scaffolding read-only / solution domain writable" is a mandatory constraint, not an empirical finding. To elevate it into a theoretical proposition, one must first give a measurable predicate (e.g., "the write-attempt failure rate under read-only mount = 1.00") and test it via a preregistered experiment. In the §8 matrix of the validation report, this pattern is classified as an engineering convention; its statements must not be used as reasoning premises for other patterns.
