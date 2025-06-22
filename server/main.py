from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contract_agents.master_agent import master_agent
from contract_agents.context_agent import summariser_agent
from contract_agents.web_search import search_web
from contract_agents.code_update import code_updater_agent
from models.code_masking import load_model, predict
from models.gnn_model import EnhancedFraudGNN
from scraping.token_address_scrape import scrape_token
from scraping.wallet_address_scrape import scrape_wallet
from scraping.scrape_transactions import get_wallet_transactions
from wallet_token_agents.master_wallet_agent import wallet_analyst_agent
from wallet_token_agents.master_token_agent import token_analyst_agent
from feedback_agents.potential_wallet_finder import wallet_finder
from feedback_agents.wallet_behaviour_analysis import fraud_analyzer
from utils.utils import fetch_all_wallet_data
from dotenv import load_dotenv
import asyncio

# -------------------------
# FastAPI App Initialization
# -------------------------
app = FastAPI()

# Allow all CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Global Model and Tokenizer
# -------------------------
model = None
tokenizer = None

@app.on_event("startup")
async def load_model_on_startup():
    print("Loading Keys...")
    load_dotenv()
    print("Keys loaded.")
    global model, tokenizer
    print("Loading model on startup...")
    model, tokenizer = await load_model()
    print("Model loaded.")
    print("Loading GNN model...")
    gnn_model = EnhancedFraudGNN(in_channels=15, hidden_channels=512, out_channels=1, heads=4)
    print(f"GNN model loaded with architecture: {gnn_model}")

# -------------------------
# Request Model
# -------------------------
class ContractRequest(BaseModel):
    contract: str

# -------------------------
# Endpoint
# -------------------------
@app.post("/smart_contract")
async def analyze_smart_contract(req: ContractRequest):
    contract = req.contract
    print("Predicting Vulnerability...")
    vulnerability = await predict(model, tokenizer, contract)
    print("Vulnerability Detected:", vulnerability)

    print("Running Master Agent...")
    data = await master_agent(contract, vulnerability)  # Empty context for now

    searches = data.get("searches", [])
    vulnerability_reasoning = data.get("vulnerability_reasoning", "")
    vulnerabilities = data.get("vulnerabilities", [])

    print("Generating Searches...")
    search_response = await search_web(searches)

    print("Generating Summary...")
    summary = await summariser_agent(search_response, contract, vulnerability_reasoning, vulnerabilities)

    return {
        "summary": summary
    }

@app.post("/update_code")
async def update(request: Request):
    """
    Endpoint to update code based on the provided request.
    This is a placeholder for the actual implementation.
    """
    data = await request.json()
    code = data.get("code", "")
    changes = data.get("changes", "")
    
    # Call the summariser agent with the provided code and vulnerabilities
    updated_code = await code_updater_agent(code, changes)
    
    updated_code = updated_code.strip()
    if updated_code.startswith("```"):
        updated_code = updated_code[3:]
    if updated_code.endswith("```"):
        updated_code = updated_code[:-3]

    return {"updated_code": updated_code}

@app.post("/wallet_score")
async def score_wallet(request: Request):
    """
    Endpoint to score a wallet based on the provided request.
    This is a placeholder for the actual implementation.
    """
    data = await request.json()
    wallet_address = data.get("wallet_address", "")
    
    if not wallet_address:
        return {"error": "Wallet address is required"}
    
    wallet_data = await scrape_wallet(wallet_address)

    report = await wallet_analyst_agent(wallet_data)
    return {"report": report}
    
@app.post("/token_score")
async def score_token(request: Request):
    """
    Endpoint to score a token based on the provided request.
    This is a placeholder for the actual implementation.
    """
    data = await request.json()
    token_address = data.get("token_address", "")
    
    if not token_address:
        return {"error": "Token address is required"}
    
    token_data = await scrape_token(chain_id="8453", addresses=[token_address])

    report = await token_analyst_agent(token_data)
    return {"report": report}

@app.post("/feedback")
async def feedback(request: Request):
    """
    Endpoint to handle feedback from the user.
    This is a placeholder for the actual implementation.
    """
    data = await request.json()
    fdata = data.get("fdata", "")
    wallet_address = data.get("wallet_address", "")
    token_address = data.get("token_address", "")
    amt = data.get("amt", "")

    if not fdata or not wallet_address:
        return {"error": "Feedback data, wallet address, token address, and amount are required"}
    
    transaction_details = await get_wallet_transactions(wallet_address, token_address)

    report = await wallet_finder(fdata, wallet_address, token_address, amt, transaction_details)

    results_dict = await fetch_all_wallet_data(report["search_queries"])

    # print(results_dict)

    final_results = await fraud_analyzer(fdata, wallet_address, token_address, amt, transaction_details, results_dict)

    return {"report": final_results}

# uvicorn main:app --reload --host 0.0.0.0 --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)