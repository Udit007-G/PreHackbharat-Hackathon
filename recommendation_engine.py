def _memory_text(memory) -> str:
    if isinstance(memory, str):
        return memory
    return getattr(memory, "text", str(memory))


def _matches_finding(finding, text: str) -> bool:
    rule_id = getattr(finding, "rule_id", "").lower()
    message = getattr(finding, "message", str(finding)).lower()
    text = text.lower()

    if rule_id == "hardcoded-secret" or "secret" in message or "password" in message:
        return any(term in text for term in ("secret", "password", "api key", "token"))

    if rule_id == "debug-print" or "debug" in message:
        return "debug" in text or "print" in text

    return message in text


def generate_recommendation(finding, memories) -> str:
    accepted = 0
    ignored = 0
    message = getattr(finding, "message", str(finding))

    for memory in memories:
        text = _memory_text(memory)

        if not _matches_finding(finding, text):
            continue

        lower_text = text.lower()

        if "accepted" in lower_text or "fixed" in lower_text:
            accepted += 1

        if "ignored" in lower_text or "rejected" in lower_text:
            ignored += 1

    if accepted > ignored:
        return (
            f"{message}\n\n"
            "Past fixes were mostly accepted.\n"
            "Recommend applying the same solution."
        )

    if ignored > accepted:
        return (
            f"{message}\n\n"
            "Past fixes were often ignored.\n"
            "Recommend stronger enforcement."
        )

    return (
        f"{message}\n\n"
        "No clear team preference found."
    )
