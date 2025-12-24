from fastapi import APIRouter, Query
router = APIRouter()
@router.post("/ask")
async def ask_ai(prompt: str = Query(...)):
    return {"factory_response": "Mocked AI Response", "input_received": prompt}