#!/bin/bash
# 快速验证项目配置

echo "🔍 验证 Matchmaker Backend 配置..."

# 检查 Python 文件
if [ -f "app/main.py" ]; then
    echo "✅ app/main.py 存在"
else
    echo "❌ app/main.py 不存在"
    exit 1
fi

# 检查 Dockerfile
if [ -f "Dockerfile" ]; then
    echo "✅ Dockerfile 存在"
else
    echo "❌ Dockerfile 不存在"
    exit 1
fi

# 检查 render.yaml
if [ -f "render.yaml" ]; then
    echo "✅ render.yaml 存在"
else
    echo "❌ render.yaml 不存在"
    exit 1
fi

# 检查 requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 存在"
else
    echo "❌ requirements.txt 不存在"
    exit 1
fi

# 验证 Python 语法
echo ""
echo "🐍 验证 Python 语法..."
python3 -m py_compile app/main.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python 语法正确"
else
    echo "❌ Python 语法错误"
    exit 1
fi

python3 -m py_compile app/core/config.py 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ config.py 语法正确"
else
    echo "❌ config.py 语法错误"
    exit 1
fi

echo ""
echo "📋 项目结构："
tree -L 3 -I '__pycache__|*.pyc|.git|.venv' . 2>/dev/null || find . -maxdepth 3 -type f -name "*.py" | head -20

echo ""
echo "✅ 所有配置检查通过！可以开始部署。"
