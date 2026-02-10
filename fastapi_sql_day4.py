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
