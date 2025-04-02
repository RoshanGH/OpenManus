import json
import os

from app.logger import logger
import traceback

from datetime import datetime
from pydantic import BaseModel
import uuid
import asyncio
from utils_file import *

from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Task(BaseModel):
    id: str
    prompt: str
    created_at: datetime
    status: str
    steps: list = []

    def model_dump(self, *args, **kwargs):
        data = super().model_dump(*args, **kwargs)
        data["created_at"] = self.created_at.isoformat()
        return data


class TaskManager:
    def __init__(self):
        self.tasks = {}
        self.queues = {}

    def create_task(self, prompt: str, user_id='admin') -> Task:
        task_id = str(uuid.uuid4())
        # 创建用户文件夹

        task = Task(
            id=task_id, prompt=prompt, created_at=datetime.now(), status="pending"
        )
        self.tasks[task_id] = task
        self.tasks['user_id'] = user_id
        self.queues[task_id] = asyncio.Queue()
        return task

    async def update_task_step(
        self, task_id: str, step: int, result: str, step_type: str = "step"
    ):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.steps.append({"step": step, "result": result, "type": step_type})
            await self.queues[task_id].put(
                {"type": step_type, "step": step, "result": result}
            )
            await self.queues[task_id].put(
                {"type": "status", "status": task.status, "steps": task.steps}
            )

    async def complete_task(self, task_id: str):
        if task_id in self.tasks:
            task = self.tasks[task_id]
            task.status = "completed"
            await self.queues[task_id].put(
                {"type": "status", "status": task.status, "steps": task.steps}
            )
            await self.queues[task_id].put({"type": "complete"})

    async def fail_task(self, task_id: str, error: str):
        if task_id in self.tasks:
            self.tasks[task_id].status = f"failed: {error}"
            await self.queues[task_id].put({"type": "error", "message": error})


task_manager = TaskManager()


# 在运行任务之前就接管Manus的日志
class SSELogHandler:
    def __init__(self, task_id):
        self.task_id = task_id

    async def __call__(self, message):
        import re

        # Extract - Subsequent Content
        cleaned_message = re.sub(r"^.*? - ", "", message)

        event_type = "log"
        if "✨ Manus's thoughts:" in cleaned_message:
            event_type = "think"
        elif "🛠️ Manus selected" in cleaned_message:
            event_type = "tool"
        elif "🎯 Tool" in cleaned_message:
            event_type = "act"
        elif "📝 Oops!" in cleaned_message:
            event_type = "error"
        elif "🏁 Special tool" in cleaned_message:
            event_type = "complete"

        # print("test_log", f"【【{cleaned_message}】】")
        # print("[steps]", task_manager.tasks[self.task_id].steps)
        # 写入json
        user_path = os.path.join(os.path.join(os.getcwd(), 'task_logs'), task_manager.tasks['user_id'])
        if not os.path.exists(user_path):
            os.mkdir(user_path)
        json_path = os.path.join(user_path, f'{self.task_id}.json')
        # 记录到本地
        data = {}
        data['steps'] = task_manager.tasks[self.task_id].steps
        data['task_info'] = {
            "user_id": task_manager.tasks['user_id'],
            "created_at": round(datetime.timestamp(task_manager.tasks[self.task_id].created_at)),
            "prompt": task_manager.tasks[self.task_id].prompt,
            "status": task_manager.tasks[self.task_id].status
        }
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))

        await task_manager.update_task_step(
            self.task_id, 0, cleaned_message, event_type
        )


# 运行任务
async def run_task(task_id: str, prompt: str):
    try:
        task_manager.tasks[task_id].status = "running"
        from app.agent.manus import Manus
        agent = Manus(
            name="Manus",
            description="A versatile agent that can solve various tasks using multiple tools",
        )

        async def on_think(thought):
            await task_manager.update_task_step(task_id, 0, thought, "think")

        async def on_tool_execute(tool, input):
            await task_manager.update_task_step(
                task_id, 0, f"Executing tool: {tool}\nInput: {input}", "tool"
            )

        async def on_action(action):
            await task_manager.update_task_step(
                task_id, 0, f"Executing action: {action}", "act"
            )

        async def on_run(step, result):
            await task_manager.update_task_step(task_id, step, result, "run")

        sse_handler = SSELogHandler(task_id)

        # 通过接管日志来实现返回数据
        logger.add(sse_handler)

        result = await agent.run(prompt)
        await task_manager.update_task_step(task_id, 1, result, "result")
        await task_manager.complete_task(task_id)
    except Exception as e:
        print(traceback.print_exc())
        print(e)
        await task_manager.fail_task(task_id, str(e))


@app.get("/tasks/{user_id}")
async def get_tasks(user_id: str):
    user_path = os.path.join(os.path.join(os.getcwd(), 'task_logs'), user_id)
    # 判断当前有没有历史记录
    if not os.path.exists(user_path):
        return JSONResponse(
            content=[],
            headers={"Content-Type": "application/json"},
        )
    # 存在则获取目录下所有的json文件
    file_list = get_json_files(user_path)
    task_infos = []
    for file_path in file_list:
        json_data = read_file(file_path, to_json=True)
        if 'task_info' not in json_data.keys():
            continue
        task_infos.append(json_data['task_info'])
    # 排序
    sorted_tasks = sorted(task_infos, key=lambda x: x["created_at"], reverse=True)
    return JSONResponse(
        content=sorted_tasks,
        headers={"Content-Type": "application/json"},
    )


@app.get("/get_task/{user_id}/{task_id}")
async def get_task(user_id: str, task_id: str):
    user_path = os.path.join(os.path.join(os.getcwd(), 'task_logs'), user_id)
    task_path = os.path.join(user_path, f'{task_id}.json')

    if task_id not in task_manager.tasks:
        # 不在实时的任务里, 就说明可能执行完了
        if not os.path.exists(task_path):
            return JSONResponse(
                content=[],
                headers={"Content-Type": "application/json"},
            )
        # 到这里说明就任务已经有过记录, 直接读取返回
        json_data = read_file(task_path, to_json=True)
        return JSONResponse(
            content=json_data,
            headers={"Content-Type": "application/json"},
        )
    else:
        # 在实时执行的task
        data = {}
        data['steps'] = task_manager.tasks[task_id].steps
        data['task_info'] = {
            "user_id": task_manager.tasks[user_id],
            "created_at": round(datetime.timestamp(task_manager.tasks[task_id].created_at)),
            "prompt": task_manager.tasks[task_id].prompt,
            "status": task_manager.tasks[task_id].status
        }
        return JSONResponse(
            content=data,
            headers={"Content-Type": "application/json"},
        )



if __name__ == '__main__':

    task = task_manager.create_task("我需要你帮我分析jcma公司在20250320-20250326之前的编导素材时长在31秒到60秒之间的素材消耗，生成一份可视化的详细数据MD报告")
    # print("task_id", task.id)
    asyncio.run(run_task(task.id, task.prompt))
    # =======================================
    # import uvicorn
    # uvicorn.run(app, host='localhost', port=5172)
