def review_code(code):

    findings = []

    if "password =" in code:
        findings.append(
            "Hardcoded password detected"
        )

    if "print(" in code:
        findings.append(
            "Debug print statement detected"
        )

    return findings