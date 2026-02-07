# Day5 Linux 进阶技巧 + 核心总结（算法岗闭环）
## 1. 压缩解压
| 命令 | 作用 | 算法岗示例 |
|------|------|------------|
| zip -r 包名.zip 目录 | 打包为zip | zip -r project.zip ./code/ |
| unzip 包名.zip -d 目录 | 解压zip | unzip dataset.zip -d ./data/ |
| tar -zcvf 包名.tar.gz 目录 | 打包为tar.gz | tar -zcvf model.tar.gz ./weights/ |
| tar -zxvf 包名.tar.gz -C 目录 | 解压tar.gz | tar -zxvf model.tar.gz -C /root/code/ |

## 2. 后台运行程序
- 核心：nohup 命令 > 日志文件 2>&1 &
- 示例：nohup ./train.sh > train.log 2>&1 &
- 查看进程：ps aux | grep 程序名
- 终止进程：kill -9 PID

## 3. 定时任务（crontab）
- 编辑：crontab -e
- 时间格式：分 时 日 月 周 命令
- 示例：0 1 * * * /home/qi/clean_log.sh（每天凌晨1点清理日志）

## 4. 前4天核心总结
- Day1：文件/目录基础操作；
- Day2：权限/查找/进程管理；
- Day3：Conda环境+Shell脚本；
- Day4：网络/日志/远程连接；
- Day5：压缩/后台/定时任务（进阶提效）。
