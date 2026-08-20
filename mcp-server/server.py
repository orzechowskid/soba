"""AI-SDLC Framework MCP Server"""
import logging
import asyncio
import json
import traceback
import sys
import signal
import re
import subprocess
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, PromptMessage, Tool, Prompt, PromptArgument

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai-sdlc-mcp")
logger.setLevel(logging.DEBUG)

# Add file handler for debug logging (overwrites on each startup)
_file_handler = logging.FileHandler("/home/dan/repos/sdlc/mcp-server/debug.log", mode="w")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_file_handler)

# Ensure logging never silently drops
logging.raiseExceptions = False

def _global_excepthook(exc_type, exc_value, exc_tb):
    logger.critical(
        "UNCAUGHT EXCEPTION (sys.excepthook): %s: %s\n%s",
        exc_type.__name__,
        exc_value,
        "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
    )
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = _global_excepthook

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def _async_exception_handler(loop, context):
    exc = context.get("exception")
    if isinstance(exc, BaseException):
        logger.critical(
            "UNCAUGHT ASYNC EXCEPTION: %s: %s\n%s",
            type(exc).__name__,
            exc,
            "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )
    else:
        logger.critical("ASYNC LOOP CONTEXT: %s", context)
    loop.default_exception_handler(context)

# Server instance
app = Server("ai-sdlc-framework")

# Prompt handlers
PHASE_MAP = {
    "enhancement": "09-phase-enhancement.md",
    "requirements": "02-phase-requirements.md",
    "design": "03-phase-design.md",
    "implementation": "04-phase-implementation.md",
    "review": "05-phase-review.md",
    "testing": "06-phase-testing.md",
    "deployment": "07-phase-deployment.md",
    "monitoring": "08-phase-monitoring.md",
}

VALID_PHASES = ("enhancement", "requirements", "design", "implementation", "review", "testing", "deployment", "monitoring")


def _detect_test_command(project_path):
    """Detect the project's test command.

    Returns (argv, label) or None if no test command can be detected.
    """
    pkg = project_path / "package.json"
    if pkg.is_file():
        try:
            scripts = json.loads(pkg.read_text(encoding="utf-8")).get("scripts", {})
        except (json.JSONDecodeError, OSError):
            scripts = {}
        if isinstance(scripts, dict) and scripts.get("test"):
            return ["npm", "test"], "npm test"
    pyproject = project_path / "pyproject.toml"
    if pyproject.is_file():
        try:
            text = pyproject.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            text = ""
        if "[tool.pytest" in text:
            return [sys.executable, "-m", "pytest"], "python -m pytest"
    if (project_path / "pytest.ini").is_file():
        return [sys.executable, "-m", "pytest"], "python -m pytest"
    if (project_path / "go.mod").is_file():
        return ["go", "test", "./..."], "go test ./..."
    if (project_path / "Cargo.toml").is_file():
        return ["cargo", "test"], "cargo test"
    makefile = project_path / "Makefile"
    if makefile.is_file():
        try:
            make_text = makefile.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            make_text = ""
        if re.search(r"^test\s*:", make_text, re.MULTILINE):
            return ["make", "test"], "make test"
    node_test_exts = ("js", "ts", "mjs", "mts", "cjs", "jsx", "tsx")
    node_tests = [
        p for ext in node_test_exts for p in project_path.glob(f"**/*.test.{ext}")
    ]
    if node_tests:
        return ["node", "--test"], "node --test"
    py_tests = list(project_path.glob("**/test_*.py")) + list(
        project_path.glob("**/*_test.py")
    )
    if py_tests:
        return [sys.executable, "-m", "pytest"], "python -m pytest"
    return None


def _run_test_suite(project_path, timeout=600):
    """Run the project's detected test suite.

    Returns (passed: bool | None, detail: str). passed is None when no test
    command could be detected.
    """
    detected = _detect_test_command(project_path)
    if detected is None:
        return None, (
            "no test command detected (no package.json test script, pytest "
            "config, go.mod, Cargo.toml, Makefile test target, or *.test.* "
            "files)"
        )
    argv, label = detected
    try:
        proc = subprocess.run(
            argv,
            cwd=str(project_path),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return False, f"{label} timed out after {timeout}s"
    except FileNotFoundError:
        return False, f"{label}: executable not found"
    output = (proc.stdout or "") + (proc.stderr or "")
    tail = output[-800:]
    if proc.returncode == 0:
        return True, f"{label} exited 0"
    return False, f"{label} exited {proc.returncode}: {tail}"


@app.list_prompts()
async def list_prompts():
    logger.debug("list_prompts: entry")
    try:
        result = [
            Prompt(name="sdlc_bootstrap", description="Load Tier 1 documents (bootstrap + lifecycle overview) as session context", arguments=[]),
            Prompt(name="sdlc_phase", description="Load the relevant Tier 2 playbook for a given phase", arguments=[PromptArgument(name="phase_name", description="Phase name (e.g., implementation)", required=True)]),
            Prompt(name="sdlc_resume", description="Restore context after loss/compaction: loads Tier 1 + current phase playbook + pipeline state", arguments=[PromptArgument(name="project_path", description="Absolute path to project root", required=True)]),
        ]
        logger.debug(f"list_prompts: returning {len(result)} prompts")
        return result
    except Exception:
        logger.exception("list_prompts: exception")
        raise

@app.get_prompt()
async def get_prompt(name, arguments=None):
    logger.debug(f"get_prompt: entry, name={name}, argument_keys={list((arguments or {}).keys())}")
    try:
        arguments = arguments or {}

        if name == "sdlc_bootstrap":
            messages = []
            for doc in ["00-bootstrap.md", "01-lifecycle-overview.md"]:
                path = DOCS_DIR / doc
                if path.is_file():
                    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8"))))
            logger.debug(f"get_prompt: sdlc_bootstrap returning {len(messages)} messages")
            return {"messages": messages}

        elif name == "sdlc_phase":
            phase = arguments.get("phase_name", "")
            doc = PHASE_MAP.get(phase)
            if not doc:
                result = {"messages": [PromptMessage(role="user", content=TextContent(type="text", text=f"Unknown phase: {phase}. Valid: {', '.join(PHASE_MAP.keys())}"))]}
                logger.debug(f"get_prompt: sdlc_phase unknown phase, {len(result['messages'])} messages")
                return result
            path = DOCS_DIR / doc
            if not path.is_file():
                result = {"messages": [PromptMessage(role="user", content=TextContent(type="text", text=f"Document not found: {doc}"))]}
                logger.debug(f"get_prompt: sdlc_phase doc missing, {len(result['messages'])} messages")
                return result
            result = {"messages": [PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8")))]}
            logger.debug(f"get_prompt: sdlc_phase returning {len(result['messages'])} messages")
            return result

        elif name == "sdlc_resume":
            messages = []
            # Load Tier 1
            for doc in ["00-bootstrap.md", "01-lifecycle-overview.md"]:
                path = DOCS_DIR / doc
                if path.is_file():
                    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8"))))
            # Load pipeline state
            project_path = Path(arguments.get("project_path", ""))
            state_file = project_path / "sdlc-state.json"
            state_text = "No state file found."
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    state_text = json.dumps(state, indent=2)
                    current_phase = state.get("current_phase", "requirements")
                except json.JSONDecodeError:
                    current_phase = "requirements"
            else:
                # Infer phase: a phase directory's existence means that phase is
                # complete (01-lifecycle-overview.md §6), so current is the next phase.
                current_phase = "requirements"
                dir_for_phase = {
                    "enhancement": "enhancement",
                    "requirements": "requirements",
                    "design": "design",
                    "implementation": "implementation",
                    "review": "review",
                    "testing": "testing",
                    "deployment": "deploy",
                    "monitoring": "monitoring",
                }
                for i, phase in enumerate(VALID_PHASES):
                    if (project_path / "docs" / dir_for_phase[phase]).is_dir():
                        if i + 1 < len(VALID_PHASES):
                            current_phase = VALID_PHASES[i + 1]

            messages.append(PromptMessage(role="user", content=TextContent(type="text", text=f"Current Pipeline State:\n{state_text}\n\nLoading playbook for phase: {current_phase}")))
            # Load phase playbook
            doc = PHASE_MAP.get(current_phase)
            if doc:
                path = DOCS_DIR / doc
                if path.is_file():
                    messages.append(PromptMessage(role="user", content=TextContent(type="text", text=path.read_text(encoding="utf-8"))))
            logger.debug(f"get_prompt: sdlc_resume returning {len(messages)} messages")
            return {"messages": messages}

        logger.debug("get_prompt: unknown prompt name, returning empty")
        return {"messages": []}
    except Exception:
        logger.exception(f"get_prompt: exception for name={name}")
        raise

# Document source directory (parent of mcp-server/)
DOCS_DIR = Path(__file__).parent.parent

@app.list_tools()
async def list_tools():
    logger.debug("list_tools: entry")
    try:
        result = [
            Tool(name="list_documents", description="List available AI-SDLC documents with tier and purpose", inputSchema={"type": "object", "properties": {}, "required": []}),
            Tool(name="get_document", description="Retrieve a specific AI-SDLC document by filename", inputSchema={"type": "object", "properties": {"doc_name": {"type": "string", "description": "Document filename (e.g., '00-bootstrap.md')"}}, "required": ["doc_name"]}),
            Tool(name="get_pipeline_state", description="Read project pipeline state from sdlc-state.json. Requires project_path parameter.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to the project root"}}, "required": ["project_path"]}),
            Tool(name="set_pipeline_state", description="Update the project pipeline state in sdlc-state.json. Provide project_path and any fields to update (current_phase, feature, last_gate). Unprovided fields are preserved from existing state.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to project root"}, "current_phase": {"type": "string", "enum": list(VALID_PHASES), "description": "Phase name"}, "feature": {"type": "string", "description": "Feature name"}, "last_gate": {"type": "string", "description": "Gate that was just passed"}, "override_reason": {"type": "string", "description": "Reason for skipping phases. Required when jumping more than one phase forward."}}, "required": ["project_path"]}),
            Tool(name="begin_sdlc", description="Initialize a new SDLC pipeline for a project. Creates sdlc-state.json starting at the requirements phase. Fails if a state file already exists.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to project root"}, "feature": {"type": "string", "description": "Feature name"}}, "required": ["project_path", "feature"]}),
            Tool(name="check_gate", description="Verify deliverables exist and are properly formatted before requesting human approval for a phase transition. Returns verifiable gate results and lists human judgment gates.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to project root"}, "from_phase": {"type": "string", "description": "Phase being exited (e.g., requirements)"}, "to_phase": {"type": "string", "description": "Phase being entered (e.g., design)"}}, "required": ["project_path", "from_phase", "to_phase"]}),
            Tool(name="record_approval", description="Record a human approval decision for a phase transition. Logs decision type, caveats, and risk acceptances to docs/decisions/<feature>-approval.md.", inputSchema={"type": "object", "properties": {"project_path": {"type": "string", "description": "Absolute path to project root"}, "phase": {"type": "string", "description": "The phase being approved (e.g., requirements)"}, "decision": {"type": "string", "description": "approve | approve_with_caveats | send_back_to_[phase]"}, "caveats": {"type": "string", "description": "Text describing any conditions or caveats"}, "risk_acceptances": {"type": "array", "items": {"type": "object", "properties": {"risk": {"type": "string"}, "severity": {"type": "string"}, "agent_recommendation": {"type": "string"}, "human_decision": {"type": "string"}, "justification": {"type": "string"}}}, "description": "Array of risk acceptance records"}}, "required": ["project_path", "phase", "decision"]}),
        ]
        logger.debug(f"list_tools: returning {len(result)} tools")
        return result
    except Exception:
        logger.exception("list_tools: exception")
        raise

