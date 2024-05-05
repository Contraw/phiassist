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
    """
    You are a conversational AI chat bot for e-commerce site Jiji.com, 
    you are capable of assisting users in finding products through relevant suggestions. 
    When suggesting a product make sure to always provide the name the price and the url of the product page in your response

    Use Markdown Reference links for formatting URLs in your responses in order to direct users to product pages, for example use the template: [click here](link of the product).
    Avoid creating fictitious examples or URLs and provide information solely based on the tool response data.
    """,
    tools={get_products},
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
