from typing import Any


class TemplateManager:
    """Renders deterministic Markdown templates from verified discovery data."""

    TITLES = {"srs": "Software Requirements Specification", "brd": "Business Requirements Document", "mom": "Minutes of Meeting", "client_summary": "Client Requirement Summary", "technical": "Technical Requirements Document"}

    def render(self, document_type: str, context: dict[str, Any]) -> str:
        sections = self._sections(document_type, context)
        return "\n\n".join([f"# {self.TITLES[document_type]}\n", *[f"## {name}\n{body}" for name, body in sections]]) + "\n"

    def _sections(self, kind: str, ctx: dict[str, Any]) -> list[tuple[str, str]]:
        overview = f"**Project:** {ctx['project'].title}\n\n**Meeting:** {ctx['meeting'].title}\n\n**Generated from:** approved discovery findings and meeting context."
        if kind == "srs":
            return [("1. Introduction", overview), ("2. Purpose", self._purpose(ctx)), ("3. Scope", ctx['project'].description or "Scope is to be confirmed during discovery."), ("4. Functional Requirements", self._requirements(ctx, "functional")), ("5. Non Functional Requirements", self._requirements(ctx, "non_functional")), ("6. System Features", self._requirements(ctx, "technical")), ("7. Constraints", self._constraints(ctx)), ("8. Assumptions", self._assumptions(ctx)), ("9. Future Scope", "Items not approved for the current scope should be assessed in a future phase.")]
        if kind == "brd":
            return [("Business Objective", self._purpose(ctx)), ("Business Requirements", self._requirements(ctx, "business")), ("Stakeholders", self._participants(ctx)), ("Business Rules", self._requirements(ctx, "functional")), ("Timeline", self._timeline(ctx)), ("Risks", self._constraints(ctx))]
        if kind == "mom":
            return [("Meeting Date", str(ctx['meeting'].scheduled_at)), ("Participants", self._participants(ctx)), ("Agenda", ctx['meeting'].agenda or "No agenda recorded."), ("Discussion Points", ctx['transcript'] or ctx['meeting'].description or "No transcript was available."), ("Decisions", self._requirements(ctx, None)), ("Pending Questions", self._questions(ctx, pending=True)), ("Next Steps", "Validate this document, resolve pending questions, and approve the agreed requirements.")]
        if kind == "client_summary":
            return [("Overview", overview), ("Agreed Requirements", self._requirements(ctx, None)), ("Open Items", self._questions(ctx, pending=True)), ("Recommended Next Steps", "Confirm open items and approve the requirements for delivery planning.")]
        return [("Technical Context", overview), ("Technical Requirements", self._requirements(ctx, "technical")), ("Quality Attributes", self._requirements(ctx, "non_functional")), ("Integration and Deployment Considerations", self._constraints(ctx)), ("Open Technical Questions", self._questions(ctx, pending=True))]

    @staticmethod
    def _purpose(ctx: dict[str, Any]) -> str:
        return ctx['project'].description or f"Define the requirements for {ctx['project'].title}."

    @staticmethod
    def _requirements(ctx: dict[str, Any], category: str | None) -> str:
        items = [item for item in ctx['requirements'] if category is None or item.category == category]
        return "\n".join(f"- **{item.title}**: {item.description or 'Details to be confirmed.'}" for item in items) or "No approved requirements are available for this section."

    @staticmethod
    def _participants(ctx: dict[str, Any]) -> str:
        return "\n".join(f"- {p.name}{f' ({p.role})' if p.role else ''}" for p in ctx['participants']) or "Participants were not recorded."

    @staticmethod
    def _questions(ctx: dict[str, Any], pending: bool) -> str:
        status = "pending" if pending else "answered"
        items = [q for q in ctx['questions'] if q.status == status]
        return "\n".join(f"- {q.question}" for q in items) or "None."

    @staticmethod
    def _timeline(ctx: dict[str, Any]) -> str:
        return str(ctx['project'].expected_end_date or "Timeline has not been agreed.")

    @staticmethod
    def _constraints(ctx: dict[str, Any]) -> str:
        return "\n".join(f"- {q.question}" for q in ctx['questions'] if q.status == "pending") or "No constraints have been formally recorded."

    @staticmethod
    def _assumptions(ctx: dict[str, Any]) -> str:
        return "Approved requirements reflect the current meeting outcome; unresolved questions remain assumptions until answered."
