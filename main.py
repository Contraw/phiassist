from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from phi.assistant import Assistant
from phi.llm.groq import Groq
from tool import get_products
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

assistant = Assistant(
    llm=Groq(model="llama3-8b-8192"),
    description="You should never include in your response what tool you used",
    instructions=["You are an e-commerce site assistant that helps users get product details based on their query"],
    tools=[get_products],
    show_tool_calls=False,
    markdown=True,
)

# Exception handler for general exceptions
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"}
    )

# Define the query endpoint to handle GET requests asynchronously.
@app.get("/query")
async def query_assistant(query: str):
    try:
        response = await assistant.run(query, stream=False)
        return {"response": response}
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
@app.get("/status")
async def status_check():
    return {"assistant_status": "ready"}
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the server...")
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the server...")