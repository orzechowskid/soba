"""AI-SDLC Framework MCP Server"""
import logging
import asyncio
import json
import traceback
import sys
import signal
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
    "requirements": "03-phase-requirements.md",
    "design": "04-phase-design.md",
    "implementation": "05-phase-implementation.md",
    "review": "06-phase-review.md",
    "testing": "07-phase-testing.md",
    "deployment": "08-phase-deployment.md",
    "monitoring": "09-phase-monitoring.md",
}

VALID_PHASES = ("requirements", "design", "implementation", "review", "testing", "deployment", "monitoring")

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
                # Infer phase
                current_phase = "requirements"
                if (project_path / "docs/adr").exists(): current_phase = "design"
                if (project_path / "docs/implementation").exists(): current_phase = "implementation"
                if (project_path / "docs/review").exists(): current_phase = "review"
                if (project_path / "docs/deploy").exists(): current_phase = "deployment"
                if (project_path / "docs/monitoring").exists(): current_phase = "monitoring"
            
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
            # Infer state from docs/ directories
            inferred = {"current_phase": "requirements", "feature": "unknown", "last_gate": "none"}
            if (project_path / "docs/adr").exists():
                inferred["current_phase"] = "design"
                inferred["last_gate"] = "requirements"
            if (project_path / "docs/implementation").exists():
                inferred["current_phase"] = "implementation"
                inferred["last_gate"] = "design"
            if (project_path / "docs/review").exists():
                inferred["current_phase"] = "review"
                inferred["last_gate"] = "implementation"
            if (project_path / "docs/deploy").exists():
                inferred["current_phase"] = "deployment"
                inferred["last_gate"] = "review"
            if (project_path / "docs/monitoring").exists():
                inferred["current_phase"] = "monitoring"
                inferred["last_gate"] = "deployment"
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
            state = {"current_phase": "requirements", "feature": feature, "last_gate": "none", "timestamp": datetime.datetime.now().isoformat()}
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
            
            if gate_key == "requirements->design":
                req_file = project_path / "requirements.md"
                if req_file.is_file():
                    content = req_file.read_text(encoding="utf-8")
                    verifiable.append({"gate": "requirements.md exists", "status": "pass"})
                    if "FR-" in content or "FR-" in content.upper():
                        verifiable.append({"gate": "Functional requirements present", "status": "pass"})
                    else:
                        verifiable.append({"gate": "Functional requirements present", "status": "fail", "detail": "No FR- entries found"})
                    if "AC-" in content or "Acceptance" in content:
                        verifiable.append({"gate": "Acceptance criteria present", "status": "pass"})
                    else:
                        verifiable.append({"gate": "Acceptance criteria present", "status": "fail", "detail": "No AC- entries or Acceptance section found"})
                    if "Constraint" in content:
                        verifiable.append({"gate": "Constraints section present", "status": "pass"})
                    else:
                        verifiable.append({"gate": "Constraints section present", "status": "fail", "detail": "No Constraints section found"})
                    if "Assumption" in content:
                        verifiable.append({"gate": "Assumptions section present", "status": "pass"})
                    else:
                        verifiable.append({"gate": "Assumptions section present", "status": "fail", "detail": "No Assumptions section found"})
                    if "Open Question" in content or "Out-of-Scope" in content:
                        verifiable.append({"gate": "Open questions / out-of-scope present", "status": "pass"})
                    else:
                        verifiable.append({"gate": "Open questions / out-of-scope present", "status": "fail", "detail": "No Open Questions or Out-of-Scope section found"})
                else:
                    verifiable.append({"gate": "requirements.md exists", "status": "fail", "detail": "File not found"})
                
                human_gates.append({"gate": "Requirements completeness", "requires": "human judgment", "detail": "Verify requirements are complete and correct"})
                human_gates.append({"gate": "Stakeholder alignment", "requires": "human judgment", "detail": "Verify business priority and stakeholder buy-in"})
            
            elif gate_key == "design->implementation":
                adr_dir = project_path / "docs" / "adr"
                if adr_dir.is_dir():
                    adr_files = list(adr_dir.glob("*.md"))
                    if len(adr_files) > 0:
                        verifiable.append({"gate": "docs/adr/ exists with ADRs", "status": "pass", "detail": f"{len(adr_files)} ADR(s) found"})
                        # Check ADR format
                        for adr in adr_files:
                            content = adr.read_text(encoding="utf-8")
                            if all(field in content for field in ["Context", "Decision"]):
                                verifiable.append({"gate": f"ADR format: {adr.name}", "status": "pass"})
                            else:
                                verifiable.append({"gate": f"ADR format: {adr.name}", "status": "fail", "detail": "Missing Context or Decision fields"})
                    else:
                        verifiable.append({"gate": "docs/adr/ exists with ADRs", "status": "fail", "detail": "Directory empty"})
                else:
                    verifiable.append({"gate": "docs/adr/ exists with ADRs", "status": "fail", "detail": "Directory not found"})
                
                human_gates.append({"gate": "Architecture soundness", "requires": "human judgment", "detail": "Verify architecture is appropriate"})
                human_gates.append({"gate": "Tradeoff analysis", "requires": "human judgment", "detail": "Verify tradeoffs are acceptable"})
            
            elif gate_key == "implementation->review":
                impl_dir = project_path / "docs" / "implementation"
                if impl_dir.is_dir() and any(impl_dir.glob("*.md")):
                    verifiable.append({"gate": "Implementation summary exists", "status": "pass"})
                else:
                    verifiable.append({"gate": "Implementation summary exists", "status": "fail", "detail": "docs/implementation/ missing or empty"})
                # Check for source files
                src_indicators = ["src", "lib", "app", "pkg"]
                has_src = any((project_path / d).is_dir() for d in src_indicators)
                if has_src:
                    verifiable.append({"gate": "Source code directory exists", "status": "pass"})
                else:
                    verifiable.append({"gate": "Source code directory exists", "status": "fail", "detail": "No src/lib/app/pkg directory found"})
                
                human_gates.append({"gate": "Code quality", "requires": "human judgment", "detail": "Verify code meets team standards"})
            
            elif gate_key == "review->testing":
                review_dir = project_path / "docs" / "review"
                if review_dir.is_dir() and any(review_dir.glob("*.md")):
                    verifiable.append({"gate": "Review report exists", "status": "pass"})
                else:
                    verifiable.append({"gate": "Review report exists", "status": "fail", "detail": "docs/review/ missing or empty"})
                
                human_gates.append({"gate": "Peer review complete", "requires": "human judgment", "detail": "Requires explicit human confirmation that peer review is complete"})
                human_gates.append({"gate": "Critical issues resolved", "requires": "human judgment", "detail": "Verify all critical and major issues are resolved"})
            
            elif gate_key == "testing->deployment":
                test_dir = project_path / "docs" / "testing"
                if test_dir.is_dir() and any(test_dir.glob("*.md")):
                    verifiable.append({"gate": "Test report exists", "status": "pass"})
                else:
                    verifiable.append({"gate": "Test report exists", "status": "fail", "detail": "docs/testing/ missing or empty"})
                # Check for test files
                test_indicators = list(project_path.glob("**/*test*")) + list(project_path.glob("**/*_test.*"))
                if test_indicators:
                    verifiable.append({"gate": "Test files exist", "status": "pass", "detail": f"{len(test_indicators)} test file(s) found"})
                else:
                    verifiable.append({"gate": "Test files exist", "status": "fail", "detail": "No test files found"})
                
                human_gates.append({"gate": "Test coverage sufficient", "requires": "human judgment", "detail": "Verify coverage is adequate"})
                human_gates.append({"gate": "Regression risk acceptable", "requires": "human judgment", "detail": "Verify edge cases are tested"})
            
            elif gate_key == "deployment->monitoring":
                deploy_dir = project_path / "docs" / "deploy"
                if deploy_dir.is_dir() and any(deploy_dir.glob("*.md")):
                    verifiable.append({"gate": "Deployment config exists", "status": "pass"})
                else:
                    verifiable.append({"gate": "Deployment config exists", "status": "fail", "detail": "docs/deploy/ missing or empty"})
                
                human_gates.append({"gate": "Deployment successful", "requires": "human judgment", "detail": "Post-deployment verification required"})
                human_gates.append({"gate": "System stable", "requires": "human judgment", "detail": "Production stability confirmation"})
            
            else:
                result = [TextContent(type="text", text=f"Unknown gate transition: {gate_key}. Valid transitions: requirements->design, design->implementation, implementation->review, review->testing, testing->deployment, deployment->monitoring")]
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
