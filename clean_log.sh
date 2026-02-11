#!/bin/bash
# 清理7天前的.log文件，记录清理日志
find ~/linux-basic-notes -name "*.log" -mtime +7 -delete
echo "$(date) - 已清理7天前的日志文件" >> clean_log_history.log
