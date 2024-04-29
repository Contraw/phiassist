from fastapi import FastAPI, HTTPException
from phi.assistant import Assistant
from phi.llm.groq import Groq
from tool import get_products

app = FastAPI()

# Initialize the assistant with the specified configuration.
assistant = Assistant(
    llm=Groq(model="llama3-8b-8192"),
    description="You should never include in your response what tool you used",
    instructions=["You are an e-commerce site assistant that helps users get product details based on their query"],
    tools=[get_products],
    show_tool_calls=False,
    markdown=True,
)

# Define the query endpoint to handle GET requests asynchronously.
@app.get("/query")
async def query_assistant(query: str):
    try:
        # Run the assistant asynchronously and return the response.
        response = await assistant.run(query, stream=False)
        return {"response": response}
    except Exception as e:
        # Raise an HTTPException if an error occurs.
        raise HTTPException(status_code=500, detail=str(e))

# Define a health check endpoint.
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Define a status check endpoint.
@app.get("/status")
async def status_check():
    return {"assistant_status": "ready"}