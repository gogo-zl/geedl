import os
import re
import subprocess
from pathlib import Path

# 设置路径
project_dir = Path(__file__).resolve().parent
version_path = project_dir / "geedl" / "__version__.py"

# 读取并解析旧版本号
content = version_path.read_text(encoding="utf-8")
old_version = re.search(r'__version__\s*=\s*"(.+?)"', content).group(1)

# 升级 patch 版本号
major, minor, patch = map(int, old_version.split('.'))
new_version = f"{major}.{minor}.{patch + 1}"

# 替换写入新版本
new_content = re.sub(r'__version__\s*=\s*".+?"', f'__version__ = "{new_version}"', content)
version_path.write_text(new_content, encoding="utf-8")
print(f"版本更新：{old_version} → {new_version}")

# 清除旧构建文件
for folder in ["build", "dist", "geedl.egg-info"]:
    subprocess.run(["rmdir", "/s", "/q", folder], shell=True)

# 构建新版本
subprocess.run("python setup.py sdist bdist_wheel", shell=True)

# 上传到 PyPI
subprocess.run("twine upload dist/*", shell=True)

# Git 提交 + tag + push
subprocess.run("git add -A", shell=True)
subprocess.run(f'git commit -m "Release v{new_version}"', shell=True)
subprocess.run(f"git tag v{new_version}", shell=True)
subprocess.run("git push origin master --tags", shell=True)

print("发布完成")
