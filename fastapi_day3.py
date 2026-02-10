# FastAPI入门：第一个基础接口
from fastapi import FastAPI

# 1. 创建FastAPI应用实例（算法岗固定写法）
app = FastAPI(title="算法数据接口", version="1.0")

# 2. 定义接口：GET请求，路径为/hello
@app.get("/hello")
def hello_world(name: str = "算法工程师"):
    """
    第一个FastAPI接口：返回欢迎语
    - 参数name：可选，默认值为“算法工程师”
    """
    return {"message": f"你好，{name}！这是你的第一个FastAPI接口"}

# 3. 启动服务器（终端执行：uvicorn fastapi_day3:app --reload）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
