## User

炸了[Default] [DualBR apply auto] {"accepted": false, "backup_path": "/Users/bytedance/work/reverse_for_fun_mt/analysis/110_arm64/artifact/deobfuscation-cfg/bndb/libmtguard_dualbr_smba_cfg27_predicate_live_validated_20260828.bndb.7.bak", "candidates": [4643116], "error": "existing-indirect-branches-mismatch", "logs": [], "modified": false, "operation": "apply-auto", "root": 4643116, "selected_fragment": 4643116}

## Assistant

这次实际上是安全拒绝，`modified=false`，没有再次写坏 BNDB。新证明已经把 0x46db04 升级为双目标，但事务层仍要求“现有单目标边必须与新双目标完全相等”，因此在写入前报 `existing-indirect-branches-mismatch`。我会沿事务预检与提交后校验定位这道旧约束，只放行“现有目标是新证明目标集合的真子集”的单→双升级。

## Activity

    context compacted

## Assistant

我会用 `bn` 核对 0x46db04 当前单边记录，并按 TDD 修正事务层：只允许“现有单目标是新鲜双目标证明的子集”这一种升级，其他不一致仍拒绝。当前失败发生在写入前，`modified=false`，这份 BNDB 没被本次操作改坏。

## Assistant

现场状态已确认：0x46db04 只记录了 `0x46dc30`，而新鲜投影证明目标是 `{0x46db08, 0x46dc30}`。这是旧单目标元数据被新证明补全，不是目标冲突；我正在把它建模为可回滚的 `exact-upgrade`，避免简单放宽比较后丢失原单边。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/tests/test_boundary_fixed_point.py
    @@ -1394,2 +1394,51 @@
     
    +def test_fresh_dual_proof_monotonically_upgrades_a_matching_single_edge(tmp_path) -> None:
    +    """An incomplete one-entry JUMP_TO map may be completed by fresh raw proof."""
    +
    +    view, root, discovery, guards = _fixture(
    +        tmp_path,
    +        stages=((0x110, 0x200, 0x240),),
    +        inherited_registers=(),
    +    )
    +    view.edges[0x110] = (("aarch64", 0x240),)
    +
    +    report = _service().apply_selected_root(
    +        root,
    +        discovery,
    +        guards,
    +        bounds=FixedPointBounds(max_rounds=3, max_edge_sites=2, max_heads=1),
    +    )
    +
    +    expected = (("aarch64", 0x200), ("aarch64", 0x240))
    +    assert report.converged and report.modified
    +    assert report.written_edges == ((0x110, 0x200, 0x240),)
    +    assert report.rounds[0].edge_actions[0].status == "exact-upgrade"
    +    assert view.edges[0x110] == expected
    +    assert view.edge_writes[0] == (0x110, expected)
    +
    +
    +def test_failed_dual_upgrade_restores_the_exact_prior_single_edge(tmp_path) -> None:
    +    """A single-to-dual write retains its nonempty inverse in the journal."""
    +
    +    view, root, discovery, guards = _fixture(
    +        tmp_path,
    +        stages=((0x110, 0x200, 0x240),),
    +        inherited_registers=(),
    +    )
    +    prior = (("aarch64", 0x240),)
    +    view.edges[0x110] = prior
    +
    +    with pytest.raises(RecoveryError, match="function-workflow-selection-failed"):
    +        _service(fail_derived=True).apply_selected_root(
    +            root,
    +            discovery,
    +            guards,
    +            bounds=FixedPointBounds(max_rounds=3, max_edge_sites=2, max_heads=1),
    +        )
    +
    +    assert view.edges[0x110] == prior
    +    assert view.edge_writes[0][1] == (("aarch64", 0x200), ("aarch64", 0x240))
    +    assert view.edge_writes[-1] == (0x110, prior)
    +
    +
     def test_proven_single_target_computed_branch_writes_one_edge_without_if_rewrite(tmp_path) -> None:

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -1382,3 +1382,3 @@
         false_target: int | None
    -    status: str  # exact-new | exact-existing | mismatch
    +    status: str  # exact-new | exact-upgrade | exact-existing | mismatch
         candidate: Candidate
    @@ -1437,2 +1437,27 @@
     
    +def _is_proven_single_to_dual_edge_upgrade(
    +    observed: set[tuple[object, int]],
    +    expected: set[tuple[object, int]],
    +    candidate: Candidate,
    +) -> bool:
    +    """Admit only a fresh raw dual proof which strictly completes one edge.
    +
    +    Binary Ninja may materialize a register-valued ``JUMP_TO`` with only one
    +    currently known destination.  That one-entry map is not a complete switch
    +    proof.  A new raw projection may replace it only when it preserves the
    +    existing destination, adds exactly one peer, and carries the predicate
    +    capture required to build the conditional Lifted-IL rewrite.
    +    """
    +
    +    return (
    +        len(observed) == 1
    +        and len(expected) == 2
    +        and observed < expected
    +        and candidate.result.is_dual_target
    +        and candidate.capture is not None
    +        and candidate.result.predicate_condition is not None
    +        and candidate.projection in {"raw-resolver", "raw-terminator-overlay"}
    +    )
    +
    +
     def _set_user_indirect_branches(function: object, site: int, pairs: Iterable[tuple[object, int]]) -> None:
    @@ -1635,3 +1660,3 @@
     class _WrittenEdge:
    -    """Exact source-owned inverse record retained only for one transaction."""
    +    """Exact source-owned forward write and its transaction-local inverse."""
     
    @@ -1640,2 +1665,3 @@
         targets: tuple[int, ...]
    +    prior_targets: tuple[int, ...] = ()
     

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -1498,7 +1498,9 @@
             return False
    -    if not targets:
    -        return any(
    -            getattr(item, "source", None) == source_key and getattr(item, "site", None) == site
    -            for item in tuple(getattr(journal, "written_edges", ()))
    -        )
    +    for item in tuple(getattr(journal, "written_edges", ())):
    +        if (
    +            getattr(item, "source", None) == source_key
    +            and getattr(item, "site", None) == site
    +            and _journaled_inverse_targets(getattr(item, "prior_targets", ())) == targets
    +        ):
    +            return True
         for item in tuple(getattr(journal, "retired_edges", ())):
    @@ -4288,2 +4290,3 @@
                 source = _reacquire_source(view, written.source)
    +            prior = tuple(getattr(written, "prior_targets", ()))
                 _restore_journaled_user_indirect_branches(
    @@ -4291,3 +4294,3 @@
                     written.site,
    -                [],
    +                sorted(_target_pairs(source.arch, prior), key=lambda item: item[1]) if prior else [],
                     journal=journal,
    @@ -4295,3 +4298,4 @@
                 )
    -            if _edge_pairs(source, written.site):
    +            expected_prior = _target_pairs(source.arch, prior) if prior else set()
    +            if _edge_pairs(source, written.site) != expected_prior:
                     raise RecoveryError("edge-rollback-audit-failed")
    @@ -4381,3 +4385,5 @@
                 source = _reacquire_source(view, written.source)
    -            if _edge_pairs(source, written.site):
    +            prior = tuple(getattr(written, "prior_targets", ()))
    +            expected_prior = _target_pairs(source.arch, prior) if prior else set()
    +            if _edge_pairs(source, written.site) != expected_prior:
                     raise RecoveryError("edge-rollback-audit-failed")

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -1789,3 +1789,5 @@
         def has_mutation(self) -> bool:
    -        return any(action.status == "exact-new" for action in self.edge_actions) or any(item.accepted for item in self.head_candidates)
    +        return any(action.status in {"exact-new", "exact-upgrade"} for action in self.edge_actions) or any(
    +            item.accepted for item in self.head_candidates
    +        )
     
    @@ -2918,2 +2920,4 @@
                     status = "exact-existing"
    +            elif _is_proven_single_to_dual_edge_upgrade(observed, expected, item):
    +                status = "exact-upgrade"
                 else:

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -3700,3 +3700,5 @@
             prewrite_guard(view)
    -        pending_edges = tuple(action for action in plan.edge_actions if action.status == "exact-new")
    +        pending_edges = tuple(
    +            action for action in plan.edge_actions if action.status in {"exact-new", "exact-upgrade"}
    +        )
             _root_raw_overlay_actions_are_exact(root, journal, pending_edges)
    @@ -3706,4 +3708,9 @@
                     raise RecoveryError("branch-byte-fingerprint-mismatch")
    -            if _edge_pairs(source, action.site):
    -                raise RecoveryError("indirect-edge-state-changed-before-write")
    +            observed = _edge_pairs(source, action.site)
    +            expected = _target_pairs(source.arch, action.targets)
    +            if action.status == "exact-new":
    +                if observed:
    +                    raise RecoveryError("indirect-edge-state-changed-before-write")
    +            elif not _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                raise RecoveryError("existing-indirect-branches-mismatch")
             if pending_edges:
    @@ -3718,5 +3725,13 @@
                 source, source_key = _current_lifted_owner_for_action(root, action)
    -            if _edge_pairs(source, action.site):
    -                raise RecoveryError("indirect-edge-state-changed-before-write")
    -            journal.written_edges.append(_WrittenEdge(source_key, action.site, action.targets))
    +            observed = _edge_pairs(source, action.site)
    +            expected = _target_pairs(source.arch, action.targets)
    +            if action.status == "exact-new":
    +                if observed:
    +                    raise RecoveryError("indirect-edge-state-changed-before-write")
    +                prior_targets: tuple[int, ...] = ()
    +            elif _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                prior_targets = tuple(sorted(target for _architecture, target in observed))
    +            else:
    +                raise RecoveryError("existing-indirect-branches-mismatch")
    +            journal.written_edges.append(_WrittenEdge(source_key, action.site, action.targets, prior_targets))
                 _set_user_indirect_branches(source, action.site, sorted(_target_pairs(source.arch, action.targets), key=lambda item: item[1]))

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -4607,3 +4607,3 @@
                 raise RecoveryError("component-contraction-action-ambiguous")
    -        if getattr(action, "status", None) not in {"exact-new", "exact-existing"}:
    +        if getattr(action, "status", None) not in {"exact-new", "exact-upgrade", "exact-existing"}:
                 continue
    @@ -4639,3 +4639,3 @@
                     raise RecoveryError("component-contraction-real-ingress-unproven")
    -            if getattr(action, "status", None) not in {"exact-new", "exact-existing"}:
    +            if getattr(action, "status", None) not in {"exact-new", "exact-upgrade", "exact-existing"}:
                     raise RecoveryError("component-contraction-ingress-mismatch")
    @@ -4670,3 +4670,5 @@
                 raise RecoveryError("component-contraction-owner-set-empty")
    -        new_actions = tuple(item for item in required_actions if item.status == "exact-new")
    +        new_actions = tuple(
    +            item for item in required_actions if item.status in {"exact-new", "exact-upgrade"}
    +        )
             if not new_actions:

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -3072,2 +3072,5 @@
                         raise RecoveryError("component-contraction-edge-not-empty")
    +            elif action.status == "exact-upgrade":
    +                if not _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                    raise RecoveryError("existing-indirect-branches-mismatch")
                 elif observed != expected:
    @@ -3084,6 +3087,14 @@
                 owner, owner_key = _current_lifted_owner_for_action(root, action)
    -            if _edge_pairs(owner, action.site):
    -                raise RecoveryError("component-contraction-edge-not-empty")
    +            observed = _edge_pairs(owner, action.site)
    +            expected = _target_pairs(owner.arch, action.targets)
    +            if action.status == "exact-new":
    +                if observed:
    +                    raise RecoveryError("component-contraction-edge-not-empty")
    +                prior_targets: tuple[int, ...] = ()
    +            elif _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                prior_targets = tuple(sorted(target for _architecture, target in observed))
    +            else:
    +                raise RecoveryError("existing-indirect-branches-mismatch")
                 _record_action_expectation(action, journal)
    -            journal.written_edges.append(_WrittenEdge(owner_key, action.site, action.targets))
    +            journal.written_edges.append(_WrittenEdge(owner_key, action.site, action.targets, prior_targets))
                 _set_user_indirect_branches(
    @@ -3091,3 +3102,3 @@
                     action.site,
    -                sorted(_target_pairs(owner.arch, action.targets), key=lambda item: item[1]),
    +                sorted(expected, key=lambda item: item[1]),
                 )

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -6342,3 +6342,5 @@
     ) -> None:
    -    pending_edges = sum(action.status == "exact-new" for action in plan.edge_actions)
    +    pending_edges = sum(
    +        action.status in {"exact-new", "exact-upgrade"} for action in plan.edge_actions
    +    )
         pending_heads = sum(item.accepted for item in plan.head_candidates)
    @@ -6346,3 +6348,3 @@
             address = next(
    -            (item.site for item in plan.edge_actions if item.status == "exact-new"),
    +            (item.site for item in plan.edge_actions if item.status in {"exact-new", "exact-upgrade"}),
                 budget_address,

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -3455,3 +3455,7 @@
                         address=next(
    -                        (item.site for item in plan.edge_actions if item.status == "exact-new"),
    +                        (
    +                            item.site
    +                            for item in plan.edge_actions
    +                            if item.status in {"exact-new", "exact-upgrade"}
    +                        ),
                             getattr(root, "start", None),
    @@ -3488,2 +3492,7 @@
                         raise RecoveryError("component-post-delete-edge-not-empty")
    +                prior_targets: tuple[int, ...] = ()
    +            elif action.status == "exact-upgrade":
    +                if not _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                    raise RecoveryError("existing-indirect-branches-mismatch")
    +                prior_targets = tuple(sorted(target for _architecture, target in observed))
                 elif reissue_existing:
    @@ -3505,3 +3514,5 @@
                 else:
    -                journal.written_edges.append(_WrittenEdge(source_key, action.site, action.targets))
    +                journal.written_edges.append(
    +                    _WrittenEdge(source_key, action.site, action.targets, prior_targets)
    +                )
                     _set_user_indirect_branches(
    @@ -6071,3 +6082,3 @@
             if not ingress:
    -            if action.status == "exact-new":
    +            if action.status in {"exact-new", "exact-upgrade"}:
                     saw_non_ingress = True
    @@ -6079,3 +6090,3 @@
                 continue
    -        if action.status not in {"exact-new", "exact-existing"}:
    +        if action.status not in {"exact-new", "exact-upgrade", "exact-existing"}:
                 raise RecoveryError("component-post-delete-action-not-new")
    @@ -6098,2 +6109,5 @@
                     raise RecoveryError("component-post-delete-edge-not-empty")
    +        elif action.status == "exact-upgrade":
    +            if not _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                raise RecoveryError("existing-indirect-branches-mismatch")
             elif observed != expected:

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -3961,3 +3961,3 @@
     
    -        pending: list[tuple[EdgeAction, object, FunctionKey]] = []
    +        pending: list[tuple[EdgeAction, object, FunctionKey, tuple[int, ...]]] = []
             for action in fresh.edge_actions:
    @@ -3974,7 +3974,9 @@
                 observed = _edge_pairs(owner, action.site)
    -            if observed and observed != expected:
    +            upgrade = _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate)
    +            if observed and observed != expected and not upgrade:
                     raise RecoveryError("existing-indirect-branches-mismatch")
    -            _record_reconciled_edge_expectation(journal, owner_key, action, bool(observed))
    -            if not observed:
    -                pending.append((action, owner, owner_key))
    +            _record_reconciled_edge_expectation(journal, owner_key, action, observed == expected)
    +            if not observed or upgrade:
    +                prior_targets = tuple(sorted(target for _architecture, target in observed))
    +                pending.append((action, owner, owner_key, prior_targets))
     
    @@ -3995,3 +3997,3 @@
             guards.verify_file_integrity(root.view)
    -        for action, owner, owner_key in pending:
    +        for action, owner, owner_key, prior_targets in pending:
                 # Journal before the native setter: it can commit and still raise.
    @@ -3999,3 +4001,12 @@
                 # source identity from a pre-merge plan.
    -            journal.written_edges.append(_WrittenEdge(owner_key, action.site, action.targets))
    +            observed = _edge_pairs(owner, action.site)
    +            expected = _target_pairs(owner.arch, action.targets)
    +            if prior_targets:
    +                if not _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                    raise RecoveryError("existing-indirect-branches-mismatch")
    +            elif observed:
    +                raise RecoveryError("indirect-edge-state-changed-before-write")
    +            journal.written_edges.append(
    +                _WrittenEdge(owner_key, action.site, action.targets, prior_targets)
    +            )
                 _set_user_indirect_branches(
    @@ -4003,5 +4014,8 @@
                     action.site,
    -                sorted(_target_pairs(owner.arch, action.targets), key=lambda item: item[1]),
    +                sorted(expected, key=lambda item: item[1]),
                 )
    -        for owner_key in sorted({owner_key for _action, _owner, owner_key in pending}, key=lambda item: item.canonical()):
    +        for owner_key in sorted(
    +            {owner_key for _action, _owner, owner_key, _prior in pending},
    +            key=lambda item: item.canonical(),
    +        ):
                 _full_auto_reanalyze(_reacquire_source(root.view, owner_key))

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/isolated_apply_worker.py
    @@ -77,2 +77,3 @@
         _head_source_revalidation_reason,
    +    _is_proven_single_to_dual_edge_upgrade,
         _lifted_rewrite_present,
    @@ -2971,3 +2972,3 @@
             ranges = tuple(bound for record in removed for bound in record.block_ranges)
    -        pending: list[tuple[object, object, FunctionKey]] = []
    +        pending: list[tuple[object, object, FunctionKey, tuple[int, ...]]] = []
             for action in post.edge_actions:
    @@ -2977,7 +2978,10 @@
                 expected, observed = _target_pairs(owner.arch, action.targets), _edge_pairs(owner, action.site)
    -            if observed and observed != expected:
    +            upgrade = _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate)
    +            if observed and observed != expected and not upgrade:
                     raise RecoveryError("existing-indirect-branches-mismatch")
    -            _record_reconciled_edge_expectation(journal, owner_key, action, bool(observed))
    -            if not observed:
    -                pending.append((action, owner, owner_key))
    +            _record_reconciled_edge_expectation(journal, owner_key, action, observed == expected)
    +            if not observed or upgrade:
    +                pending.append(
    +                    (action, owner, owner_key, tuple(sorted(target for _architecture, target in observed)))
    +                )
             if not pending:
    @@ -2985,6 +2989,17 @@
             guards.verify_file_integrity(root.view)
    -        for action, owner, owner_key in pending:
    -            journal.written_edges.append(_WrittenEdge(owner_key, action.site, action.targets))
    -            _set_user_indirect_branches(owner, action.site, sorted(_target_pairs(owner.arch, action.targets), key=lambda item: item[1]))
    -        for owner_key in sorted({owner_key for _action, _owner, owner_key in pending}, key=lambda item: item.canonical()):
    +        for action, owner, owner_key, prior_targets in pending:
    +            observed, expected = _edge_pairs(owner, action.site), _target_pairs(owner.arch, action.targets)
    +            if prior_targets:
    +                if not _is_proven_single_to_dual_edge_upgrade(observed, expected, action.candidate):
    +                    raise RecoveryError("existing-indirect-branches-mismatch")
    +            elif observed:
    +                raise RecoveryError("indirect-edge-state-changed-before-write")
    +            journal.written_edges.append(
    +                _WrittenEdge(owner_key, action.site, action.targets, prior_targets)
    +            )
    +            _set_user_indirect_branches(owner, action.site, sorted(expected, key=lambda item: item[1]))
    +        for owner_key in sorted(
    +            {owner_key for _action, _owner, owner_key, _prior in pending},
    +            key=lambda item: item.canonical(),
    +        ):
                 _full_auto_reanalyze(_reacquire_source(root.view, owner_key))

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -5912,3 +5912,7 @@
     
    -    pending = tuple(action for action in actions if getattr(action, "status", None) == "exact-new")
    +    pending = tuple(
    +        action
    +        for action in actions
    +        if getattr(action, "status", None) in {"exact-new", "exact-upgrade"}
    +    )
         if not pending:

## Assistant

回归测试已经从“预检直接拒绝”转为通过，并验证了失败回滚会恢复原来的单目标边。接下来我会跑完整测试，再补一条组件收缩路径测试，确保 0x46d92c 这种存在错误函数头的真实路径也走同一套升级逻辑。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/tests/test_component_contraction.py
    @@ -136,2 +136,21 @@
     
    +def test_leaf_contraction_stages_a_proven_single_to_dual_upgrade() -> None:
    +    """A matching one-entry map is still pending ingress, not exact state."""
    +
    +    edge = _action(0x520, 0x500, 0x300, 0x340, status="exact-upgrade")
    +    plan = _plan(
    +        (edge,),
    +        (_head(0x300, _resolver(0x520, 0x500)),),
    +        (_key(0x100), _key(0x300), _key(0x500)),
    +        ((_key(0x500), _key(0x300), "resolver-target", 0x520),),
    +    )
    +
    +    step = workflow._select_component_contraction(plan)
    +
    +    assert step.mode == "leaf"
    +    assert step.write_actions == (edge,)
    +    assert step.required_actions == (edge,)
    +    assert step.delete_head.start == 0x300
    +
    +
     def test_leaf_contraction_uses_the_current_owner_of_an_exact_interior_semantic_target() -> None:

## Assistant

源代码和打包产物均通过 872 项测试，组件收缩也会把 `exact-upgrade` 当作待写入边处理。现在我安装新包；由于 BN 已加载旧 Python 模块，安装后需要重启 BN 才会真正启用。

## Assistant

已修复并安装新插件。

原因：0x46db04 已有单目标 `0x46dc30`，新证明补全为 `{0x46db08, 0x46dc30}`，旧事务层误判为冲突。现在支持可回滚的单→双目标升级，异常时恢复原单边。

- 872 项测试通过
- `.7.bak` 对应操作未修改原 BNDB
- 请重启 Binary Ninja，再对 0x46d92c 执行 Auto。

## Assistant

这次不再按单个 case 补丁处理。我会用 `bn` 先枚举当前 Tags 中仍未修复的 DualBR 间接跳转，建立多地址回归集；再按 TDD 修复 `root-user-type-restore-audit-failed`，反复在独立备份上验证多个根函数，直到成功路径、拒绝路径和回滚都稳定。先保持当前 BNDB 只读。

## Activity

    file changes: Completed · 1 changes
    Add: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/scan_tagged_dualbr_candidates.py
    """Read-only classify unresolved-indirect tags with the installed DualBR prover.
    
    Run through ``bn py exec --script`` against the active GUI view.  The script
    does not register workflows, write edges, remove function heads, or save the
    database; it only projects the exact tagged native BR sites owned by each
    current function.
    """
    
    from __future__ import annotations
    
    from collections import defaultdict
    
    from dualjump.adapter import BinaryNinjaDiscovery
    from dualjump.runtime import get_runtime
    
    
    tag_type = bv.tag_types["Unresolved Indirect Control Flow"]
    tagged_by_root: dict[int, set[int]] = defaultdict(set)
    ambiguous: list[dict[str, object]] = []
    
    for site, _tag in bv.tags_by_type(tag_type):
        owners = tuple(bv.get_functions_containing(site))
        if len(owners) != 1:
            ambiguous.append(
                {
                    "site": hex(int(site)),
                    "owners": [hex(int(owner.start)) for owner in owners],
                }
            )
            continue
        tagged_by_root[int(owners[0].start)].add(int(site))
    
    discovery = BinaryNinjaDiscovery(get_runtime().config)
    roots: list[dict[str, object]] = []
    for root_start, tagged_sites in sorted(tagged_by_root.items()):
        function = bv.get_function_at(root_start)
        if function is None:
            roots.append(
                {
                    "root": hex(root_start),
                    "tagged_sites": [hex(site) for site in sorted(tagged_sites)],
                    "error": "exact-current-root-missing",
                }
            )
            continue
        try:
            session = discovery.discover_function(
                function,
                function.lifted_il,
                raw_terminator_overlay=True,
                raw_terminator_sites=tuple(sorted(tagged_sites)),
            )
            accepted = [
                {
                    "site": hex(int(candidate.site)),
                    "targets": [hex(int(target)) for target in candidate.result.targets],
                    "projection": candidate.projection,
                    "reason": candidate.result.reason,
                    "dual": bool(candidate.result.is_dual_target),
                }
                for candidate in session.report.candidates
                if candidate.result.accepted and candidate.site in tagged_sites
            ]
            rejected = [
                {
                    "site": hex(int(candidate.site)),
                    "projection": candidate.projection,
                    "reason": candidate.result.reason,
                }
                for candidate in session.report.rejected
                if candidate.site in tagged_sites
            ]
            current_edges = {}
            for site in sorted(tagged_sites):
                current_edges[hex(site)] = [
                    hex(int(edge.dest_addr))
                    for edge in function.get_indirect_branches_at(site)
                ]
            roots.append(
                {
                    "root": hex(root_start),
                    "name": function.name,
                    "type": str(function.type),
                    "has_user_type": bool(function.has_user_type),
                    "tagged_sites": [hex(site) for site in sorted(tagged_sites)],
                    "current_edges": current_edges,
                    "accepted": accepted,
                    "rejected": rejected,
                }
            )
        except Exception as error:
            roots.append(
                {
                    "root": hex(root_start),
                    "name": function.name,
                    "tagged_sites": [hex(site) for site in sorted(tagged_sites)],
                    "error": f"{type(error).__name__}: {error}",
                }
            )
    
    result = {
        "snapshot": int(bv.file.database.current_snapshot.id),
        "tag_count": sum(len(sites) for sites in tagged_by_root.values()) + len(ambiguous),
        "root_count": len(tagged_by_root),
        "accepted_dual_roots": [
            item["root"]
            for item in roots
            if any(candidate["dual"] for candidate in item.get("accepted", ()))
        ],
        "ambiguous": ambiguous,
        "roots": roots,
    }

## Assistant

只读扫描完成：当前 65 个未解析间接流 Tag 中，直接由现有 DualBR 证明器确认的未修复双目标根有 4 个：`0x50d588`、`0x51e970`、`0x51f030`、`0x525dc4`。它们都会进入多 case 回归；其余大量多所有者/真 switch 暂不混入修复集合。现在先在 `.10.bak` 的独立副本重现类型恢复错误并采集期望/实际类型。

## Activity

    file changes: Completed · 1 changes
    Add: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_isolated_root_apply.py
    """Run one source-tree DualBR Apply against disposable BNDB stages.
    
    This is a test driver, not a plugin entrypoint.  The caller prepares two
    byte-identical input copies under this directory and supplies the exact root
    and database snapshot.  The isolated worker owns all mutation and output.
    """
    
    from __future__ import annotations
    
    from dataclasses import asdict
    from hashlib import sha256
    import json
    import os
    from pathlib import Path
    import sys
    
    
    HERE = Path(__file__).resolve().parent
    PROJECT = HERE.parents[1]
    SOURCE = PROJECT / "src"
    BNPYTHON = "/Applications/Binary Ninja.app/Contents/MacOS/bnpython3"
    ENTRYPOINT = PROJECT / "scripts" / "isolated_preview_worker_entry.py"
    
    
    def _inside_here(value: str) -> Path:
        path = Path(value).resolve()
        if HERE not in path.parents or path == HERE:
            raise SystemExit("path-outside-multi-case-validation")
        return path
    
    
    def _sha256(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    
    
    def main() -> None:
        if os.environ.get("BN_DISABLE_USER_PLUGINS") != "1":
            raise SystemExit("BN_DISABLE_USER_PLUGINS=1-required")
        if len(sys.argv) != 7:
            raise SystemExit(
                "usage: run_isolated_root_apply.py ROOT SNAPSHOT ACTIVE ROLLBACK OUTPUT REPORT"
            )
        root = int(sys.argv[1], 0)
        snapshot = int(sys.argv[2], 0)
        active, rollback, output, report = (_inside_here(value) for value in sys.argv[3:])
        if (
            root < 0
            or snapshot < 0
            or not active.is_file()
            or not rollback.is_file()
            or output.exists()
            or report.suffix != ".json"
        ):
            raise SystemExit("invalid-disposable-stage")
        if str(SOURCE) not in sys.path:
            sys.path.insert(0, str(SOURCE))
    
        from dualjump.isolated_worker import IsolatedWorkerSupervisor, WorkerChannels, WorkerRequest
        from dualjump.whole_view import FunctionKey, WholeViewBounds
    
        baseline = _sha256(active)
        if _sha256(rollback) != baseline:
            raise SystemExit("rollback-hash-mismatch")
        selected = FunctionKey(baseline, root, "aarch64", "linux-aarch64")
        request_id = f"multi-case-{root:x}"
        request = WorkerRequest(
            active_stage_path=active,
            rollback_path=rollback,
            output_stage_path=output,
            disposable_root=active.parent,
            baseline_sha256=baseline,
            baseline_snapshot=snapshot,
            bounds=WholeViewBounds(max_inbound_refs_per_head=4096),
            overall_timeout_seconds=1800.0,
            no_progress_timeout_seconds=600.0,
            channels=WorkerChannels(active.parent / f"{request_id}.cancel"),
            operation="apply",
            selected_function=selected,
            request_id=request_id,
        )
        payload: dict[str, object] = {
            "active": str(active),
            "rollback": str(rollback),
            "output": str(output),
            "baseline_sha256": baseline,
            "snapshot": snapshot,
            "selected": selected.canonical(),
            "workflow_sha256": _sha256(SOURCE / "dualjump" / "workflow.py"),
        }
        try:
            outcome = IsolatedWorkerSupervisor((BNPYTHON, str(ENTRYPOINT))).run(request)
            payload["outcome"] = asdict(outcome)
            payload["output_sha256"] = _sha256(output) if output.is_file() else None
        except BaseException as error:
            payload["error"] = f"{type(error).__name__}: {error}"
        report.write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=repr),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "report": str(report),
                    "accepted": payload.get("outcome", {}).get("accepted")
                    if isinstance(payload.get("outcome"), dict)
                    else None,
                    "error": payload.get("error"),
                    "output_present": output.is_file(),
                },
                sort_keys=True,
            )
        )
    
    
    if __name__ == "__main__":
        main()

