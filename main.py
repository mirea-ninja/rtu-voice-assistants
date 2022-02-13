import uvicorn
import logging
# from src.app import app

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        # logging.FileHandler("logs.log", mode='w', encoding='UTF-8'),
        logging.StreamHandler()
    ]
)

if __name__ == "__main__":
    uvicorn.run("src.app:app", host="0.0.0.0", port=3001, reload=True)
