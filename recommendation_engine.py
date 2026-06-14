def generate_recommendation(
    finding,
    memories
):

    accepted = 0
    ignored = 0

    finding_lower = finding.lower()

    for memory in memories:

        text = memory.text.lower()

        # Password-related issue
        if "password" in finding_lower:

            if "password" not in text:
                continue

        # Debug-related issue
        elif "debug" in finding_lower:

            if (
                "debug" not in text
                and
                "print" not in text
            ):
                continue

        if "accepted" in text:
            accepted += 1

        if (
            "ignored" in text
            or
            "rejected" in text
        ):
            ignored += 1

    if accepted > ignored:

        return (
            f"{finding}\n\n"
            f"Past fixes were mostly accepted.\n"
            f"Recommend applying the same solution."
        )

    elif ignored > accepted:

        return (
            f"{finding}\n\n"
            f"Past fixes were often ignored.\n"
            f"Recommend stronger enforcement."
        )

    else:

        return (
            f"{finding}\n\n"
            f"No clear team preference found."
        )