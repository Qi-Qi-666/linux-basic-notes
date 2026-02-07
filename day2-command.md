# Day2 Linux 核心命令（权限+查找+进程）
## 1. 权限管理
| 命令 | 作用 | 示例 |
|------|------|------|
| chmod | 修改权限 | chmod +x test.sh |
| chown | 修改所有者 | sudo chown qi:qi test.txt |

## 2. 查找命令
| 命令 | 作用 | 示例 |
|------|------|------|
| find | 按文件名找 | find ~ -name "*.md" |
| grep | 按内容找 | grep -r "linux" . |

## 3. 进程管理
| 命令 | 作用 | 示例 |
|------|------|------|
| ps aux | 查看进程 | ps aux | grep python |
| kill | 终止进程 | kill -9 1234 |
