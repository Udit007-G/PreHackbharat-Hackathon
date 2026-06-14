import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule_id: str
    message: str
    line: int
    evidence: str


SECRET_ASSIGNMENT = re.compile(
    r"\b(?:password|passwd|pwd|secret|api_key|token)\b\s*=\s*['\"][^'\"]+['\"]",
    re.IGNORECASE,
)


def review_code(code: str) -> list[Finding]:
    findings: list[Finding] = []

    for line_number, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()

        if SECRET_ASSIGNMENT.search(stripped):
            findings.append(
                Finding(
                    rule_id="hardcoded-secret",
                    message="Hardcoded secret detected",
                    line=line_number,
                    evidence=stripped,
                )
            )

        if "print(" in stripped and not stripped.startswith("#"):
            findings.append(
                Finding(
                    rule_id="debug-print",
                    message="Debug print statement detected",
                    line=line_number,
                    evidence=stripped,
                )
            )

    return findings
