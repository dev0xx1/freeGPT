def blockify(block_name,
             text: str):
    return f"""
<{block_name}>
{text}
</{block_name}>
""".strip()
