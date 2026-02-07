# Day3 Linux 环境配置 + Shell 脚本（算法岗核心）
## 1. Conda 环境管理
| 命令 | 作用 | 示例 |
|------|------|------|
| conda create -n ml_env python=3.10 -y | 创建环境 | conda create -n ml_env python=3.10 -y |
| conda activate ml_env | 激活环境 | conda activate ml_env |
| pip install -r requirements.txt | 批量装依赖 | pip install -r requirements.txt |

## 2. Shell 脚本
- 第一行：#!/bin/bash
- 加执行权限：chmod +x 脚本.sh
- 运行：./脚本.sh
