# SQL算法岗模板：Python + SQLite 处理数据集（核心逻辑）
# 用途：算法岗本地处理小数据集、统计样本分布
import sqlite3

def init_dataset_db():
    # 1. 连接数据库（不存在则自动创建）
    conn = sqlite3.connect("algorithm_data.db")
    cursor = conn.cursor()
    
    # 2. 创建数据集表（算法岗常用结构：标签+得分+特征）
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS dataset (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT,  -- 样本标签（如“猫”“狗”）
        score FLOAT, -- 模型预测得分
        feature1 FLOAT, -- 特征1（如图片宽度）
        feature2 FLOAT  -- 特征2（如图片高度）
    );
    """
    cursor.execute(create_table_sql)
    
    # 3. 插入模拟数据（实际用的时候替换为CSV导入）
    insert_data_sql = """
    INSERT INTO dataset (label, score, feature1, feature2)
    VALUES 
    ('cat', 0.92, 12.3, 45.6),
    ('dog', 0.88, 14.1, 39.2),
    ('cat', 0.75, 11.8, 42.9),
    ('dog', 0.95, 13.5, 40.1),
    ('bird', 0.80, 9.7, 35.3);
    """
    cursor.execute(insert_data_sql)
    
    # 4. 提交修改（建表/插数据必须执行）
    conn.commit()
    print("数据库初始化成功！")
    return conn, cursor

def query_dataset(conn, cursor):
    # 核心查询1：查看所有数据（算法岗看数据集全貌）
    cursor.execute("SELECT * FROM dataset;")
    all_data = cursor.fetchall()
    print("\n=== 所有数据集 ===")
    for row in all_data:
        print(row)
    
    # 核心查询2：筛选高置信度样本（score>0.9）
    cursor.execute("SELECT label, score FROM dataset WHERE score > 0.9;")
    high_score_data = cursor.fetchall()
    print("\n=== score>0.9的高置信度样本 ===")
    for row in high_score_data:
        print(row)
    
    # 核心查询3：分组统计标签数量（算法岗分析数据分布）
    cursor.execute("SELECT label, COUNT(*) FROM dataset GROUP BY label;")
    label_count = cursor.fetchall()
    print("\n=== 各标签样本数量 ===")
    for row in label_count:
        print(f"标签 {row[0]}: {row[1]} 条")

# 主函数：执行所有操作
if __name__ == "__main__":
    # 初始化数据库+插入数据
    conn, cursor = init_dataset_db()
    # 执行查询（算法岗核心统计逻辑）
    query_dataset(conn, cursor)
    # 关闭连接
    cursor.close()
    conn.close()
    print("\n操作完成！")
    # === Day2 新增：聚合函数+GROUP BY（算法岗核心统计）===
    # 1. 整体统计
    cursor.execute("SELECT COUNT(*), AVG(score) FROM dataset;")
    total, avg_score = cursor.fetchone()
    print("\n=== 整体数据统计 ===")
    print(f"总样本数：{total}，score均值：{round(avg_score, 2)}")
    
    # 2. 分组统计（核心）
    cursor.execute("SELECT label, COUNT(*), AVG(score) FROM dataset GROUP BY label;")
    group_stats = cursor.fetchall()
    print("\n=== 按标签分组统计 ===")
    for label, count, avg in group_stats:
        print(f"标签 {label}：{count} 条，score均值 {round(avg, 2)}")
