from fastapi import FastAPI, HTTPException
from phi.assistant import Assistant
from phi.llm.groq import Groq
from tool import get_products
import asyncio

app = FastAPI()

assistant = Assistant(
    llm=Groq(model="llama3-8b-8192"),
    description="Your an eccomerce site assistant that helps users get product details based on there query",
    tools=[get_products],
    show_tool_calls=False
)

@app.get("/query")
async def query_assistant(query: str):
    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, assistant.run, query, markdown=True, stream=False)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/status")
async def status_check():
    return {"assistant_status": "ready"}