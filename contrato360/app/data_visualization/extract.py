import re


def extrai_codigo_python(text):
    match = re.search(r'```python(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None