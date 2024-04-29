import uvicorn
import os

if __name__ == "__main__":
    
    PORT = int(os.environ.get("PORT", 3000))
    print(f"Server is running on port {PORT}")
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)