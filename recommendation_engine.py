def generate_recommendation(
    finding,
    memories
):

    accepted = 0
    ignored = 0

    for memory in memories:

        text = memory.text.lower()

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