## Activity

    file changes: Completed · 1 changes
    Add: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    """Exercise the exact GUI/AI three-operation backend on one disposable BNDB.
    
    Each invocation runs in a fresh ``bnpython3`` process with user plugins
    disabled.  It captures root type/range/edge state and traces the production
    root-user-type restoration boundary without changing its decision.
    """
    
    from __future__ import annotations
    
    import json
    import os
    from pathlib import Path
    import sys
    
    
    HERE = Path(__file__).resolve().parent
    PROJECT = HERE.parents[1]
    SOURCE = PROJECT / "src"
    
    
    def _inside_here(value: str) -> Path:
        path = Path(value).resolve()
        if HERE not in path.parents or path == HERE:
            raise SystemExit("path-outside-multi-case-validation")
        return path
    
    
    def _root_state(view, root_start: int) -> dict[str, object]:
        function = view.get_function_at(root_start)
        if function is None:
            return {"missing": True}
        sites = []
        try:
            for instruction in function.low_level_il.instructions:
                if instruction.operation.name not in {"LLIL_JUMP", "LLIL_JUMP_TO", "LLIL_TAILCALL"}:
                    continue
                raw = bytes(view.read(instruction.address, 4))
                if len(raw) != 4 or (int.from_bytes(raw, "little") & 0xFFFFFC1F) != 0xD61F0000:
                    continue
                sites.append(
                    {
                        "site": hex(int(instruction.address)),
                        "operation": instruction.operation.name,
                        "edges": [
                            hex(int(edge.dest_addr))
                            for edge in function.get_indirect_branches_at(instruction.address)
                        ],
                    }
                )
        except Exception as error:
            sites.append({"error": f"{type(error).__name__}: {error}"})
        workflow = getattr(getattr(function, "workflow", None), "name", None)
        return {
            "missing": False,
            "name": function.name,
            "has_user_type": bool(function.has_user_type),
            "type": str(function.type),
            "workflow": workflow,
            "ranges": [[hex(int(item.start)), hex(int(item.end))] for item in function.address_ranges],
            "indirect_sites": sites,
        }
    
    
    def main() -> None:
        if os.environ.get("BN_DISABLE_USER_PLUGINS") != "1":
            raise SystemExit("BN_DISABLE_USER_PLUGINS=1-required")
        if len(sys.argv) != 4:
            raise SystemExit("usage: run_live_backend_case.py ROOT ACTIVE REPORT")
        root_start = int(sys.argv[1], 0)
        active = _inside_here(sys.argv[2])
        report = _inside_here(sys.argv[3])
        if root_start < 0 or not active.is_file() or report.suffix != ".json":
            raise SystemExit("invalid-case-input")
        if str(SOURCE) not in sys.path:
            sys.path.insert(0, str(SOURCE))
    
        import binaryninja
        from dualjump.adapter import BinaryNinjaDiscovery
        from dualjump.config import load_config
        from dualjump.workflow import (
            ApplyService,
            BinaryNinjaActivityFactory,
            BinaryNinjaApplyHost,
            BinaryNinjaWorkflowFactory,
            DerivedWorkflowRegistry,
            ThreeOperationBackend,
            make_current_pass_rewrite_action,
        )
        import dualjump.workflow as workflow_module
    
        view = binaryninja.load(str(active), update_analysis=False)
        traces: list[dict[str, object]] = []
        phases: list[dict[str, object]] = []
        original_restore = workflow_module._restore_root_user_type
    
        def traced_restore(view_arg, start, architecture, platform, journal, *, reanalyze):
            trace = {
                "root": hex(int(start)),
                "reanalyze": bool(reanalyze),
                "expected_present": bool(journal.root_user_type_present),
                "expected_type": journal.root_user_type_text,
                "before": _root_state(view_arg, int(start)),
            }
            try:
                restored = original_restore(
                    view_arg,
                    start,
                    architecture,
                    platform,
                    journal,
                    reanalyze=reanalyze,
                )
            except BaseException as error:
                trace["error"] = f"{type(error).__name__}: {error}"
                trace["after"] = _root_state(view_arg, int(start))
                traces.append(trace)
                raise
            trace["after"] = _root_state(view_arg, int(start))
            traces.append(trace)
            return restored
    
        workflow_module._restore_root_user_type = traced_restore
        payload: dict[str, object] = {
            "root": hex(root_start),
            "active": str(active),
            "snapshot": int(view.file.database.current_snapshot.id),
            "modified_before": bool(view.modified),
            "before": _root_state(view, root_start),
        }
        try:
            config = load_config()
            discovery = BinaryNinjaDiscovery(config)
            registry = DerivedWorkflowRegistry(
                BinaryNinjaWorkflowFactory(),
                BinaryNinjaActivityFactory(),
                make_current_pass_rewrite_action(discovery),
            )
            host = BinaryNinjaApplyHost(
                ApplyService(registry),
                BinaryNinjaDiscovery(config),
                config=config,
            )
            backend = ThreeOperationBackend(host, registry)
            function = view.get_function_at(root_start)
            if function is None:
                raise RuntimeError("exact-current-root-missing")
            operation = backend.apply_auto(function, phase_sink=phases.append)
            payload["operation"] = operation.as_dict()
        except BaseException as error:
            payload["driver_error"] = f"{type(error).__name__}: {error}"
        finally:
            workflow_module._restore_root_user_type = original_restore
            payload["modified_after"] = bool(view.modified)
            payload["after"] = _root_state(view, root_start)
            payload["restore_traces"] = traces
            payload["phases"] = phases
            view.file.close()
        report.write_text(
            json.dumps(payload, indent=2, sort_keys=True, default=repr),
            encoding="utf-8",
        )
        print(
            json.dumps(
                {
                    "report": str(report),
                    "accepted": payload.get("operation", {}).get("accepted")
                    if isinstance(payload.get("operation"), dict)
                    else None,
                    "error": payload.get("operation", {}).get("error")
                    if isinstance(payload.get("operation"), dict)
                    else payload.get("driver_error"),
                    "modified_after": payload.get("modified_after"),
                },
                sort_keys=True,
            )
        )
    
    
    if __name__ == "__main__":
        main()