@app.call_tool()
async def call_tool(name, args):
    logger.debug(f"call_tool: entry, name={name}, arg_keys={list((args or {}).keys())}")
    try:
        if name == "list_documents":
            docs = []
            for f in sorted(DOCS_DIR.glob("*.md")):
                if f.name == "README.md":
                    continue
                docs.append(f"- {f.name}")
            result = [TextContent(type="text", text="\n".join(docs))]
            logger.debug(f"call_tool: list_documents returning {len(result)} items, text length={len(result[0].text) if result else 0}")
            return result
        elif name == "get_document":
            doc_name = args.get("doc_name", "")
            # Prevent path traversal
            if not doc_name or ".." in doc_name or "/" in doc_name or "\\" in doc_name:
                result = [TextContent(type="text", text="Error: Invalid document name.")]
                logger.debug(f"call_tool: get_document invalid name, {len(result)} items")
                return result
            doc_path = DOCS_DIR / doc_name
            if not doc_path.is_file():
                result = [TextContent(type="text", text=f"Error: Document not found: {doc_name}")]
                logger.debug(f"call_tool: get_document not found, {len(result)} items")
                return result
            text = doc_path.read_text(encoding="utf-8")
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: get_document returning {len(result)} items, text length={len(result[0].text)}")
            return result
        elif name == "get_pipeline_state":
            project_path = Path(args.get("project_path", ""))
            state_file = project_path / "sdlc-state.json"
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    text = json.dumps(state, indent=2)
                    result = [TextContent(type="text", text=text)]
                    logger.debug(f"call_tool: get_pipeline_state returning {len(result)} items, text length={len(result[0].text)}")
                    return result
                except json.JSONDecodeError:
                    result = [TextContent(type="text", text="Error: Invalid sdlc-state.json format.")]
                    logger.debug(f"call_tool: get_pipeline_state invalid json, {len(result)} items")
                    return result
            # Infer state from docs/ directories.
            # Per 01-lifecycle-overview.md §6, a phase directory's existence means
            # that phase is COMPLETE, so the current phase is the next one.
            inferred = {"current_phase": "requirements", "feature": "unknown", "last_gate": "none"}
            dir_for_phase = {
                "enhancement": "enhancement",
                "requirements": "requirements",
                "design": "design",
                "implementation": "implementation",
                "review": "review",
                "testing": "testing",
                "deployment": "deploy",
                "monitoring": "monitoring",
            }
            for i, phase in enumerate(VALID_PHASES):
                if (project_path / "docs" / dir_for_phase[phase]).is_dir():
                    if i + 1 < len(VALID_PHASES):
                        inferred["current_phase"] = VALID_PHASES[i + 1]
                    inferred["last_gate"] = phase
            text = json.dumps(inferred, indent=2)
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: get_pipeline_state inferred returning {len(result)} items, text length={len(result[0].text)}")
            return result
        elif name == "set_pipeline_state":
            project_path = Path(args.get("project_path", ""))
            if not project_path.is_absolute():
                result = [TextContent(type="text", text="Error: project_path must be an absolute path.")]
                logger.debug(f"call_tool: set_pipeline_state invalid path, {len(result)} items")
                return result
            state_file = project_path / "sdlc-state.json"
            # Load existing state or defaults
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    state = {}
            else:
                state = {"current_phase": "requirements", "feature": "unknown", "last_gate": "none"}
            # Phase transition validation
            if "current_phase" in args:
                new_phase = args["current_phase"]
                phase_order = list(VALID_PHASES)
                existing_phase = state.get("current_phase", "requirements")

                if existing_phase in phase_order and new_phase in phase_order:
                    old_idx = phase_order.index(existing_phase)
                    new_idx = phase_order.index(new_phase)

                    # Forward skip: new is more than 1 phase ahead
                    if new_idx > old_idx + 1:
                        skipped = phase_order[old_idx + 1:new_idx]
                        warning = f"Warning: Skipping phases {', '.join(skipped)}. Ensure deliverables for those phases are complete."
                        logger.warning(f"call_tool: set_pipeline_state {warning}")

                        # Require override_reason when skipping
                        override_reason = args.get("override_reason")
                        if not override_reason:
                            result = [TextContent(type="text", text=f"{warning}\n\nTo skip phases, provide an 'override_reason' parameter explaining why.")]
                            return result

                        # Store override reason in state
                        state["override_reason"] = override_reason
                        state["skipped_phases"] = skipped
            # Merge provided fields
            for field in ("current_phase", "feature", "last_gate"):
                if field in args:
                    value = args[field]
                    if field == "current_phase" and value not in VALID_PHASES:
                        result = [TextContent(type="text", text=f"Error: Invalid phase '{value}'. Valid: {', '.join(VALID_PHASES)}")]
                        logger.debug(f"call_tool: set_pipeline_state invalid phase, {len(result)} items")
                        return result
                    state[field] = value
            state["timestamp"] = __import__("datetime").datetime.now().isoformat()
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            text = json.dumps(state, indent=2)
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: set_pipeline_state wrote state, text length={len(result[0].text)}")
            return result

        elif name == "begin_sdlc":
            project_path = Path(args.get("project_path", ""))
            if not project_path.is_absolute():
                result = [TextContent(type="text", text="Error: project_path must be an absolute path.")]
                logger.debug(f"call_tool: begin_sdlc invalid path, {len(result)} items")
                return result
            feature = args.get("feature", "")
            if not feature:
                result = [TextContent(type="text", text="Error: feature parameter is required.")]
                logger.debug(f"call_tool: begin_sdlc missing feature, {len(result)} items")
                return result
            state_file = project_path / "sdlc-state.json"
            if state_file.is_file():
                existing = json.loads(state_file.read_text(encoding="utf-8"))
                result = [TextContent(type="text", text=f"Error: State file already exists for this project.\nCurrent state:\n{json.dumps(existing, indent=2)}\n\nTo update, use set_pipeline_state instead.")]
                logger.debug(f"call_tool: begin_sdlc state exists, {len(result)} items")
                return result
            import datetime
            # Auto-detect: brownfield (enhancement) if prior artifacts exist
            docs_dirs = [
                project_path / "docs" / "requirements",
                project_path / "docs" / "design",
                project_path / "docs" / "implementation",
                project_path / "docs" / "review",
                project_path / "docs" / "testing",
                project_path / "docs" / "deploy",
                project_path / "docs" / "monitoring",
                project_path / "docs" / "enhancement",
            ]
            has_prior_artifacts = any(d.is_dir() for d in docs_dirs)
            if has_prior_artifacts:
                initial_phase = "enhancement"
            else:
                initial_phase = "requirements"
            state = {"schema_version": 2, "current_phase": initial_phase, "feature": feature, "last_gate": "none", "timestamp": datetime.datetime.now().isoformat()}
            # Note brownfield detection in state
            state["project_mode"] = "enhancement" if has_prior_artifacts else "greenfield"
            state_file.parent.mkdir(parents=True, exist_ok=True)
            state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")
            # Create docs directory
            (project_path / "docs").mkdir(parents=True, exist_ok=True)
            text = json.dumps(state, indent=2)
            result = [TextContent(type="text", text=text)]
            logger.debug(f"call_tool: begin_sdlc created state, text length={len(result[0].text)}")
            return result
        elif name == "check_gate":
            project_path = Path(args.get("project_path", ""))
            from_phase = args.get("from_phase", "")
            to_phase = args.get("to_phase", "")

            verifiable = []
            human_gates = []

            gate_key = f"{from_phase}->{to_phase}"

            # Load feature name from state for filename validation
            state_file = project_path / "sdlc-state.json"
            feature = ""
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    feature = state.get("feature", "")
                except (json.JSONDecodeError, OSError):
                    pass

            if gate_key == "enhancement->requirements":
                enh_dir = project_path / "docs" / "enhancement"
                if enh_dir.is_dir():
                    enh_files = sorted(enh_dir.glob("*.md"))
                    if enh_files:
                        enh_file = enh_files[-1]
                        verifiable.append({"gate": "docs/enhancement/ directory exists with deliverable", "status": "pass", "detail": f"{enh_file.name}"})
                        content = enh_file.read_text(encoding="utf-8")

                        # Check required sections
                        required_sections = ["Current System Overview", "Prior Features", "Relevant Design References", "Change Context"]
                        for section in required_sections:
                            if section in content:
                                verifiable.append({"gate": f"Section present: {section}", "status": "pass"})
                            else:
                                verifiable.append({"gate": f"Section present: {section}", "status": "fail", "detail": f"No '{section}' section found"})
                    else:
                        verifiable.append({"gate": "docs/enhancement/ directory exists with deliverable", "status": "fail", "detail": "Directory exists but no .md files found"})
                else:
                    verifiable.append({"gate": "docs/enhancement/ directory exists with deliverable", "status": "fail", "detail": "docs/enhancement/ directory not found"})

                human_gates.append({"gate": "System understanding is adequate", "requires": "human judgment", "detail": "Verify the agent has adequate understanding of the existing system"})
                human_gates.append({"gate": "Prior architectural decisions considered", "requires": "human judgment", "detail": "Verify prior design decisions have been properly accounted for"})
                human_gates.append({"gate": "Change context accurately describes fit", "requires": "human judgment", "detail": "Verify the change context accurately describes where the new feature fits"})

            if gate_key == "requirements->design":
                req_dir = project_path / "docs" / "requirements"
                if req_dir.is_dir():
                    req_files = sorted(req_dir.glob("*.md"))
                    if req_files:
                        # Use the most recent (highest numbered) file
                        req_file = req_files[-1]
                        verifiable.append({"gate": "docs/requirements/ directory exists with deliverable", "status": "pass", "detail": f"{req_file.name}"})
                        content = req_file.read_text(encoding="utf-8")

                        # Check functional requirements
                        if "FR-" in content:
                            verifiable.append({"gate": "Functional requirements present (FR-*)", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Functional requirements present (FR-*)", "status": "fail", "detail": "No FR- entries found"})

                        # Check acceptance criteria
                        if "AC-" in content:
                            verifiable.append({"gate": "Acceptance criteria present (AC-*)", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Acceptance criteria present (AC-*)", "status": "fail", "detail": "No AC- entries found"})

                        # Check constraints
                        if "Constraint" in content:
                            verifiable.append({"gate": "Constraints section present", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Constraints section present", "status": "fail", "detail": "No Constraints section found"})

                        # Check assumptions
                        if "Assumption" in content:
                            verifiable.append({"gate": "Assumptions section present", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Assumptions section present", "status": "fail", "detail": "No Assumptions section found"})

                        # Check open questions
                        if "Open Question" in content:
                            verifiable.append({"gate": "Open questions section present", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Open questions section present", "status": "fail", "detail": "No Open Questions section found"})

                        # Check out-of-scope
                        if "Out-of-Scope" in content or "Out of Scope" in content:
                            verifiable.append({"gate": "Out-of-scope section present", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Out-of-scope section present", "status": "fail", "detail": "No Out-of-Scope section found"})

                        # Self-review check
                        if "Self-Review" in content or "Self Review" in content:
                            verifiable.append({"gate": "Self-review completed", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Self-review completed", "status": "fail", "detail": "No Self-Review section found"})
                    else:
                        verifiable.append({"gate": "docs/requirements/ directory exists with deliverable", "status": "fail", "detail": "Directory exists but no .md files found"})
                else:
                    verifiable.append({"gate": "docs/requirements/ directory exists with deliverable", "status": "fail", "detail": "docs/requirements/ directory not found"})

                human_gates.append({"gate": "Requirements completeness and correctness", "requires": "human judgment", "detail": "Verify requirements are complete and correct"})
                human_gates.append({"gate": "Business priority and stakeholder alignment", "requires": "human judgment", "detail": "Verify business priority and stakeholder buy-in"})
                human_gates.append({"gate": "No critical ambiguities remain unresolved", "requires": "human judgment", "detail": "Verify no critical ambiguities remain"})

            elif gate_key == "design->implementation":
                design_dir = project_path / "docs" / "design"
                if design_dir.is_dir():
                    design_files = sorted(design_dir.glob("*.md"))
                    if len(design_files) > 0:
                        verifiable.append({"gate": "docs/design/ exists with technical-design documents", "status": "pass", "detail": f"{len(design_files)} document(s) found"})
                        for design_file in design_files:
                            content = design_file.read_text(encoding="utf-8")
                            # Check required technical-design document sections
                            required_sections = ["TR-", "AC-", "Constraint", "Assumption", "Reference"]
                            missing = [s for s in required_sections if s not in content]
                            if not missing:
                                verifiable.append({"gate": f"Technical-design document format complete: {design_file.name}", "status": "pass"})
                            else:
                                verifiable.append({"gate": f"Technical-design document format complete: {design_file.name}", "status": "fail", "detail": f"Missing: {', '.join(missing)}"})

                            # Check technology stack
                            tech_terms = ["tech stack", "technology stack", "tech-stack", "technology", "framework", "language"]
                            if any(term in content.lower() for term in tech_terms):
                                verifiable.append({"gate": f"Technology stack identified: {design_file.name}", "status": "pass"})
                            else:
                                verifiable.append({"gate": f"Technology stack identified: {design_file.name}", "status": "fail", "detail": "No technology stack mentioned"})

                            # Check dependencies
                            dep_terms = ["dependency", "dependencies", "third-party", "third party", "library"]
                            if any(term in content.lower() for term in dep_terms):
                                verifiable.append({"gate": f"Dependencies identified: {design_file.name}", "status": "pass"})
                            else:
                                verifiable.append({"gate": f"Dependencies identified: {design_file.name}", "status": "fail", "detail": "No dependencies mentioned"})

                            # Self-review check
                            if "Self-Review" in content or "Self Review" in content:
                                verifiable.append({"gate": f"Self-review completed: {design_file.name}", "status": "pass"})
                            else:
                                verifiable.append({"gate": f"Self-review completed: {design_file.name}", "status": "fail", "detail": "No Self-Review section found"})
                    else:
                        verifiable.append({"gate": "docs/design/ exists with technical-design documents", "status": "fail", "detail": "Directory exists but no .md files found"})
                else:
                    verifiable.append({"gate": "docs/design/ exists with technical-design documents", "status": "fail", "detail": "docs/design/ directory not found"})

                human_gates.append({"gate": "Architecture soundness", "requires": "human judgment", "detail": "Verify architecture is appropriate for the problem"})
                human_gates.append({"gate": "Tradeoff analysis", "requires": "human judgment", "detail": "Verify tradeoffs are acceptable"})
                human_gates.append({"gate": "Scope is appropriately bounded", "requires": "human judgment", "detail": "Verify scope is bounded for this implementation phase"})

            elif gate_key == "implementation->review":
                # Check implementation summary
                impl_dir = project_path / "docs" / "implementation"
                if impl_dir.is_dir() and any(impl_dir.glob("*.md")):
                    impl_files = sorted(impl_dir.glob("*.md"))
                    impl_summary_text = impl_files[-1].read_text(encoding="utf-8", errors="ignore")
                    verifiable.append({"gate": "Implementation summary exists", "status": "pass"})
                else:
                    impl_summary_text = ""
                    verifiable.append({"gate": "Implementation summary exists", "status": "fail", "detail": "docs/implementation/ missing or empty"})

                # Check for source files
                src_indicators = ["src", "lib", "app", "pkg"]
                has_src = any((project_path / d).is_dir() for d in src_indicators)
                if has_src:
                    verifiable.append({"gate": "Source code directory exists", "status": "pass"})

                    # Find source files for inline documentation check
                    source_files = []
                    for indicator in src_indicators:
                        src_path = project_path / indicator
                        if src_path.is_dir():
                            source_files.extend(src_path.glob("**/*.py"))
                            source_files.extend(src_path.glob("**/*.js"))
                            source_files.extend(src_path.glob("**/*.ts"))
                            source_files.extend(src_path.glob("**/*.go"))
                            source_files.extend(src_path.glob("**/*.java"))
                            source_files.extend(src_path.glob("**/*.rs"))

                    # Check inline documentation
                    if source_files:
                        doc_patterns = ['"""', "'''", "/**", "///", "# @param", "# @return", "/// <summary>", "//!"]
                        files_with_docs = 0
                        for sf in source_files:
                            try:
                                sf_content = sf.read_text(encoding="utf-8")
                                if any(pattern in sf_content for pattern in doc_patterns):
                                    files_with_docs += 1
                            except (OSError, UnicodeDecodeError):
                                pass
                        doc_ratio = files_with_docs / len(source_files) if source_files else 0
                        if doc_ratio > 0:
                            verifiable.append({"gate": "Inline documentation present in source files", "status": "pass", "detail": f"{files_with_docs}/{len(source_files)} files have documentation"})
                        else:
                            verifiable.append({"gate": "Inline documentation present in source files", "status": "fail", "detail": "No inline documentation found in source files"})
                    else:
                        verifiable.append({"gate": "Inline documentation present in source files", "status": "fail", "detail": "No source files found to check"})

                    # Check AC mapping coverage against the technical-design document
                    design_dir = project_path / "docs" / "design"
                    design_files = sorted(design_dir.glob("*.md")) if design_dir.is_dir() else []
                    if design_files:
                        design_text = design_files[-1].read_text(encoding="utf-8", errors="ignore")
                        ac_ids = sorted(set(re.findall(r"\bAC-[A-Z]+-\d+-\d+\b", design_text)))
                        if not ac_ids:
                            verifiable.append({"gate": "AC mapping covers design acceptance criteria", "status": "fail", "detail": f"No AC- entries found in {design_files[-1].name}"})
                        else:
                            missing_acs = [a for a in ac_ids if a not in impl_summary_text]
                            if missing_acs:
                                verifiable.append({"gate": "AC mapping covers design acceptance criteria", "status": "fail", "detail": f"Missing from implementation summary: {', '.join(missing_acs)}"})
                            else:
                                verifiable.append({"gate": "AC mapping covers design acceptance criteria", "status": "pass", "detail": f"All {len(ac_ids)} ACs from {design_files[-1].name} present in implementation summary"})
                    else:
                        verifiable.append({"gate": "AC mapping covers design acceptance criteria", "status": "fail", "detail": "No technical-design document found to check AC mapping against"})

                    # Check API documentation
                    api_doc_indicators = [
                        project_path / "docs" / "api",
                        project_path / "docs" / "apidoc",
                        project_path / "openapi.json",
                        project_path / "openapi.yaml",
                        project_path / "swagger.json",
                        project_path / "swagger.yaml",
                    ]
                    has_api_docs = any(p.is_file() or p.is_dir() for p in api_doc_indicators)
                    skip_recorded = bool(re.search(r"api\s+documentation[\s\S]{0,400}?(?:not\s+required|skip)", impl_summary_text, re.IGNORECASE))
                    if has_api_docs:
                        verifiable.append({"gate": "API documentation exists", "status": "pass"})
                    elif skip_recorded:
                        verifiable.append({"gate": "API documentation exists", "status": "pass", "detail": "Documented skip recorded in implementation summary"})
                    else:
                        verifiable.append({"gate": "API documentation exists", "status": "fail", "detail": "No API documentation found (openapi, swagger, or docs/api/) and no documented skip in implementation summary"})

                    # Check the project's test suite runs successfully
                    suite_passed, suite_detail = _run_test_suite(project_path)
                    if suite_passed is True:
                        verifiable.append({"gate": "Project test suite runs successfully", "status": "pass", "detail": suite_detail})
                    elif suite_passed is False:
                        verifiable.append({"gate": "Project test suite runs successfully", "status": "fail", "detail": suite_detail})
                    else:
                        verifiable.append({"gate": "Project test suite runs successfully", "status": "fail", "detail": suite_detail})
                else:
                    verifiable.append({"gate": "Source code directory exists", "status": "fail", "detail": "No src/lib/app/pkg directory found"})
                    verifiable.append({"gate": "Inline documentation present in source files", "status": "fail", "detail": "Cannot check without source files"})
                    verifiable.append({"gate": "API documentation exists", "status": "fail", "detail": "Cannot verify without source context"})
                    verifiable.append({"gate": "Project test suite runs successfully", "status": "fail", "detail": "Cannot verify without project context"})

                human_gates.append({"gate": "Code quality meets team standards", "requires": "human judgment", "detail": "Verify code meets team standards"})
                human_gates.append({"gate": "Implementation matches architectural intent", "requires": "human judgment", "detail": "Verify implementation follows the design"})
                human_gates.append({"gate": "No unexpected technical debt introduced", "requires": "human judgment", "detail": "Verify no unexpected technical debt was introduced"})

            elif gate_key == "review->testing":
                review_dir = project_path / "docs" / "review"
                if review_dir.is_dir():
                    review_files = sorted(review_dir.glob("*.md"))
                    if review_files:
                        verifiable.append({"gate": "Review report exists", "status": "pass", "detail": f"{len(review_files)} review file(s) found"})
                        # Check for self-review checklist
                        for review_file in review_files:
                            content = review_file.read_text(encoding="utf-8")
                            checklist_sections = ["Correctness", "Completeness", "Code Quality", "Security"]
                            found_sections = [s for s in checklist_sections if s in content]
                            missing_sections = [s for s in checklist_sections if s not in content]
                            if found_sections:
                                verifiable.append({"gate": f"Self-review checklist: {review_file.name}", "status": "pass", "detail": f"Found: {', '.join(found_sections)}"})
                            else:
                                verifiable.append({"gate": f"Self-review checklist: {review_file.name}", "status": "fail", "detail": f"Missing checklist sections: {', '.join(missing_sections)}"})
                    else:
                        verifiable.append({"gate": "Review report exists", "status": "fail", "detail": "docs/review/ exists but no .md files found"})
                else:
                    verifiable.append({"gate": "Review report exists", "status": "fail", "detail": "docs/review/ missing or empty"})

                human_gates.append({"gate": "Peer review complete", "requires": "human judgment", "detail": "Requires explicit human confirmation that peer review is complete"})
                human_gates.append({"gate": "Critical and major issues resolved", "requires": "human judgment", "detail": "Verify all critical and major issues are resolved"})

            elif gate_key == "testing->deployment":
                # Check test files
                test_dir = project_path / "tests"
                test_indicators = list(project_path.glob("**/test_*.py")) + list(project_path.glob("**/*_test.py")) + list(project_path.glob("**/*_test.go")) + list(project_path.glob("**/*.test.js")) + list(project_path.glob("**/*.test.ts")) + list(project_path.glob("**/*.spec.js")) + list(project_path.glob("**/*.spec.ts"))
                # Deduplicate
                seen = set()
                unique_tests = []
                for t in test_indicators:
                    if t not in seen:
                        seen.add(t)
                        unique_tests.append(t)
                if test_dir.is_dir() or unique_tests:
                    verifiable.append({"gate": "Test files exist", "status": "pass", "detail": f"{len(unique_tests)} test file(s) found"})
                else:
                    verifiable.append({"gate": "Test files exist", "status": "fail", "detail": "No test files found in tests/ or alongside source"})

                # Check test report
                test_report_dir = project_path / "docs" / "testing"
                if test_report_dir.is_dir():
                    test_report_files = sorted(test_report_dir.glob("*.md"))
                    if test_report_files:
                        verifiable.append({"gate": "Test report exists", "status": "pass", "detail": f"{len(test_report_files)} report(s) found"})
                        # Check for coverage threshold in report
                        report_content = test_report_files[-1].read_text(encoding="utf-8")
                        if "coverage" in report_content.lower():
                            verifiable.append({"gate": "Coverage documented in test report", "status": "pass"})
                        else:
                            verifiable.append({"gate": "Coverage documented in test report", "status": "fail", "detail": "No coverage information in test report"})

                        # Check AC traceability against design
                        design_dir = project_path / "docs" / "design"
                        design_files = sorted(design_dir.glob("*.md")) if design_dir.is_dir() else []
                        if design_files:
                            design_text = design_files[-1].read_text(encoding="utf-8", errors="ignore")
                            ac_ids = sorted(set(re.findall(r"\bAC-[A-Z]+-\d+-\d+\b", design_text)))
                            if not ac_ids:
                                verifiable.append({"gate": "AC traceability covers design acceptance criteria", "status": "fail", "detail": f"No AC- entries found in {design_files[-1].name}"})
                            else:
                                missing_acs = [a for a in ac_ids if a not in report_content]
                                if missing_acs:
                                    verifiable.append({"gate": "AC traceability covers design acceptance criteria", "status": "fail", "detail": f"Missing from test report: {', '.join(missing_acs)}"})
                                else:
                                    verifiable.append({"gate": "AC traceability covers design acceptance criteria", "status": "pass", "detail": f"All {len(ac_ids)} ACs from {design_files[-1].name} present in test report"})
                        else:
                            verifiable.append({"gate": "AC traceability covers design acceptance criteria", "status": "fail", "detail": "No technical-design document found to check traceability against"})
                    else:
                        verifiable.append({"gate": "Test report exists", "status": "fail", "detail": "docs/testing/ exists but no .md files found"})
                else:
                    verifiable.append({"gate": "Test report exists", "status": "fail", "detail": "docs/testing/ not found"})

                suite_passed, suite_detail = _run_test_suite(project_path)
                if suite_passed is True:
                    verifiable.append({"gate": "Test suite passes (exit code 0)", "status": "pass", "detail": suite_detail})
                elif suite_passed is False:
                    verifiable.append({"gate": "Test suite passes (exit code 0)", "status": "fail", "detail": suite_detail})
                else:
                    verifiable.append({"gate": "Test suite passes (exit code 0)", "status": "fail", "detail": suite_detail})

                human_gates.append({"gate": "Test coverage is sufficient", "requires": "human judgment", "detail": "Verify coverage meets defined threshold"})
                human_gates.append({"gate": "Regression risk is acceptable", "requires": "human judgment", "detail": "Verify regression risk is managed"})
                human_gates.append({"gate": "Edge cases are adequately tested", "requires": "human judgment", "detail": "Verify edge cases are covered"})

            elif gate_key == "deployment->monitoring":
                deploy_dir = project_path / "docs" / "deploy"
                if deploy_dir.is_dir():
                    deploy_files = sorted(deploy_dir.glob("*.md"))
                    if deploy_files:
                        verifiable.append({"gate": "Deployment config exists", "status": "pass", "detail": f"{len(deploy_files)} file(s) found"})
                        # Check for rollback procedure
                        rollback_found = False
                        rollback_content = ""
                        for df in deploy_files:
                            content = df.read_text(encoding="utf-8")
                            if "rollback" in content.lower():
                                rollback_found = True
                                rollback_content += content
                        if rollback_found:
                            rollback_sections = ["trigger", "rollback steps", "data rollback", "communication", "verification"]
                            found_rb = [s for s in rollback_sections if s in rollback_content.lower()]
                            if len(found_rb) >= 2:
                                verifiable.append({"gate": "Rollback procedure documented", "status": "pass", "detail": f"Found sections: {', '.join(found_rb)}"})
                            else:
                                verifiable.append({"gate": "Rollback procedure documented", "status": "fail", "detail": f"Rollback found but incomplete. Found: {', '.join(found_rb)}. Expected: {', '.join(rollback_sections)}"})
                        else:
                            verifiable.append({"gate": "Rollback procedure documented", "status": "fail", "detail": "No rollback procedure found in deployment docs"})
                    else:
                        verifiable.append({"gate": "Deployment config exists", "status": "fail", "detail": "docs/deploy/ exists but no .md files found"})
                else:
                    verifiable.append({"gate": "Deployment config exists", "status": "fail", "detail": "docs/deploy/ not found"})

                # Check CI/CD pipeline files
                cicd_indicators = [
                    project_path / ".github" / "workflows",
                    project_path / "Jenkinsfile",
                    project_path / ".gitlab-ci.yml",
                    project_path / "azure-pipelines.yml",
                    project_path / ".circleci" / "config.yml",
                    project_path / "Bitbucket Pipelines",
                ]
                has_cicd = any(p.is_file() or p.is_dir() for p in cicd_indicators)
                if has_cicd:
                    verifiable.append({"gate": "CI/CD pipeline files exist", "status": "pass"})
                else:
                    verifiable.append({"gate": "CI/CD pipeline files exist", "status": "fail", "detail": "No CI/CD pipeline files found"})

                human_gates.append({"gate": "Deployment is successful", "requires": "human judgment", "detail": "Post-deployment verification required"})
                human_gates.append({"gate": "System is stable in production", "requires": "human judgment", "detail": "Production stability confirmation"})

            else:
                result = [TextContent(type="text", text=f"Unknown gate transition: {gate_key}. Valid transitions: enhancement->requirements, requirements->design, design->implementation, implementation->review, review->testing, testing->deployment, deployment->monitoring")]
                logger.debug(f"call_tool: check_gate unknown transition, returning error")
                return result

            # Determine overall status
            all_verifiable_pass = all(g.get("status") == "pass" for g in verifiable)
            if not verifiable:
                overall = "fail"
            elif all_verifiable_pass:
                overall = "pass" if not human_gates else "pending"
            else:
                overall = "fail"

            result_text = json.dumps({"overall": overall, "verifiable_gates": verifiable, "human_gates": human_gates}, indent=2)
            result = [TextContent(type="text", text=result_text)]
            logger.debug(f"call_tool: check_gate overall={overall}, {len(verifiable)} verifiable, {len(human_gates)} human")
            return result
        elif name == "record_approval":
            project_path = Path(args.get("project_path", ""))
            phase = args.get("phase", "")
            decision = args.get("decision", "")
            caveats = args.get("caveats", "")
            risk_acceptances = args.get("risk_acceptances", [])

            # Get feature name from state
            state_file = project_path / "sdlc-state.json"
            feature = "unknown"
            if state_file.is_file():
                try:
                    state = json.loads(state_file.read_text(encoding="utf-8"))
                    feature = state.get("feature", "unknown")
                except json.JSONDecodeError:
                    pass

            # Create approval file
            decisions_dir = project_path / "docs" / "decisions"
            decisions_dir.mkdir(parents=True, exist_ok=True)
            approval_file = decisions_dir / f"{feature}-approval.md"

            timestamp = __import__("datetime").datetime.now().isoformat()

            # Build entry
            entry_lines = [
                f"## {phase} — {timestamp}",
                f"- **Decision**: {decision}",
            ]
            if caveats:
                entry_lines.append(f"- **Caveats**: {caveats}")
            if risk_acceptances:
                entry_lines.append("- **Risk Acceptances**:")
                for ra in risk_acceptances:
                    entry_lines.append(f"  - Risk: {ra.get('risk', 'N/A')}, Severity: {ra.get('severity', 'N/A')}")
                    entry_lines.append(f"    - Agent recommended: {ra.get('agent_recommendation', 'N/A')}")
                    entry_lines.append(f"    - Human decision: {ra.get('human_decision', 'N/A')}")
                    entry_lines.append(f"    - Justification: {ra.get('justification', 'N/A')}")

            entry_text = "\n".join(entry_lines) + "\n"

            # Append or create
            if approval_file.is_file():
                existing = approval_file.read_text(encoding="utf-8")
                approval_file.write_text(existing + "\n" + entry_text, encoding="utf-8")
            else:
                approval_file.write_text(f"# Approval Log — Feature: {feature}\n\n" + entry_text, encoding="utf-8")

            result = [TextContent(type="text", text=f"Approval recorded for {phase} phase in {approval_file}. Decision: {decision}")]
            logger.debug(f"call_tool: record_approval wrote to {approval_file}")
            return result
        logger.debug(f"call_tool: unknown tool name '{name}', returning empty")
        return []
    except Exception:
        logger.exception(f"call_tool: exception for name={name}")
        raise

async def main():
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(_async_exception_handler)
    logger.info("Starting AI-SDLC MCP Server...")
    logger.info(f"Server name: {app.name}")
    logger.info(f"Documents directory: {DOCS_DIR}")
    try:
        async with stdio_server() as (read_stream, write_stream):
            init_opts = app.create_initialization_options()
            logger.debug(f"Initialization options: {init_opts}")
            await app.run(read_stream, write_stream, init_opts)
    except Exception:
        logger.exception("main: unhandled exception during server run")
        raise

if __name__ == "__main__":
    asyncio.run(main())
