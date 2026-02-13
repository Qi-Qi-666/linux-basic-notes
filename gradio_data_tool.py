# 新增：导入日志库（Python自带，不用额外装）
import logging
import time

# 配置日志：记录到文件+控制台都能看到
logging.basicConfig(
    level=logging.INFO,  # 记录INFO及以上级别的日志
    format="%(asctime)s - %(levelname)s - %(message)s",  # 日志格式：时间-级别-内容
    handlers=[
        logging.FileHandler("data_tool.log", encoding="utf-8"),  # 日志保存到data_tool.log文件
        logging.StreamHandler()  # 同时在终端显示日志
    ]
)
logger = logging.getLogger(__name__)

# 原有导入代码（修复HTTPException导入路径）
import gradio as gr
import sqlite3
import csv
from fastapi import HTTPException  # 适配新版FastAPI的导入规则

# 复用之前的数据库连接函数（不用改）
def get_db_connection():
    conn = sqlite3.connect("algorithm_data.db")
    conn.row_factory = sqlite3.Row  # 让查询结果能按列名访问
    return conn

# 1. 上传CSV到数据库（整合之前的上传逻辑+抗错+日志）
def upload_csv_to_db(file):
    # 新增：记录操作开始
    logger.info("开始执行【上传CSV】操作")
    if file is None:
        logger.warning("上传CSV失败：未选择任何文件")  # 新增：记录警告日志
        return "❌ 请先选择要上传的CSV文件！"
    try:
        # 连接数据库，创建表（如果不存在）
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dataset (
                label TEXT,
                score REAL,
                feature1 REAL,
                feature2 REAL
            )
        """)
        # 清空旧数据（避免重复）
        cursor.execute("DELETE FROM dataset")
        
        # 读取上传的CSV文件，插入数据库
        with open(file.name, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                # 抗错：检查score/feature1/feature2是否是数字
                try:
                    score = float(row["score"])
                    feature1 = float(row["feature1"])
                    feature2 = float(row["feature2"])
                except ValueError:
                    conn.close()
                    logger.error("上传CSV失败：某行的分数/特征不是数字！")
                    return f"❌ CSV数据错误：某行的分数/特征不是数字！"
                # 插入数据
                cursor.execute("""
                    INSERT INTO dataset (label, score, feature1, feature2)
                    VALUES (?, ?, ?, ?)
                """, (row["label"], score, feature1, feature2))
        
        conn.commit()
        conn.close()
        logger.info("上传CSV成功：文件=%s" % file.name)  # 新增：记录成功日志
        return "✅ CSV文件上传成功！数据库已更新～"
    except Exception as e:
        logger.error("上传CSV失败：%s" % str(e))  # 新增：记录错误日志
        return f"❌ 上传失败：{str(e)}"

# 2. 查单条数据（整合之前的抗错逻辑+日志）
def get_single_data_ui(data_id):
    logger.info("开始执行【查询单条数据】操作，输入ID=%s" % data_id)  # 新增
    try:
        data_id = int(data_id)
        if data_id <= 0:
            logger.warning("查询单条数据失败：ID=%s必须是正数" % data_id)
            return "❌ 数据ID必须是正数哦（比如1、2、3）！", []
    except ValueError:
        logger.error("查询单条数据失败：ID=%s不是数字" % data_id)
        return "❌ ID必须是数字哦（比如1、2、3）！", []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT rowid, label, score, feature1, feature2 
        FROM dataset 
        WHERE rowid = ?
    """, (data_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        logger.warning("查询单条数据失败：ID=%s不存在" % data_id)  # 新增
        return f"❌ 没找到ID为{data_id}的数据哦！", []
    # 整理成表格格式返回
    result = [["数据ID", "标签", "得分", "特征1", "特征2"],
              [row["rowid"], row["label"], row["score"], row["feature1"], row["feature2"]]]
    logger.info("查询单条数据成功：ID=%s" % data_id)  # 新增
    return "✅ 查到数据啦～", result

# 3. 过滤数据（整合之前的抗错逻辑+日志）
def filter_data_ui(label, min_score):
    logger.info("开始执行【过滤数据】操作，标签=%s，最低得分=%s" % (label, min_score))  # 新增
    # 抗错：检查分数范围
    if min_score < 0 or min_score > 1:
        logger.warning("过滤数据失败：最低得分=%s超出0-1范围" % min_score)
        return "❌ 最低得分必须在0到1之间哦！", []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    if label.strip() != "":  # 填了标签就按标签+分数过滤
        cursor.execute("""
            SELECT rowid, label, score, feature1, feature2 
            FROM dataset 
            WHERE label = ? AND score >= ?
        """, (label, min_score))
    else:  # 没填标签就只按分数过滤
        cursor.execute("""
            SELECT rowid, label, score, feature1, feature2 
            FROM dataset 
            WHERE score >= ?
        """, (min_score,))
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        tip = f"❌ 没找到标签为{label}且得分≥{min_score}的数据哦！" if label else f"❌ 没找到得分≥{min_score}的数据哦！"
        logger.warning("过滤数据失败：标签=%s，最低得分=%s 无匹配数据" % (label, min_score))  # 新增
        return tip, []
    
    # 整理成表格格式
    result = [["数据ID", "标签", "得分", "特征1", "特征2"]]
    for row in rows:
        result.append([row["rowid"], row["label"], row["score"], row["feature1"], row["feature2"]])
    logger.info("过滤数据成功：找到%s条数据" % (len(result)-1))  # 新增
    return f"✅ 查到{len(result)-1}条符合条件的数据～", result

# 4. 导出CSV（整合之前的抗错逻辑+日志）
def export_csv_ui():
    logger.info("开始执行【导出CSV】操作")  # 新增
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT label, score, feature1, feature2 FROM dataset")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            logger.warning("导出CSV失败：数据库为空")  # 新增
            return "❌ 数据库里还没有数据哦！先上传CSV再导出～", None
        
        # 转成字典格式，写入CSV
        rows_dict = []
        for row in rows:
            rows_dict.append({
                "label": row["label"],
                "score": row["score"],
                "feature1": row["feature1"],
                "feature2": row["feature2"]
            })
        
        csv_filename = "exported_dataset.csv"
        with open(csv_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["label","score","feature1","feature2"])
            writer.writeheader()
            writer.writerows(rows_dict)
        
        logger.info("导出CSV成功：保存为exported_dataset.csv")  # 新增
        return "✅ CSV导出成功！点击下方文件下载～", csv_filename
    except Exception as e:
        logger.error("导出CSV失败：%s" % str(e))  # 新增
        return f"❌ 导出失败：{str(e)}", None

# 搭建Gradio可视化界面（核心：把功能组装成网页）
with gr.Blocks(title="数据集管理工具") as demo:
    gr.Markdown("# 📊 算法数据集管理工具")
    gr.Markdown("### 不用记接口，点按钮就能操作～")
    
    # 第一部分：上传CSV
    with gr.Tab("1. 上传CSV到数据库"):
        file_input = gr.File(label="选择要上传的CSV文件（列：label,score,feature1,feature2）", file_types=[".csv"])
        upload_btn = gr.Button("🚀 上传并更新数据库", variant="primary")
        upload_output = gr.Textbox(label="上传结果")
        upload_btn.click(upload_csv_to_db, inputs=file_input, outputs=upload_output)
    
    # 第二部分：查单条数据
    with gr.Tab("2. 查单条数据"):
        data_id_input = gr.Number(label="输入要查询的数据ID（正数）", value=1)
        query_btn = gr.Button("🔍 查询数据", variant="secondary")
        query_tip = gr.Textbox(label="查询提示")
        query_result = gr.Dataframe(label="查询结果", headers=["数据ID", "标签", "得分", "特征1", "特征2"])
        query_btn.click(get_single_data_ui, inputs=data_id_input, outputs=[query_tip, query_result])
    
    # 第三部分：过滤数据
    with gr.Tab("3. 按条件过滤数据"):
        label_input = gr.Textbox(label="输入要过滤的标签（留空则不按标签过滤）", placeholder="比如：cat")
        min_score_input = gr.Slider(label="最低得分（0-1）", minimum=0, maximum=1, value=0.8)
        filter_btn = gr.Button("🎯 过滤数据", variant="secondary")
        filter_tip = gr.Textbox(label="过滤提示")
        filter_result = gr.Dataframe(label="过滤结果", headers=["数据ID", "标签", "得分", "特征1", "特征2"])
        filter_btn.click(filter_data_ui, inputs=[label_input, min_score_input], outputs=[filter_tip, filter_result])
    
    # 第四部分：导出CSV
    with gr.Tab("4. 导出CSV文件"):
        export_btn = gr.Button("📥 导出数据库为CSV", variant="primary")
        export_tip = gr.Textbox(label="导出提示")
        export_file = gr.File(label="下载导出的CSV文件")
        export_btn.click(export_csv_ui, inputs=[], outputs=[export_tip, export_file])

# 启动Gradio服务（固定你的WSL IP，不用改）
if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,       # Gradio默认端口
        share=False             # 不用公开链接，只用本地访问
    )