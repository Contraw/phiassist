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
    llm=Groq(model="llama3-8b-8192"),
    description=
    """
    You are Jiji a AI chatbot that help's customers find products there looking for by searching the store on behalf of them.
    The eccomerce store that you search products on is called jiji.com.et.
    """,
    instructions=["The previous chat content is provided just so you can remember so Avoid creating fictitious products, examples or URLs based upon it",
                  "Use the get_product tool for new product queries dont make up answer by just looking at the previous chat." ],
    tools={get_products},
    show_tool_calls=False,
    num_history_messages=1,
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
