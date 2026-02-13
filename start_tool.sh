#!/bin/bash
# 一键启动数据工具脚本（Gradio可视化界面+日志）
echo "======================================"
echo "🎯 正在启动算法数据集可视化工具..."
echo "🌐 启动后访问：http://172.21.114.63:7860"
echo "📝 操作日志会保存到 data_tool.log 文件"
echo "======================================"

# 检查Python3是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python3！"
    exit 1
fi

# 检查Gradio是否安装（自动补装）
if ! python3 -c "import gradio" &> /dev/null; then
    echo "⚠️  未安装Gradio，正在自动安装..."
    python3 -m pip install gradio -i https://pypi.tuna.tsinghua.edu.cn/simple
fi

# 启动Gradio工具（带日志输出）
python3 gradio_data_tool.py