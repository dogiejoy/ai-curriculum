from pathlib import Path

# Path object — works on macOS, Linux, Windows เหมือนกัน
current = Path(__file__).parent       # folder ของ script นี้
project_root = current.parent.parent  # ขึ้น 2 ระดับ (ai-curriculum/)
print(f"Script in: {current}")
print(f"Project root: {project_root}")

# Construct path ด้วย / operator (overload)
env_file = project_root / ".env"
print(f"Env: {env_file}")
print(f"Exists: {env_file.exists()}")

# Read/write text ในบรรทัดเดียว
readme = current / "README.md"
readme.write_text("# Python idioms playground\n", encoding="utf-8")
print(readme.read_text())

# List files ใน folder — generator : glob
week01_files = (project_root / "week-01").glob("*.py")
for f in week01_files:
    print(f.name, "->", f.stat().st_size, "bytes")

# Recursive glob : rglob
all_python = project_root.rglob("*.py")  # ทุก .py ใน subfolder
print(f"Python files: {len(list(all_python))}")

# Path attributes
sample = Path("/Users/dogiejoy/side-projects/ai-curriculum/week-01/hello_claude.py")
print(f"Name: {sample.name}")              # hello_claude.py
print(f"Stem: {sample.stem}")              # hello_claude
print(f"Suffix: {sample.suffix}")          # .py
print(f"Parent: {sample.parent}")          # .../week-01
print(f"Parts: {sample.parts}")            # tuple ของ path components
