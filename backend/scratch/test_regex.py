import re

def replace_context(match):
    path = match.group(1).strip()
    print(f"Matched path: {path}")
    return "SUBSTITUTED"

value = "{{user_context.default_notion_db}}"
regex = r'\{\{\s*user_context\.([\w\.]+)\s*\}\}'
new_value = re.sub(regex, replace_context, value)
print(f"Old: {value}")
print(f"New: {new_value}")
