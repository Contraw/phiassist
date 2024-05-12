from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Request, status, Depends
from phi.assistant import Assistant
from phi.llm.groq import Groq
from tool import search_products
import signal
import logging
import uvicorn

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_assistant() -> Assistant:
    return Assistant(
        llm=Groq(model="llama3-8b-8192", temperature=0.3),
        description="""
        Made by "Vizier".
        You are Jiji, an "Ethiopian" conversational AI chatbot that helps customers find products they're looking for by searching the store on their behalf.
        The e-commerce store that you search products on is called jiji.com.et.
        """,
        instructions=["Use the get_product function for product queries, don't make up answers by just looking at the previous chat.",
            "Using the provided product information, including product name, price, and link, create a comprehensive response in markdown format that summarizes the products details and the hyperlink the user can follow to view the product page",
            "Use Emoji's"],
        tools={search_products},
        show_tool_calls=False,
        num_history_messages=5,
        read_chat_history=True,
        markdown=True,
        debug_mode=True
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation Error"},
    )

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )

@app.post("/query")
def query_assistant(query: str, assistant: Assistant = Depends(create_assistant)):
    try:
        response = assistant.run(query, stream=False)
        return {"response": response}
    except TimeoutError as e:
        logger.error(f"Timeout error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=408, detail="Request Timeout")
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Register a signal handler to handle KeyboardInterrupt (Ctrl+C)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    uvicorn.run(app, host="0.0.0.0" )

