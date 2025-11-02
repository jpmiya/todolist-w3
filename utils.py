import os, json, re
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account

load_dotenv()

RPC_HTTP = os.getenv("RPC_HTTP")
CHAIN_ID = int(os.getenv("CHAIN_ID", "11155111"))
CONTRACT_ADDRESS = Web3.to_checksum_address(os.getenv("CONTRACT_ADDRESS"))
ACCOUNT_ENV = Web3.to_checksum_address(os.getenv("ACCOUNT_ADDRESS"))
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
account_obj = Account.from_key(PRIVATE_KEY)
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")

# --- Web3 + contrato ---
w3 = Web3(Web3.HTTPProvider(RPC_HTTP))
assert w3.is_connected(), "No conecta al RPC"
with open("ABI.json","r",encoding="utf-8") as f:
    ABI = json.load(f)
c = w3.eth.contract(address=CONTRACT_ADDRESS, abi=ABI)


def send_tx(tx_func):
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    base = w3.eth.gas_price
    tx = tx_func.build_transaction({
        "from": ACCOUNT_ADDRESS,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "maxFeePerGas": base * 2,
        "maxPriorityFeePerGas": max(int(base * 0.1), 1),
    })
    gas_est = w3.eth.estimate_gas(tx)
    tx["gas"] = int(gas_est * 1.2)
    signed = account_obj.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.raw_transaction) 
    rcpt = w3.eth.wait_for_transaction_receipt(txh)
    print("TX:", txh.hex(), "| status:", rcpt.status, "| gasUsed:", rcpt.gasUsed)
    if rcpt.status != 1:
        raise RuntimeError("La transacción revirtió (status 0)")
    return rcpt


def events_from_receipt(rcpt, event_name):
    # decodifica logs del receipt para el evento dado
    event = getattr(c.events, event_name)
    return event().process_receipt(rcpt)

def get_past_events(event_name, from_block=0, to_block='latest', argument_filters=None):
    # obtiene eventos históricos (si el nodo soporta createFilter)
    event = getattr(c.events, event_name)
    filt = event.create_filter(fromBlock=from_block, toBlock=to_block, argument_filters=argument_filters or {})
    return filt.get_all_entries()

def send_tx_payable(tx_func, tx_overrides=None):
    tx_overrides = tx_overrides or {}
    nonce = w3.eth.get_transaction_count(ACCOUNT_ADDRESS)
    base = w3.eth.gas_price
    tx_params = {
        "from": ACCOUNT_ADDRESS,
        "nonce": nonce,
        "chainId": CHAIN_ID,
        "maxFeePerGas": base * 2,
        "maxPriorityFeePerGas": max(int(base * 0.1), 1),
    }
    #esto agrega el value a los parametros de la tx, el value tiene que estar en wei. 
    tx_params.update(tx_overrides)

    tx = tx_func.build_transaction(tx_params)
    gas_est = w3.eth.estimate_gas(tx)
    tx["gas"] = int(gas_est * 1.2)
    signed = account_obj.sign_transaction(tx)
    txh = w3.eth.send_raw_transaction(signed.raw_transaction) 
    rcpt = w3.eth.wait_for_transaction_receipt(txh)
    print("TX:", txh.hex(), "| status:", rcpt.status, "| gasUsed:", rcpt.gasUsed)
    if rcpt.status != 1:
        raise RuntimeError("La transacción revirtió (status 0)")
    return rcpt


def print_event(rcpt, event_name):
    evs = events_from_receipt(rcpt, event_name)
    for e in evs:
        print(f"Evento {event_name}:", dict(e.args))