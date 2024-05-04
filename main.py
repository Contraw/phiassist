from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from phi.assistant import Assistant
from phi.llm.groq import Groq
import asyncio
from tool import get_products
import logging
import functools

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
    
assistant = Assistant(
    llm=Groq(model="gemma-7b-it"),
    system_prompt=
    f"""
    Your role as the AI assistant for e-commerce site Jiji is to assist users in finding products through relevant suggestions.
    Ensure responses are accurate, concise, and user-focused.
    Use Markdown Reference links for formatting URLs in the tool responses in order to direct users to product pages, for example use the template: [link](url).
    Avoid creating fictitious examples or URLs and provide information solely based on tool data.
    """,
    tools=[get_products],
    num_history_messages=3,
    add_chat_history_to_messages=True,
    markdown=True
)

# Exception handler for general exceptions
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )

@app.get("/query")
async def query_assistant(query: str):
    try:
        # Prepare to call the synchronous assistant.run method correctly
        func = functools.partial(assistant.run, query, stream=False)
        # Use asyncio to run this function in the background
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, func)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))
