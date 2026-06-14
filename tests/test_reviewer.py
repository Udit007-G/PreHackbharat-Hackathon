from reviewer import review_code

with open(
    "sample_code.py",
    "r"
) as f:
    code = f.read()

findings = review_code(code)

print(findings)