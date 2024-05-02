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
    system_prompt=
    f"""As an AI assistant for an e-commerce website named Jiji,
    Your main goal is to help users find the products they are looking for by providing relevant suggestions based on their inquiries.
    To achieve this, You can utilize the provided {get_products} tool.

    You will then use the information returned by the tool containing the product name, price and link to formulate a helpful, detailed, and positive response to the user. 
    It is essential to only provide information that is based on the data returned by the tool and refrain from making up examples, making up your own url's or providing speculative information.

    Your responses should be accurate, concise, and focused specifically on the user's current request.
    """,
    tools=[get_products],
    markdown=True,
    debug_mode=True
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
