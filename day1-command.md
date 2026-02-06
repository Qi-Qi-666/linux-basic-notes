# Day1 Linux 核心命令（文件/目录操作）
## 1. 路径相关
- 绝对路径：从 `/` 开始，如 `/home/qi/test.txt`
- 相对路径：从当前目录开始，如 `test.txt`、`../doc`
- 家目录：`~`，根目录：`/`

## 2. 高频命令
| 命令 | 作用 | 示例 |
|------|------|------|
| `pwd` | 查看当前路径 | `pwd` |
| `ls` | 简单列出目录内容 | `ls -a`（显示隐藏文件） |
| `ll` | 详细列出目录内容 | `ll` |
| `cd` | 切换目录 | `cd ~`（家目录）、`cd ..`（上一级） |
| `mkdir` | 创建目录 | `mkdir -p a/b/c`（递归创建） |
| `touch` | 创建空文件 | `touch test.txt` |
| `cat` | 查看小文件内容 | `cat test.txt` |
| `cp` | 复制文件/目录 | `cp -r test test_bak` |
| `mv` | 移动/重命名 | `mv test.txt new.txt` |
| `rm` | 删除文件/目录 | `rm -rf test`（强制删除目录） |