## Assistant

已复现并拿到关键证据：修复过程中函数边界从 `0x50d588–0x50d5f8` 扩展到 `0x50d588–0x50d7bc`，工作流把签名推断成 `void*()`；插件尝试恢复原用户类型 `int64_t()` 后，再次 FullAuto 又把它覆盖回 `void*()`，于是审计失败并正确回滚。下一步会区分“setter 未生效”和“后续重分析覆盖”，再决定是重建类型对象还是调整恢复时序。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -92,5 +92,25 @@
         traces: list[dict[str, object]] = []
    +    type_set_traces: list[dict[str, object]] = []
         phases: list[dict[str, object]] = []
         original_restore = workflow_module._restore_root_user_type
    +    original_set_user_type = binaryninja.Function.set_user_type
     
    +    def traced_set_user_type(function, user_type):
    +        trace = {
    +            "root": hex(int(function.start)),
    +            "requested": str(user_type),
    +            "before": str(function.type),
    +            "before_present": bool(function.has_user_type),
    +        }
    +        try:
    +            result = original_set_user_type(function, user_type)
    +        except BaseException as error:
    +            trace["error"] = f"{type(error).__name__}: {error}"
    +            type_set_traces.append(trace)
    +            raise
    +        trace["after"] = str(function.type)
    +        trace["after_present"] = bool(function.has_user_type)
    +        type_set_traces.append(trace)
    +        return result
    +
         def traced_restore(view_arg, start, architecture, platform, journal, *, reanalyze):
    @@ -122,2 +142,3 @@
         workflow_module._restore_root_user_type = traced_restore
    +    binaryninja.Function.set_user_type = traced_set_user_type
         payload: dict[str, object] = {
    @@ -152,2 +173,3 @@
             workflow_module._restore_root_user_type = original_restore
    +        binaryninja.Function.set_user_type = original_set_user_type
             payload["modified_after"] = bool(view.modified)
    @@ -155,2 +177,3 @@
             payload["restore_traces"] = traces
    +        payload["type_set_traces"] = type_set_traces
             payload["phases"] = phases

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/root_type_restore_evidence.json
    @@ -1,3 +1,14 @@
     {
    -  "acceptance_criteria": [],
    +  "acceptance_criteria": [
    +    {
    +      "id": "AC-root-type-current-epoch",
    +      "requirement_ids": [
    +        "R-root-type-current-epoch"
    +      ],
    +      "description": "A saved user function type is restored through the documented string parser when its captured Binary Ninja Type handle cannot be applied after CFG topology changes.",
    +      "test_ids": [
    +        "T-root-type-current-epoch"
    +      ]
    +    }
    +  ],
       "artifacts": [],
    @@ -9,3 +20,3 @@
         "tdd_mode": "red_green_refactor",
    -    "tdd_ready": false,
    +    "tdd_ready": true,
         "type": "bugfix"
    @@ -30,3 +41,8 @@
       },
    -  "requirements": [],
    +  "requirements": [
    +    {
    +      "id": "R-root-type-current-epoch",
    +      "statement": "DualBR Apply must preserve an analyst user function type when CFG recovery replaces the current Function topology, while retaining exact audit and rollback behavior."
    +    }
    +  ],
       "risk_traits": [],
    @@ -34,4 +50,32 @@
       "schema_version": "2.0",
    -  "targets": [],
    -  "tdd_cycles": [],
    +  "targets": [
    +    {
    +      "language": "python",
    +      "paths": [
    +        "analysis/Dual_jump_deobf/src/dualjump/workflow.py",
    +        "analysis/Dual_jump_deobf/tests/test_boundary_fixed_point.py"
    +      ],
    +      "package_or_module": "dualjump.workflow",
    +      "public_entrypoints": [
    +        "BoundaryFixedPointService.apply_selected_root"
    +      ]
    +    }
    +  ],
    +  "tdd_cycles": [
    +    {
    +      "id": "C-root-type-current-epoch",
    +      "mode": "red_green_refactor",
    +      "acceptance_criterion_ids": [
    +        "AC-root-type-current-epoch"
    +      ],
    +      "test_ids": [
    +        "T-root-type-current-epoch"
    +      ],
    +      "refactor": {
    +        "decision": "not_needed",
    +        "behavior_preservation": "Pending the minimum Green implementation."
    +      },
    +      "regression": {}
    +    }
    +  ],
       "test_sufficiency": {
    @@ -54,19 +98,20 @@
       },
    -  "tests": [],
    -  "unsupported_claims": [
    +  "tests": [
         {
    -      "claim": "Engineering readiness",
    -      "disposition": "blocking",
    -      "id": "draft-not-yet-verified",
    -      "reason": "This draft was generated before requirements, tests, and execution evidence were recorded.",
    -      "related_fields": [
    -        "requirements",
    -        "acceptance_criteria",
    -        "tests",
    -        "tdd_cycles",
    -        "regression"
    +      "id": "T-root-type-current-epoch",
    +      "path": "analysis/Dual_jump_deobf/tests/test_boundary_fixed_point.py",
    +      "framework": "pytest",
    +      "level": "component",
    +      "selector": "analysis/Dual_jump_deobf/tests/test_boundary_fixed_point.py::test_root_user_type_restore_reparses_a_stale_type_for_the_current_cfg_epoch",
    +      "acceptance_criterion_ids": [
    +        "AC-root-type-current-epoch"
           ],
    -      "scope": "change"
    +      "case_kinds": [
    +        "positive",
    +        "state",
    +        "error"
    +      ]
         }
    -  ]
    +  ],
    +  "unsupported_claims": []
     }

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/tests/test_boundary_fixed_point.py
    @@ -362,2 +362,4 @@
             self.view.user_type_writes.append(value)
    +        if self.view.ignore_non_string_user_type_writes and not isinstance(value, str):
    +            return
             self.view.user_type = value
    @@ -443,2 +445,3 @@
             self.user_type_writes = []
    +        self.ignore_non_string_user_type_writes = False
             self.degrade_user_type_after_workflow = False
    @@ -954,2 +957,47 @@
     
    +def test_root_user_type_restore_reparses_a_stale_type_for_the_current_cfg_epoch(tmp_path) -> None:
    +    """A stale BN Type handle falls back to the documented string setter.
    +
    +    Real Binary Ninja can keep ``has_user_type`` true while refusing to apply
    +    a FunctionType handle captured before function-head contraction.  Parsing
    +    the exact rendered type against the current view creates a handle valid
    +    for the rebuilt Function epoch without weakening the final exact audit.
    +    """
    +
    +    class EpochBoundType:
    +        def __init__(self, text: str) -> None:
    +            self.text = text
    +
    +        def immutable_copy(self):
    +            return EpochBoundType(self.text)
    +
    +        def __str__(self) -> str:
    +            return self.text
    +
    +    view, root, _discovery, _guards = _fixture(tmp_path, stages=())
    +    original = EpochBoundType("int64_t()")
    +    view.user_type_present = True
    +    view.user_type = original
    +    snapshot = _snapshot_root_user_type(root)
    +    journal = _FixedPointJournal(ROOT, view.workflow, "default")
    +    _seed_root_user_type_snapshot(journal, snapshot)
    +    view.user_type = "void*()"
    +    view.ignore_non_string_user_type_writes = True
    +
    +    restored = _restore_root_user_type(
    +        view,
    +        ROOT,
    +        root.arch,
    +        root.platform,
    +        journal,
    +        reanalyze=False,
    +    )
    +
    +    assert str(restored.type) == "int64_t()"
    +    assert len(view.user_type_writes) == 2
    +    assert view.user_type_writes[0] is snapshot.user_type
    +    assert view.user_type_writes[1] == "int64_t()"
    +    assert journal.root_user_type_restored is True
    +
    +
     def test_rollback_restores_the_captured_root_user_type_after_a_failed_transaction(tmp_path) -> None:

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/.gitignore
    @@ -3,2 +3,3 @@
     .DS_Store
    +.venv/
     build/

## Assistant

TDD Red 正在生成 Git 快照证据；由于工作区里已有大量 BNDB/历史产物，快照哈希阶段比测试本身慢，进程仍在运行而非卡死。我会等它完成后继续，后续测试产物会限制在专用目录。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/.git/info/exclude
    @@ -6 +6,11 @@
     # *~
    +
    +# Local reverse-engineering runtime artifacts; never source evidence.
    +analysis/110_arm64/artifact/deobfuscation-cfg/bndb/*.bak
    +analysis/110_arm64/artifact/deobfuscation-cfg/bndb/backups/
    +analysis/110_arm64/artifact/deobfuscation-cfg/bndb/*_20260828*.bndb
    +analysis/110_arm64/artifact/deobfuscation-cfg/plugin-backups/
    +analysis/Dual_jump_deobf/draft/multi_case_validation/**/*.bndb
    +analysis/Dual_jump_deobf/draft/multi_case_validation/**/*.bndb.bak
    +analysis/Dual_jump_deobf/.venv/
    +analysis/SMBA_deobf/bn-cobra-mba/third_party/

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -7210,9 +7210,36 @@
             raise RecoveryError("root-user-type-snapshot-invalid")
    -    setter = getattr(root, "set_user_type", None)
    -    if not callable(setter):
    -        raise RecoveryError("root-user-type-restore-unavailable")
    +    def current_type_matches(current) -> bool:
    +        try:
    +            return bool(getattr(current, "has_user_type")) and str(getattr(current, "type")) == journal.root_user_type_text
    +        except Exception as error:
    +            raise RecoveryError("root-user-type-restore-audit-failed") from error
    +
    +    def set_current_type(current, value) -> None:
    +        setter = getattr(current, "set_user_type", None)
    +        if not callable(setter):
    +            raise RecoveryError("root-user-type-restore-unavailable")
    +        try:
    +            setter(value)
    +        except Exception as error:
    +            raise RecoveryError("root-user-type-restore-failed") from error
    +
    +    # A Binary Ninja FunctionType handle captured before function-head
    +    # contraction can remain printable but no longer apply to the rebuilt
    +    # Function epoch.  Try the lossless immutable object first.  If exact
    +    # readback fails, use the documented StringOrType setter so Binary Ninja
    +    # reparses the same rendering against the current view/type namespace.
         try:
    -        setter(journal.root_user_type)
    -    except Exception as error:
    -        raise RecoveryError("root-user-type-restore-failed") from error
    +        set_current_type(root, journal.root_user_type)
    +        root = _reacquire_root(view, root_start, architecture, platform)
    +        object_applied = current_type_matches(root)
    +    except RecoveryError as error:
    +        if error.reason not in {"root-user-type-restore-failed", "root-user-type-restore-audit-failed"}:
    +            raise
    +        object_applied = False
    +    if not object_applied:
    +        root = _reacquire_root(view, root_start, architecture, platform)
    +        set_current_type(root, journal.root_user_type_text)
    +        root = _reacquire_root(view, root_start, architecture, platform)
    +        if not current_type_matches(root):
    +            raise RecoveryError("root-user-type-restore-audit-failed")
         if reanalyze:
    @@ -7220,8 +7247,9 @@
             root = _reacquire_root(view, root_start, architecture, platform)
    -    try:
    -        restored_present = bool(getattr(root, "has_user_type"))
    -        restored_text = str(getattr(root, "type"))
    -    except Exception as error:
    -        raise RecoveryError("root-user-type-restore-audit-failed") from error
    -    if not restored_present or restored_text != journal.root_user_type_text:
    +        # FullAuto can itself replace the Function epoch.  Reparse once more
    +        # only when the exact user type did not survive that boundary; do not
    +        # trigger another FullAuto cycle after the final metadata restore.
    +        if not current_type_matches(root):
    +            set_current_type(root, journal.root_user_type_text)
    +            root = _reacquire_root(view, root_start, architecture, platform)
    +    if not current_type_matches(root):
             raise RecoveryError("root-user-type-restore-audit-failed")

## Activity

    context compacted

## Assistant

我继续沿着真实失败路径查：当前证据表明函数边界扩展后，BN 连续接收 `set_user_type(Type)` 和 `set_user_type(str)` 都立即无效。下一步先在一次性数据库里验证“清除旧 user type 再恢复”是否能打破这个失效状态，不会碰你当前打开的 BNDB。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -77,2 +77,3 @@
         import binaryninja
    +    from binaryninja import _binaryninjacore as binaryninja_core
         from dualjump.adapter import BinaryNinjaDiscovery
    @@ -124,10 +125,51 @@
             try:
    -            restored = original_restore(
    -                view_arg,
    -                start,
    -                architecture,
    -                platform,
    -                journal,
    -                reanalyze=reanalyze,
    -            )
    +            try:
    +                restored = original_restore(
    +                    view_arg,
    +                    start,
    +                    architecture,
    +                    platform,
    +                    journal,
    +                    reanalyze=reanalyze,
    +                )
    +            except BaseException as original_error:
    +                if (
    +                    os.environ.get("DUALBR_DIAGNOSTIC_CLEAR_USER_TYPE") != "1"
    +                    or getattr(original_error, "reason", None)
    +                    != "root-user-type-restore-audit-failed"
    +                ):
    +                    raise
    +                current = workflow_module._reacquire_root(
    +                    view_arg,
    +                    start,
    +                    architecture,
    +                    platform,
    +                )
    +                clear_trace = {
    +                    "root": hex(int(current.start)),
    +                    "operation": "core-clear-user-type",
    +                    "before": str(current.type),
    +                    "before_present": bool(current.has_user_type),
    +                }
    +                binaryninja_core.BNSetFunctionUserType(current.handle, None)
    +                current = workflow_module._reacquire_root(
    +                    view_arg,
    +                    start,
    +                    architecture,
    +                    platform,
    +                )
    +                clear_trace["after"] = str(current.type)
    +                clear_trace["after_present"] = bool(current.has_user_type)
    +                type_set_traces.append(clear_trace)
    +                current.set_user_type(journal.root_user_type_text)
    +                restored = workflow_module._reacquire_root(
    +                    view_arg,
    +                    start,
    +                    architecture,
    +                    platform,
    +                )
    +                if not bool(restored.has_user_type) or str(restored.type) != journal.root_user_type_text:
    +                    raise original_error
    +                journal.root_user_type_restored = True
    +                trace["diagnostic_fallback"] = "core-clear-then-string-set"
             except BaseException as error:

## Assistant

已确认 Python 层没有公开的 `clear_user_type()`；核心 API 的 `BNSetFunctionUserType(handle, NULL)` 是唯一可测试的清除路径。我已把它只接到诊断驱动里：仅当前两种恢复都失败后才执行，且仍要求立即精确读回原签名。现在用 `0x50d588` 的独立副本验证。

## Assistant

刚才的 `NULL` 清除实验导致隔离的 `bnpython3` 在核心调用处直接退出，说明它不是安全 API，不能进插件。更重要的线索是：当前恢复逻辑在 `set_user_type` 后、BN 完成分析提交前就做了读回审计，因此可能把异步生效误判为失败；我改为验证“设置后先完成一次 FullAuto，再审计”。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -77,3 +77,2 @@
         import binaryninja
    -    from binaryninja import _binaryninjacore as binaryninja_core
         from dualjump.adapter import BinaryNinjaDiscovery
    @@ -136,3 +135,3 @@
                     if (
    -                    os.environ.get("DUALBR_DIAGNOSTIC_CLEAR_USER_TYPE") != "1"
    +                    os.environ.get("DUALBR_DIAGNOSTIC_REANALYZE_USER_TYPE") != "1"
                         or getattr(original_error, "reason", None)
    @@ -147,5 +146,5 @@
                     )
    -                clear_trace = {
    +                retry_trace = {
                         "root": hex(int(current.start)),
    -                    "operation": "core-clear-user-type",
    +                    "operation": "string-set-then-full-auto",
                         "before": str(current.type),
    @@ -153,3 +152,4 @@
                     }
    -                binaryninja_core.BNSetFunctionUserType(current.handle, None)
    +                current.set_user_type(journal.root_user_type_text)
    +                workflow_module._full_auto_reanalyze(current)
                     current = workflow_module._reacquire_root(
    @@ -160,12 +160,6 @@
                     )
    -                clear_trace["after"] = str(current.type)
    -                clear_trace["after_present"] = bool(current.has_user_type)
    -                type_set_traces.append(clear_trace)
    -                current.set_user_type(journal.root_user_type_text)
    -                restored = workflow_module._reacquire_root(
    -                    view_arg,
    -                    start,
    -                    architecture,
    -                    platform,
    -                )
    +                retry_trace["after"] = str(current.type)
    +                retry_trace["after_present"] = bool(current.has_user_type)
    +                type_set_traces.append(retry_trace)
    +                restored = current
                     if not bool(restored.has_user_type) or str(restored.type) != journal.root_user_type_text:
    @@ -173,3 +167,3 @@
                     journal.root_user_type_restored = True
    -                trace["diagnostic_fallback"] = "core-clear-then-string-set"
    +                trace["diagnostic_fallback"] = "string-set-then-full-auto"
             except BaseException as error:

## Assistant

诊断成立：同一副本、同一后端在“恢复签名后先跑 FullAuto，再精确审计”时成功，`0x50d588` 从 `0x50d5f8` 扩展到 `0x50d7bc`，签名保持 `int64_t()`，Apply 返回 accepted。根因不是签名内容错误，而是插件把 BN 的延迟提交误当成恢复失败。现在先补对应回归测试，再改正式恢复顺序。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/tests/test_boundary_fixed_point.py
    @@ -362,2 +362,5 @@
             self.view.user_type_writes.append(value)
    +        if self.view.defer_user_type_until_analysis:
    +            self.view.pending_user_type = value
    +            return
             if self.view.ignore_non_string_user_type_writes and not isinstance(value, str):
    @@ -446,2 +449,4 @@
             self.ignore_non_string_user_type_writes = False
    +        self.defer_user_type_until_analysis = False
    +        self.pending_user_type = None
             self.degrade_user_type_after_workflow = False
    @@ -587,2 +592,6 @@
             self.analysis_updates += 1
    +        if self.pending_user_type is not None:
    +            self.user_type = self.pending_user_type
    +            self.user_type_present = True
    +            self.pending_user_type = None
     
    @@ -1002,2 +1011,32 @@
     
    +def test_root_user_type_restore_waits_for_analysis_before_auditing_deferred_metadata(tmp_path) -> None:
    +    """BN may publish a Function type only after its requested FullAuto pass.
    +
    +    Treating the immediate pre-analysis readback as authoritative makes a
    +    successful metadata write look like a failed restore after CFG expansion.
    +    """
    +
    +    view, root, _discovery, _guards = _fixture(tmp_path, stages=())
    +    view.user_type_present = True
    +    view.user_type = "int64_t()"
    +    journal = _FixedPointJournal(ROOT, view.workflow, "default")
    +    _capture_root_user_type(root, journal)
    +    view.user_type = "void*()"
    +    view.defer_user_type_until_analysis = True
    +
    +    restored = _restore_root_user_type(
    +        view,
    +        ROOT,
    +        root.arch,
    +        root.platform,
    +        journal,
    +        reanalyze=True,
    +    )
    +
    +    assert str(restored.type) == "int64_t()"
    +    assert view.analysis_updates == 1
    +    assert view.pending_user_type is None
    +    assert journal.root_user_type_restored is True
    +
    +
     def test_rollback_restores_the_captured_root_user_type_after_a_failed_transaction(tmp_path) -> None:

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -7225,30 +7225,33 @@
     
    -    # A Binary Ninja FunctionType handle captured before function-head
    -    # contraction can remain printable but no longer apply to the rebuilt
    -    # Function epoch.  Try the lossless immutable object first.  If exact
    -    # readback fails, use the documented StringOrType setter so Binary Ninja
    -    # reparses the same rendering against the current view/type namespace.
    -    try:
    -        set_current_type(root, journal.root_user_type)
    -        root = _reacquire_root(view, root_start, architecture, platform)
    -        object_applied = current_type_matches(root)
    -    except RecoveryError as error:
    -        if error.reason not in {"root-user-type-restore-failed", "root-user-type-restore-audit-failed"}:
    -            raise
    -        object_applied = False
    -    if not object_applied:
    -        root = _reacquire_root(view, root_start, architecture, platform)
    -        set_current_type(root, journal.root_user_type_text)
    +    def apply_and_publish(value) -> bool:
    +        """Set one exact type representation and observe its published epoch.
    +
    +        Binary Ninja may keep exposing the pre-write effective FunctionType
    +        until the requested FullAuto update completes.  Consequently the
    +        immediate readback is authoritative only for rollback, whose inverse
    +        analysis has already completed.  A successful forward transaction
    +        must publish the write before deciding that restoration failed.
    +        """
    +
    +        nonlocal root
    +        try:
    +            set_current_type(root, value)
    +            if reanalyze:
    +                _full_auto_reanalyze(root)
    +            root = _reacquire_root(view, root_start, architecture, platform)
    +            return current_type_matches(root)
    +        except RecoveryError as error:
    +            if error.reason not in {"root-user-type-restore-failed", "root-user-type-restore-audit-failed"}:
    +                raise
    +            return False
    +
    +    # A FunctionType handle captured before head contraction can remain
    +    # printable but no longer apply to the rebuilt Function epoch.  Preserve
    +    # it as the lossless first attempt, then reparse the exact rendering
    +    # through Binary Ninja's documented StringOrType setter if needed.  Each
    +    # forward attempt receives its own publication boundary before readback.
    +    if not apply_and_publish(journal.root_user_type):
             root = _reacquire_root(view, root_start, architecture, platform)
    -        if not current_type_matches(root):
    +        if not apply_and_publish(journal.root_user_type_text):
                 raise RecoveryError("root-user-type-restore-audit-failed")
    -    if reanalyze:
    -        _full_auto_reanalyze(root)
    -        root = _reacquire_root(view, root_start, architecture, platform)
    -        # FullAuto can itself replace the Function epoch.  Reparse once more
    -        # only when the exact user type did not survive that boundary; do not
    -        # trigger another FullAuto cycle after the final metadata restore.
    -        if not current_type_matches(root):
    -            set_current_type(root, journal.root_user_type_text)
    -            root = _reacquire_root(view, root_start, architecture, platform)
         if not current_type_matches(root):

## Assistant

正式代码已通过同一路径：不再需要诊断兜底，`0x50d588` Apply 成功且扩展后的函数签名精确保持不变。接下来把同一修复并行压到 Tags 扫描得到的另外三个“当前仍未修复、且可直接证明为双目标”的真实函数上，避免只修好这一例。

## Assistant

多点结果不是“一处修好就全过”：`0x50d588`、`0x51f030`、`0x525dc4` 已接受且保留原签名；`0x51e970` 仍以 `remaining-dualbr-sites-unresolved` 回滚。说明签名恢复故障已解决，但还暴露了第二个独立终态收敛问题。我现在针对 `0x51e970` 的失败收据和当前 IL 做差分定位。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -13,2 +13,3 @@
     import sys
    +from dataclasses import asdict, is_dataclass
     
    @@ -94,5 +95,23 @@
         phases: list[dict[str, object]] = []
    +    terminal_traces: list[dict[str, object]] = []
         original_restore = workflow_module._restore_root_user_type
    +    original_terminal_diagnostics = workflow_module._terminal_remaining_dualbr_diagnostics
         original_set_user_type = binaryninja.Function.set_user_type
     
    +    def jsonable(value):
    +        if is_dataclass(value):
    +            return {key: jsonable(item) for key, item in asdict(value).items()}
    +        if isinstance(value, dict):
    +            return {str(key): jsonable(item) for key, item in value.items()}
    +        if isinstance(value, (tuple, list, set)):
    +            return [jsonable(item) for item in value]
    +        if isinstance(value, (str, int, float, bool)) or value is None:
    +            return value
    +        return repr(value)
    +
    +    def traced_terminal_diagnostics(*args, **kwargs):
    +        result = original_terminal_diagnostics(*args, **kwargs)
    +        terminal_traces.append({"diagnostics": jsonable(result)})
    +        return result
    +
         def traced_set_user_type(function, user_type):
    @@ -178,2 +197,3 @@
         workflow_module._restore_root_user_type = traced_restore
    +    workflow_module._terminal_remaining_dualbr_diagnostics = traced_terminal_diagnostics
         binaryninja.Function.set_user_type = traced_set_user_type
    @@ -209,2 +229,3 @@
             workflow_module._restore_root_user_type = original_restore
    +        workflow_module._terminal_remaining_dualbr_diagnostics = original_terminal_diagnostics
             binaryninja.Function.set_user_type = original_set_user_type
    @@ -215,2 +236,3 @@
             payload["phases"] = phases
    +        payload["terminal_traces"] = terminal_traces
             view.file.close()

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -113,3 +113,39 @@
             result = original_terminal_diagnostics(*args, **kwargs)
    -        terminal_traces.append({"diagnostics": jsonable(result)})
    +        trace = {"diagnostics": jsonable(result)}
    +        if not terminal_traces and args:
    +            function = args[0]
    +
    +            def describe(item):
    +                try:
    +                    rendered = str(item)
    +                except Exception as error:
    +                    rendered = f"<{type(error).__name__}: {error}>"
    +                return {
    +                    "address": hex(int(item.address)) if isinstance(getattr(item, "address", None), int) else None,
    +                    "operation": getattr(getattr(item, "operation", None), "name", None),
    +                    "instr_index": getattr(item, "instr_index", None),
    +                    "expr_index": getattr(item, "expr_index", None),
    +                    "text": rendered[:500],
    +                }
    +
    +            try:
    +                hlil = function.hlil
    +                trace["hlil_flat_controls"] = [
    +                    describe(item)
    +                    for item in hlil.instructions
    +                    if getattr(getattr(item, "operation", None), "name", None)
    +                    in {"HLIL_IF", "HLIL_WHILE", "HLIL_DO_WHILE", "HLIL_FOR", "HLIL_SWITCH", "HLIL_GOTO"}
    +                ]
    +                trace["hlil_ast_controls"] = [
    +                    item
    +                    for item in hlil.traverse(
    +                        lambda node: describe(node)
    +                        if getattr(getattr(node, "operation", None), "name", None)
    +                        in {"HLIL_IF", "HLIL_WHILE", "HLIL_DO_WHILE", "HLIL_FOR", "HLIL_SWITCH", "HLIL_GOTO"}
    +                        else None
    +                    )
    +                ]
    +            except Exception as error:
    +                trace["hlil_capture_error"] = f"{type(error).__name__}: {error}"
    +        terminal_traces.append(trace)
             return result

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -147,2 +147,18 @@
                     ]
    +                trace["site_mappings"] = {}
    +                for diagnostic in result:
    +                    site = int(diagnostic.site)
    +                    exact_llil = [
    +                        item
    +                        for item in function.low_level_il.instructions
    +                        if getattr(item, "address", None) == site
    +                    ]
    +                    trace["site_mappings"][hex(site)] = [
    +                        {
    +                            "llil": describe(item),
    +                            "hlils": [describe(mapped) for mapped in getattr(item, "hlils", ())],
    +                            "mlils": [describe(mapped) for mapped in getattr(item, "mlils", ())],
    +                        }
    +                        for item in exact_llil
    +                    ]
                 except Exception as error:

## Assistant

第二个根因已经明确：`0x51e970` 实际已经恢复成确定的 LLIL/MLIL 条件分支，但终态审计错误地要求“原始 BR 地址必须恰好对应唯一一个 HLIL 条件节点”。

真实情况有两种合法提升：

- `0x51ecf0`：LLIL_IF、MLIL_IF 都精确存在，HLIL 优化把该分支吸收到结构化循环里，源映射为空。
- `0x51ef64`：一个 LLIL_IF 被 HLIL 合并成两个同源条件节点，因此按地址看似“歧义”，但都来自同一个已证明分支。

我会把审计改为基于 LLIL→MLIL 的源映射，允许 HLIL 的合法消除/拆分，同时仍拒绝映射到 `HLIL_SWITCH` 或非条件控制节点。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/tests/test_t55_activity_source_admission.py
    @@ -283,2 +283,24 @@
     
    +def _source_mapped_terminal_function(
    +    *,
    +    mapped_hlils: tuple[object, ...],
    +    mapped_mlils: tuple[object, ...] | None = None,
    +    flat_hlil: tuple[object, ...] | None = None,
    +) -> SimpleNamespace:
    +    if mapped_mlils is None:
    +        mapped_mlils = (
    +            SimpleNamespace(address=0x140, operation=SimpleNamespace(name="MLIL_IF")),
    +        )
    +    llil = SimpleNamespace(
    +        address=0x140,
    +        operation=SimpleNamespace(name="LLIL_IF"),
    +        mlils=mapped_mlils,
    +        hlils=mapped_hlils,
    +    )
    +    return SimpleNamespace(
    +        low_level_il=SimpleNamespace(instructions=(llil,)),
    +        hlil=SimpleNamespace(instructions=mapped_hlils if flat_hlil is None else flat_hlil),
    +    )
    +
    +
     def test_terminal_witness_accepts_an_address_correlated_hlil_if() -> None:
    @@ -311,2 +333,48 @@
     
    +def test_terminal_witness_accepts_multiple_conditionals_source_mapped_from_one_exact_llil_if() -> None:
    +    """HLIL may split/coalesce one native predicate into multiple conditions."""
    +
    +    mapped = (
    +        _terminal_hlil_item("HLIL_IF", condition=object()),
    +        _terminal_hlil_item("HLIL_DO_WHILE", condition=object()),
    +    )
    +
    +    _require_terminal_hlil_witness(
    +        _source_mapped_terminal_function(mapped_hlils=mapped),
    +        0x140,
    +    )
    +
    +
    +def test_terminal_witness_accepts_hlil_elimination_after_exact_llil_to_mlil_if_mapping() -> None:
    +    """A proven conditional can be absorbed into structured HLIL with no direct map."""
    +
    +    _require_terminal_hlil_witness(
    +        _source_mapped_terminal_function(
    +            mapped_hlils=(),
    +            flat_hlil=(SimpleNamespace(address=0x130, operation=SimpleNamespace(name="HLIL_DO_WHILE"), condition=object()),),
    +        ),
    +        0x140,
    +    )
    +
    +
    +def test_terminal_witness_rejects_a_source_mapped_hlil_switch() -> None:
    +    mapped = (
    +        SimpleNamespace(address=0x130, operation=SimpleNamespace(name="HLIL_SWITCH")),
    +    )
    +
    +    with pytest.raises(RecoveryError, match="terminal-hlil-switch-present"):
    +        _require_terminal_hlil_witness(
    +            _source_mapped_terminal_function(mapped_hlils=mapped),
    +            0x140,
    +        )
    +
    +
    +def test_terminal_witness_rejects_elimination_without_an_exact_mapped_mlil_if() -> None:
    +    with pytest.raises(RecoveryError, match="terminal-mlil-source-correlation-unavailable"):
    +        _require_terminal_hlil_witness(
    +            _source_mapped_terminal_function(mapped_hlils=(), mapped_mlils=()),
    +            0x140,
    +        )
    +
    +
     @pytest.mark.parametrize(

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/src/dualjump/workflow.py
    @@ -6899,9 +6899,11 @@
     def _require_terminal_hlil_witness(function: object, site: int) -> None:
    -    """Require one address-correlated structured HLIL condition, never a global count.
    +    """Require a current structured projection of one materialized LLIL IF.
     
    -    A whole-function lack of ``HLIL_SWITCH`` is not a substitute: we need an
    -    exact current HLIL instruction at the original BR address.  Binary Ninja
    -    can structure that native branch as an ``IF`` or one of its conditional
    -    loop nodes, all of which expose a ``condition`` operand.  This is an
    -    observer-only postcondition and has no discovery or mutation authority.
    +    Prefer Binary Ninja's own LLIL-to-MLIL/HLIL source maps over equal-address
    +    matching.  HLIL is an AST: it may legally split one predicate into several
    +    conditions or absorb a proven MLIL IF into a surrounding loop and retain
    +    no direct HLIL expression for the native address.  In both cases the exact
    +    LLIL IF plus its mapped MLIL IF is the stable source-correlated witness.
    +    Any source-mapped switch remains a hard refusal.  Minimal test/legacy
    +    facades without source maps retain the stricter equal-address behavior.
         """
    @@ -6915,2 +6917,48 @@
             raise RecoveryError("terminal-hlil-address-correlation-unavailable") from error
    +
    +    # Production Binary Ninja instructions expose both ``mlils`` and
    +    # ``hlils``.  Require a unique current LLIL instruction at the exact
    +    # native site before consulting those maps; an address-only HLIL node can
    +    # never authorize this path on its own.
    +    try:
    +        low_level_il = getattr(function, "low_level_il")
    +        low_instructions = tuple(getattr(low_level_il, "instructions"))
    +    except (AttributeError, TypeError):
    +        low_instructions = ()
    +    exact_low = [item for item in low_instructions if getattr(item, "address", None) == site]
    +    mapped_capable = len(exact_low) == 1 and hasattr(exact_low[0], "mlils") and hasattr(exact_low[0], "hlils")
    +    if mapped_capable:
    +        current_low = exact_low[0]
    +        if _lifted_operation_name(current_low) != "LLIL_IF":
    +            raise RecoveryError("terminal-llil-source-correlation-unavailable")
    +        try:
    +            mapped_mlils = tuple(getattr(current_low, "mlils"))
    +            mapped_hlils = tuple(getattr(current_low, "hlils"))
    +        except (AttributeError, TypeError, ValueError) as error:
    +            raise RecoveryError("terminal-mlil-source-correlation-unavailable") from error
    +        mapped_mlil_ifs = [item for item in mapped_mlils if _lifted_operation_name(item) == "MLIL_IF"]
    +        if not mapped_mlil_ifs:
    +            raise RecoveryError("terminal-mlil-source-correlation-unavailable")
    +        if any(_lifted_operation_name(item) == "HLIL_SWITCH" for item in mapped_hlils):
    +            raise RecoveryError("terminal-hlil-switch-present")
    +        mapped_conditionals = [
    +            item
    +            for item in mapped_hlils
    +            if _lifted_operation_name(item) in _TERMINAL_HLIL_CONDITIONAL_OPERATIONS
    +        ]
    +        if mapped_hlils and not mapped_conditionals:
    +            raise RecoveryError("terminal-hlil-address-correlation-ambiguous")
    +        if any(getattr(item, "condition", None) is None for item in mapped_conditionals):
    +            raise RecoveryError("terminal-hlil-condition-required")
    +        if mapped_conditionals:
    +            return
    +        # No direct HLIL mapping means the exact mapped MLIL IF was eliminated
    +        # or absorbed during structuring.  Reject an equal-address switch if
    +        # one nevertheless exists; otherwise the empty map is the relevant
    +        # source-correlated result, not a missing-analysis success path.
    +        exact_hlil = [item for item in instructions if getattr(item, "address", None) == site]
    +        if any(_lifted_operation_name(item) == "HLIL_SWITCH" for item in exact_hlil):
    +            raise RecoveryError("terminal-hlil-switch-present")
    +        return
    +
         matches = [item for item in instructions if getattr(item, "address", None) == site]

## Assistant

第二处修复已在真实副本上验证：`0x51e970` 现在 accepted，原来两个终态拒绝点都能按 LLIL→MLIL 源映射正确通过，同时保留了对 `HLIL_SWITCH` 的拒绝。下一步重新跑四个 Tags 选出的真实 DualBR 根，并补充终态 Tag/函数范围/签名审计，确认新规则没有放宽成误接受。

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -53,2 +53,14 @@
         workflow = getattr(getattr(function, "workflow", None), "name", None)
    +    unresolved_tags = []
    +    try:
    +        tag_type = view.tag_types.get("Unresolved Indirect Control Flow")
    +        if tag_type is not None:
    +            ranges = tuple(function.address_ranges)
    +            unresolved_tags = [
    +                hex(int(address))
    +                for address, _tag in view.tags_by_type(tag_type)
    +                if any(int(item.start) <= int(address) < int(item.end) for item in ranges)
    +            ]
    +    except Exception as error:
    +        unresolved_tags = [f"<{type(error).__name__}: {error}>"]
         return {
    @@ -61,2 +73,3 @@
             "indirect_sites": sites,
    +        "unresolved_indirect_tags": sorted(unresolved_tags),
         }

## Activity

    file changes: Completed · 1 changes
    Update { move_path: None }: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/draft/multi_case_validation/run_live_backend_case.py
    @@ -290,2 +290,40 @@
             payload["operation"] = operation.as_dict()
    +        if operation.accepted:
    +            current = view.get_function_at(root_start)
    +            tag_type = view.tag_types.get("Unresolved Indirect Control Flow")
    +            current_ranges = tuple(current.address_ranges)
    +            tagged_sites = tuple(sorted({
    +                int(address)
    +                for address, _tag in (() if tag_type is None else view.tags_by_type(tag_type))
    +                if any(int(item.start) <= int(address) < int(item.end) for item in current_ranges)
    +            }))
    +            session = discovery.discover_function(
    +                current,
    +                current.lifted_il,
    +                raw_terminator_overlay=True,
    +                raw_terminator_sites=tagged_sites,
    +            )
    +            payload["post_tag_classification"] = {
    +                "tagged_sites": [hex(site) for site in tagged_sites],
    +                "accepted": [
    +                    {
    +                        "site": hex(int(candidate.site)),
    +                        "targets": [hex(int(target)) for target in candidate.result.targets],
    +                        "dual": bool(candidate.result.is_dual_target),
    +                        "projection": candidate.projection,
    +                        "reason": candidate.result.reason,
    +                    }
    +                    for candidate in session.report.candidates
    +                    if candidate.site in tagged_sites
    +                ],
    +                "rejected": [
    +                    {
    +                        "site": hex(int(candidate.site)),
    +                        "projection": candidate.projection,
    +                        "reason": candidate.result.reason,
    +                    }
    +                    for candidate in session.report.rejected
    +                    if candidate.site in tagged_sites
    +                ],
    +            }
         except BaseException as error:

## Assistant

四个根的二次扫描结果一致：修复后没有任何仍被证明为“双目标”的 Tag。

- 原入口 Tag 均被清除。
- 剩余 Tag 要么是已证明的单目标 BR，要么与当前 IL 证明冲突而继续保持拒绝状态。
- 没有通过放宽审计把 switch/未知间接跳转误当 DualBR。

现在跑完整测试集，然后打包并覆盖安装插件。

## Assistant

完整回归为 `878 passed`。打包器已生成 19 个文件；额外的禁用模式扫描只在旧测试夹具的 `Path.write_bytes()` 上误报（它是在写临时 BNDB/sidecar 文件，不是机器码 patch），生产源码没有该行为。现在把现有安装目录先改名留作回滚，再安装新工件；当前已打开的 BN 进程仍需重启才能替换进程级 workflow。

## Activity

    file changes: Completed · 1 changes
    Add: /Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/docs/DUALBR_MULTICASE_REGRESSION_20260831.md
    # DualBR 多位置回归修复（2026-08-31）
    
    ## 范围与基线
    
    - 基线：`libmtguard_dualbr_smba_cfg27_predicate_live_validated_20260828.bndb.10.bak`
    - 基线 snapshot：15
    - 从 `Unresolved Indirect Control Flow` Tags 读取 65 条记录；33 个唯一当前 owner 根，31 条记录因多 owner 保持歧义。
    - 对每个唯一 owner 的 Tag 使用当前 DualBR prover 做只读 raw-terminator overlay。能够直接证明为双目标且尚未修复的根只有：`0x50d588`、`0x51e970`、`0x51f030`、`0x525dc4`。
    - 每个 Apply 都在独立 BNDB 副本、独立 `bnpython3` 进程、`BN_DISABLE_USER_PLUGINS=1` 条件下加载当前源码执行；没有修改 GUI 当前打开的数据库。
    
    只读分类记录：`draft/multi_case_validation/tagged_dualbr_candidates_snapshot15.json`。
    
    ## 修复一：user type 延迟提交误审计
    
    `0x50d588` 在 CFG 从 `0x50d588–0x50d5f8` 扩展为 `0x50d588–0x50d7bc` 后，BN 暂时显示推断签名 `void*()`。插件先后调用 `set_user_type(Type)` 与 `set_user_type(str)`，但在 FullAuto 发布新分析 epoch 前立即读取 `function.type`，因此把已排队的正确写入误判为 `root-user-type-restore-audit-failed`。
    
    修复后，每次恢复尝试遵循：
    
    1. 对当前 root 设置捕获的不可变 FunctionType；
    2. 前向 Apply 请求一次 FullAuto 并等待分析完成；
    3. 重新获取当前 Function wrapper，再做 `has_user_type` 与完整字符串的精确审计；
    4. 只有不可变对象在新 epoch 仍无效时，才以相同字符串重新解析并重复一次发布边界；
    5. rollback 不额外触发 FullAuto，仍使用已经完成的逆向分析边界并做立即精确读回。
    
    没有采用 `BNSetFunctionUserType(handle, NULL)`：一次性进程实验表明该未公开清除路径会使 `bnpython3` 直接退出，不具备生产安全性。
    
    ## 修复二：HLIL 合法提升被误判为未修复
    
    `0x51e970` 已生成正确 LLIL_IF/MLIL_IF，但旧终态审计要求原始 BR 地址恰好对应唯一一个 HLIL 条件节点：
    
    - `0x51ecf0`：精确 LLIL_IF 映射到精确 MLIL_IF；该条件在 HLIL 结构化时被吸收到循环，`llil.hlils` 为空。
    - `0x51ef64`：精确 LLIL_IF 映射到一个 MLIL_IF、两个同源 HLIL_IF；这是条件合并/拆分，不是证明歧义。
    
    终态审计现优先使用 BN 的 LLIL→MLIL/HLIL 源映射：
    
    - 必须在原生 site 得到唯一当前 LLIL_IF；
    - 必须至少映射到一个 MLIL_IF；
    - 多个同源 HLIL 条件节点允许通过，并分别要求 condition 存在；
    - 空 HLIL 映射仅在精确 LLIL_IF→MLIL_IF 已成立时视为合法 HLIL 消除/吸收；
    - 任意 source-mapped 或同地址 `HLIL_SWITCH` 继续硬拒绝；
    - 不具备源映射的测试/兼容 facade 仍使用原来的严格同地址规则。
    
    ## 真实多位置结果
    
    | root | Apply | 函数范围变化 | user type | 原入口 Tag | Apply 后仍可证明的双目标 Tag |
    |---|---|---|---|---|---|
    | `0x50d588` | accepted | `0x50d588–0x50d5f8` → `0x50d588–0x50d7bc` | `int64_t()` 保持 | 清除 | 0 |
    | `0x51e970` | accepted | `0x51e970–0x51ea40` → `0x51e970–0x51efa0` | 四参数 `int64_t(...)` 保持 | 清除 | 0 |
    | `0x51f030` | accepted | 单 range 扩展为 4 个 root-owned ranges | 四参数 `int64_t(...)` 保持 | 清除 | 0 |
    | `0x525dc4` | accepted | 单 range 扩展为 6 个 root-owned ranges | 四参数 `int64_t(...)` 保持 | 清除 | 0 |
    
    Apply 后的剩余 Tag 被同一 prover 再分类：`0x51e970` 与 `0x525dc4` 的一部分是已证明单目标 BR，其余为当前证明冲突；`0x51f030` 的两处均为当前证明冲突。它们都没有被误作为 DualBR 接受。
    
    最终机器记录位于 `draft/multi_case_validation/classified_{50d588,51e970,51f030,525dc4}/report.json`。
    
    ## 验证与交付
    
    - 新增 user type 延迟发布回归测试；
    - 新增 HLIL 多条件映射、HLIL 消除、source-mapped switch 拒绝和缺少 MLIL 映射拒绝测试；
    - 全量测试：`878 passed`；
    - 文件夹插件工件：`artifact/plugin/dualbr_deobfuscator/`，manifest 19 个 payload 全部复核通过；
    - 已安装到 `~/Library/Application Support/Binary Ninja/plugins/dualbr_deobfuscator/`；旧安装保存在同级 `dualbr_deobfuscator.bak-20260831-multicase/`。
    
    Binary Ninja workflow 注册是进程级状态。已经加载旧版 DualBR workflow 的 BN 进程必须重启后才能使用本次安装。

## Assistant

已修复并安装新 DualBR 插件。

- 修复 user type 在 FullAuto 前过早审计的问题。
- 支持 HLIL 合法合并、拆分和消除，同时继续拒绝 Switch。
- 真实验证 `0x50d588`、`0x51e970`、`0x51f030`、`0x525dc4`，均 accepted、签名保持，且无 DualBR Tag 残留。
- 全量测试：`878 passed`。
- 分析报告：[DUALBR_MULTICASE_REGRESSION_20260831.md](/Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/docs/DUALBR_MULTICASE_REGRESSION_20260831.md)
- 插件工件：[dualbr_deobfuscator](/Users/bytedance/work/reverse_for_fun_mt/analysis/Dual_jump_deobf/artifact/plugin/dualbr_deobfuscator)

需要重启 Binary Ninja，当前进程仍持有旧 workflow。

本轮用时约 28 分 52 秒，使用 322,010 tokens。
