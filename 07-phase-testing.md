# Testing Phase Playbook

## 1. TEST STRATEGY

Write tests at three levels, ordered by priority:

1. **Unit tests** — test individual functions/methods in isolation. Fast, deterministic, no external dependencies.
2. **Integration tests** — test interactions between modules or with external services (using mocks/stubs where appropriate).
3. **End-to-end tests** — test complete user workflows through the full stack. Fewer in number, higher value.

## 2. COVERAGE TARGETS

- **Minimum threshold**: 80% line coverage for new code.
- **Critical paths** (auth, payment, data integrity): 100% branch coverage.
- Document coverage results in the test report. If below threshold, explain why and list uncovered paths.

## 3. TEST GENERATION GUIDELINES

- **One assertion per test** (or logically grouped assertions for a single concept).
- **Test names describe the scenario**, not the implementation: `test_user_cannot_access_another_users_resource` not `test_get_returns_403`.
- **Arrange-Act-Assert** structure for every test.
- **Test edge cases** identified in requirements: boundary values, empty states, error paths, concurrent access.
- **Do not test implementation details.** Test observable behavior.
- **Use fixtures or setup functions** for shared test data. Do not duplicate setup across tests.

## 4. REGRESSION PROTOCOL

- When fixing a bug, write a test that reproduces the bug before applying the fix.
- Verify the test fails without the fix and passes with it.
- Name the test after the bug: `test_issue_042_duplicate_order_prevention`.
- Add the test to the existing test suite; do not create a separate regression suite.

## 5. TEST EXECUTION

- Run the full test suite before requesting approval.
- All tests must pass (exit code 0).
- Record execution time and flaky test warnings in the test report.
- If tests are flaky, fix them. Do not mark tests as "skip" or "xfail" without documented justification.

## 6. OUTPUT

**Deliverables:**
- Test files (adjacent to source or in `tests/` per project convention)
- `docs/testing/<number>-<feature>-test-report.md` (relative to target project root)

**Test report required sections:**
1. Test summary (total tests, passed, failed, skipped)
2. Coverage results (line %, branch %, per-file breakdown)
3. Flaky tests (if any, with justification)
4. Regression tests added
5. Known limitations or untested paths

## 7. PHASE EXIT

After producing test files and test report:

1. Verify all tests pass.
2. Verify coverage meets threshold.
3. Run `check_gate(project_path=<project>, from_phase="testing", to_phase="deployment")` to verify deliverables.
4. Report completion to the human.
5. **STOP.** Await human approval before proceeding to deployment phase.
