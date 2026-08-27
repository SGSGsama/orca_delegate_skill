有风险，但两个 skill 的风险性质不一样。你举的 **“Terra 自己去读大段 trace 日志”**，在逆向 skill 里属于我认为目前最值得补一道硬限制的地方。

### 1. 逆向 skill：边界设计正确，但目前是“软约束”

现在的理想数据流写得非常清楚：

> raw logs/traces → **Luna** → indexed evidence
> bounded target + evidence slice → **Terra** → local semantics
> local conclusions → **Primary** → global synthesis

`references/decomposition.md:93` 甚至明确说：

> 不要让每个 Terra 加载整个 logs。

而 `runtime-and-review.md:113-121` 更明确：

* bounded target evidence gap → Terra
* function/local flow → Terra
* **more logs/traces/dumps/candidates → Luna**
* bulk evidence 的 precise anomaly → **Terra + referenced evidence slice**

所以按照设计意图：

```text
错误：
Terra：
“这个函数语义不确定，我自己把 4GB trace 从头扫一遍。”

正确：
Luna：
4GB trace → index / cluster / anomaly / raw refs

Terra：
函数 F + Luna entries #182/#391
+ trace ranges 0x...~0x...
→ 判断 F 的局部语义
```

问题在于，**目前没有真正禁止 Terra 自己扩大 evidence scope**。

Terra contract 里面有：

`Evidence slice: <specific Luna index entries, traces, callers/callees, xrefs>`

很好。

但同时又要求 Terra：

> complete local `explore → test → evidence → conclude` loop

而 Common Task 允许：

> `Starts: exact artifact/function/address/trace/tool/export references`
> `Read: bounded artifacts/functions/address ranges/input manifests`

这里的 **bounded** 没有一个明确的 stop rule。

因此一个很积极的 Terra 完全可能推理：

> “为了完成 local hypothesis test，我还需要 trace，trace 文件就在这里，那我直接 grep/parse。”

它不算公然违反 contract，但已经开始侵占 Luna 的 bulk-evidence lane。

所以逆向 skill 我给：

**职责越权风险：低~中**

**Terra 大量吞 trace 的风险：中等**

不是现在一定会发生，而是**规则存在可解释空间**。

---

### 2. 我会给逆向 Terra 再加一道硬边界

最有效的不是写“尽量不要”，而是明确：

> **Terra may inspect only the bounded trace/evidence slices explicitly supplied by the Task or referenced evidence index. Do not bulk-scan logs, traces, dumps, captures, or candidate corpora. If resolving the local question requires broad search or additional bulk evidence, return the missing evidence query/criteria to the primary coordinator for a Luna evidence pass.**

这样就很干净：

**Terra 可以深挖 300 行关键 trace。**

但不能因为这 300 行不够，就自己：

> `grep 20GB trace`
> `scan all sessions`
> `compare all 200 captures`

它应该返回：

```text
NEED_BULK_EVIDENCE

Question:
Find all executions where F returns state=7
and preceding event != X.

Needed fields:
timestamp
thread
caller
state_before
state_after
raw_ref
```

然后由 coordinator 给 Luna。

Luna 返回 37 个 indexed hits，再交 Terra。

这实际上还能让 **Terra Max 更值钱**：Max token 全花在语义上，而不是花在翻垃圾堆上。

---

## 3. 软件开发 skill 情况不同

开发 skill 里：

**Terra 自己读日志并不天然属于越权。**

因为这里 Terra 的职责明确包括：

* unknown-cause failures
* performance diagnosis
* difficult test failures
* `inspect → implement → test → ordinary repair`

见 `references/decomposition.md:112-118`。

所以例如：

```text
pytest 跑挂
↓
5000 行 failure log
↓
Terra 查 root cause
```

这是完全符合职责的。

甚至如果你强制：

> “所有日志 Terra 都不能读，必须 Luna 先总结”

反而可能降低质量。

因为 root-cause debugging 很容易被日志摘要损失关键信息：

```text
第一个错误出现的位置
异常顺序
warning 和 failure 之间的因果关系
某个状态第一次偏离正常值
```

这些往往需要 Terra 自己看到原始上下文。

所以开发 skill 更合理的边界应该是：

