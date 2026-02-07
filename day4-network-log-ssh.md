# Day4 Linux 网络+日志+远程连接（算法岗部署必备）
## 1. 网络命令
| 命令 | 作用 | 示例 |
|------|------|------|
| ping github.com -c 4 | 测试连通性 | ping github.com -c 4 |
| ss -tulpn | grep 8000 | 查端口占用 | ss -tulpn | grep 8000 |

## 2. 日志查看
| 命令 | 作用 | 示例 |
|------|------|------|
| tail -f train.log | 实时看日志 | tail -f train.log |
| grep "error" train.log | 过滤关键词 | grep "error" train.log |

## 3. 远程连接
| 命令 | 作用 | 示例 |
|------|------|------|
| ssh root@服务器IP | 登录服务器 | ssh root@123.45.67.89 |
| scp -r 本地文件 服务器IP:路径 | 传输文件 | scp -r test.py root@IP:~/code/ |
