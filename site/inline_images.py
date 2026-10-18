
from pathlib import Path
import re
import base64
import shutil

SITE = Path("site")
HTML = SITE / "index.html"
IMAGES = SITE / "images"

if not HTML.exists():
    raise FileNotFoundError(f"Не найден файл: {HTML}")

# Создаём резервную копию HTML
backup = SITE / "index.html.backup"
shutil.copy2(HTML, backup)

html = HTML.read_text(encoding="utf-8")
replaced = []

def inline_image(match):
    tag = match.group(0)
    src_match = re.search(
        r"""src\s*=\s*(["'])/?images/(\d+)\.png\1""",
        tag,
        re.IGNORECASE
    )

    if not src_match:
        return tag

    number = src_match.group(2)
    image_path = IMAGES / f"{number}.png"

    if not image_path.exists():
        raise FileNotFoundError(f"Не найдено изображение: {image_path}")

    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    data_uri = f"data:image/png;base64,{encoded}"

    updated_tag = re.sub(
        r"""src\s*=\s*(["'])/?images/\d+\.png\1""",
        f'src="{data_uri}"',
        tag,
        count=1,
        flags=re.IGNORECASE
    )

    replaced.append(number)
    return updated_tag

html = re.sub(
    r"<img\b[^>]*>",
    inline_image,
    html,
    flags=re.IGNORECASE
)

if not replaced:
    raise RuntimeError(
        "Не найдены теги img с путями images/N.png. "
        "Проверь структуру HTML."
    )

HTML.write_text(html, encoding="utf-8")

print(f"Встроено изображений: {len(replaced)}")
print("Номера:", ", ".join(replaced))
print(f"Резервная копия: {backup}")
print(f"Обновлённый файл: {HTML}")