### Terra 可以读日志来解决语义问题

例如：

> 为什么测试失败？

> 哪一步状态首先错误？

> race 从哪里开始？

> 性能回退的 causal chain 是什么？

都可以直接读。

### Luna 负责“批量处理日志”

例如：

> 比较 300 次 CI run；

> 从 80MB 日志提取所有 timeout；

> 生成 compatibility matrix；

> 对 20 个平台的 failure 做相同分类；

> 按已经定义的 schema 找所有 regression。

所以开发 skill 应该是：

```text
需要理解日志含义
        → Terra

需要大量处理日志
        → Luna
```

而不是简单：

```text
日志 → Luna
代码 → Terra
```

这一点你现在的开发 skill 基本是正确的。

---

## 4. 两个 skill 里我真正担心的越权点

我会这样评级：

| 风险                        |   RE skill |  Dev skill |
| ------------------------- | ---------: | ---------: |
| Terra 自己 bulk scan 大日志    |   **⚠️ 中** |        低~中 |
| Terra 做全局架构/全局算法判断        | **⚠️ 低~中** | **⚠️ 低~中** |
| Luna 自己发明函数语义             |      **低** |      不完全适用 |
| Luna 修改冻结 contract        |          低 |    **低~中** |
| Primary 重新做一遍 worker 全部工作 |   **⚠️ 中** |   **⚠️ 中** |
| Worker 为了完成任务无限扩大 scope   |   **⚠️ 中** |   **⚠️ 中** |

其中我认为最重要的不是 Luna，而是 **scope creep**。

比如 RE Terra 本来收到：

```text
分析 function A
```

然后：

```text
A 调 B
→ 看 B
B 调 C/D
→ 看 C/D
发现 trace 很怪
→ 扫整份 trace
发现保护逻辑
→ 开始解释整个 VM
```

这就是典型的 agent 越权路径。

你当前已有一句：

> target expands beyond a tight cluster → escalate

这是对的。

但模型有时会认为：

> “这些都是为了完成 A 的分析，所以仍然属于 local。”

因此最好再规定一个非常具体的原则：

> **Scope is defined by supplied artifacts/ranges and semantic question, not by everything transitively discovered while solving it.**

这句话会非常有效。

---

## 5. 反而 Luna 的逆向边界已经写得比较漂亮

你现在 Luna contract 有一句非常关键：

> `Forbidden: infer global algorithm/protection meaning not stated by the schema`

以及：

> ambiguous/semantic items → record exception

还有：

> accepted mapping propagation **without new semantic invention**

因此 Luna 不太容易合法地把自己升级成“小 Terra”。

比如它可以：

```text
发现 173 个函数符合 pattern P
其中 11 个存在异常
```

但不能自己接着推出：

```text
因此这 173 个都是 VM handlers。
```

我只会再补一句防止它钻空子：

> **Candidate classification must use supplied observable criteria; do not infer new function semantics merely to complete a classification.**

就差不多封死了。

---

# 我的最终判断

**整体分工是合理的，没有结构性越权问题。**

但逆向 skill 目前更多依赖模型“理解职责边界”，还没有做到真正的 **capability boundary**。

尤其是：

> **Terra Max 自己去扫大段/full trace**

这是现在规则下**确实可能发生**的。

我会明确改成：

```text
Luna owns breadth of evidence.
Terra owns depth of local semantics.
Primary owns breadth of semantics.
```

这三句其实很好地定义整个 RE pipeline：

**Luna：证据广度**

**Terra：局部语义深度**

**Daybreak：语义广度 + 全局深度**

于是：

> Terra 读 500 行高度相关 trace：✅

> Terra 扫 500 万行 trace 找 pattern：❌ Luna

> Terra 深入分析 3 个紧耦合函数：✅

> Terra 因此一路扩到 40 个函数恢复整个 VM：❌ Daybreak/重新分解

> Luna 从 500 万行 trace 找异常 cluster：✅

> Luna 根据异常 cluster 判断 VM dispatcher 的真实语义：❌ Terra

如果你要进一步提高这两个 skill 的**稳定性而不是省 token**，我认为现在最值得做的就是给 RE skill 加这两三条明确的 scope-stop 规则，而不是改 Terra/Daybreak 的 effort。
