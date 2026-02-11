# 简单说：这是能在浏览器用的数据库工具代码
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import sqlite3
import csv
import os

# 1. 建一个“接口服务”
app = FastAPI(
    title="我的数据集小工具",
    description="能查数据、能传CSV的小接口",
    version="1.0"
)

# 2. 连数据库的小函数（不用改）
def get_db_connection():
    try:
        conn = sqlite3.connect("algorithm_data.db")
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"连数据库失败：{str(e)}")

# 3. 功能1：浏览器查标签统计
@app.get("/api/label_stats", summary="查各标签有多少数据")
def get_label_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查每个标签的数量和平均分
    cursor.execute("""
        SELECT label, COUNT(*) as count, AVG(score) as avg_score 
        FROM dataset 
        GROUP BY label
    """)
    
    # 整理成好看的格式
    results = []
    for row in cursor.fetchall():
        results.append({
            "标签": row["label"],
            "数据条数": row["count"],
            "平均得分": round(row["avg_score"], 2)
        })
    
    conn.close()
    # 返回结果（浏览器能看懂的格式）
    return JSONResponse(
        status_code=200,
        content={
            "状态": "成功",
            "提示": "查询完啦",
            "数据": results
        }
    )

# 4. 功能2：浏览器上传CSV存数据库
@app.post("/api/upload_csv", summary="上传CSV文件存数据库")
def upload_csv(file: UploadFile = File(...)):
    # 只让传CSV文件
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="只能传CSV文件哦！")
    
    try:
        # 先保存上传的文件
        csv_path = f"upload_{file.filename}"
        with open(csv_path, "wb") as f:
            f.write(file.file.read())
        
        # 连数据库，清空旧数据重建表
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS dataset;")
        cursor.execute("""
            CREATE TABLE dataset (
                label TEXT,
                score FLOAT,
                feature1 FLOAT,
                feature2 FLOAT
            );
        """)
        conn.commit()
        
        # 读CSV并存进数据库
        with open(csv_path, "r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            # 检查CSV列对不对
            required_cols = ["label", "score", "feature1", "feature2"]
            if not all(col in csv_reader.fieldnames for col in required_cols):
                raise HTTPException(status_code=400, detail=f"CSV里得有这些列：{required_cols}")
            
            insert_sql = "INSERT INTO dataset VALUES (?, ?, ?, ?)"
            data_list = []
            for row in csv_reader:
                data = (
                    row["label"],
                    float(row["score"]),
                    float(row["feature1"]),
                    float(row["feature2"])
                )
                data_list.append(data)
            
            cursor.executemany(insert_sql, data_list)
            conn.commit()
            total = len(data_list)
    
        # 删临时文件，关数据库
        os.remove(csv_path)
        conn.close()
        
        # 返回上传成功的提示
        return JSONResponse(
            status_code=200,
            content={
                "状态": "成功",
                "提示": f"CSV传好啦！一共存了{total}条数据",
                "数据": {"总条数": total}
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"传文件失败：{str(e)}")

# 启动服务的代码（不用改）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
# 5. 功能3：查单条数据详情（新增）
@app.get("/api/get_data/{data_id}", summary="查单条数据的详情")
def get_single_data(data_id: int):
     # 新增抗错1：检查ID是否为正数（防止输0、负数）
    if data_id <= 0:
        raise HTTPException(status_code=400, detail="数据ID必须是正数哦（比如1、2、3）！")
    
    conn = get_db_connection()
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查指定行的数据（按行号查）
    cursor.execute("""
        SELECT rowid, label, score, feature1, feature2 
        FROM dataset 
        WHERE rowid = ?
    """, (data_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail=f"没找到ID为{data_id}的数据哦！")
    
    # 返回单条数据详情
    return JSONResponse(
        status_code=200,
        content={
            "状态": "成功",
            "提示": "查到数据啦",
            "数据": {
                "数据ID": row["rowid"],
                "标签": row["label"],
                "得分": row["score"],
                "特征1": row["feature1"],
                "特征2": row["feature2"]
            }
        }
    )
# 新功能1：按标签、分数筛选数据
@app.get("/api/filter_data", summary="按标签/最低得分过滤数据")
def filter_data(label: str = None, min_score: float = 0.0):
    # 新增抗错1：检查分数是否在0-1之间（算法得分都是0-1，防止输负数、大于1的数）
    if min_score < 0 or min_score > 1:
        raise HTTPException(status_code=400, detail="最低得分必须在0到1之间哦（比如0.8、0.9）！")

    if label:
        cursor.execute("""
            SELECT rowid, label, score, feature1, feature2
            FROM dataset
            WHERE label = ? AND score >= ?
        """, (label, min_score))
    else:
        cursor.execute("""
            SELECT rowid, label, score, feature1, feature2
            FROM dataset
            WHERE score >= ?
        """, (min_score,))

    rows = cursor.fetchall()
    conn.close()

     # 新增抗错2：没查到符合条件的数据时，友好提示
    if not rows:
        if label:
            tip = f"没找到标签为{label}且得分≥{min_score}的数据哦！"
        else:
            tip = f"没找到得分≥{min_score}的数据哦！"
        raise HTTPException(status_code=404, detail=tip)

    data_list = []
    for r in rows:
        data_list.append({
            "ID": r["rowid"],
            "标签": r["label"],
            "得分": r["score"],
            "特征1": r["feature1"],
            "特征2": r["feature2"]
        })

    return {
        "状态": "成功",
        "查到条数": len(data_list),
        "数据": data_list
    }
# ========== 功能5 数据导出接口（修复版） ==========
@app.get("/api/export_csv", summary="把数据库数据导出为CSV文件")
def export_csv():
    """
    算法岗常用：把数据库里的所有数据导回CSV，方便后续模型训练
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询所有数据
    cursor.execute("SELECT label, score, feature1, feature2 FROM dataset")
    rows = cursor.fetchall()
    conn.close()

    # ★ 新增：把SQLite的特殊列表转成纯字典列表（关键修复！）

    # 新增抗错：数据库为空时，提示不用导出
    if not rows:
        raise HTTPException(status_code=404, detail="数据库里还没有数据哦！先上传CSV文件再导出～")
    

    rows_dict = []
    for row in rows:
        rows_dict.append({
            "label": row["label"],
            "score": row["score"],
            "feature1": row["feature1"],
            "feature2": row["feature2"]
        })
    
    # 生成CSV文件（保存到当前目录，文件名：exported_dataset.csv）
    csv_filename = "exported_dataset.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["label", "score", "feature1", "feature2"])
        writer.writeheader()  # 写列名
        # ★ 修改：把rows改成rows_dict
        writer.writerows(rows_dict)  # 写数据
    
    # 返回文件给浏览器下载（FastAPI自带的文件返回功能）
    from fastapi.responses import FileResponse
    return FileResponse(
        path=csv_filename,
        filename=csv_filename,
        media_type="text/csv"
    )
