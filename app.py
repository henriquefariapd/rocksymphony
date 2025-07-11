"""
Ponto de entrada principal para o Heroku
"""
from BackEnd.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
