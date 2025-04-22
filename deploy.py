import os
import base64
from dotenv import load_dotenv
from algosdk import account, transaction
from algosdk.v2client import algod
from algosdk.transaction import StateSchema
from pyteal import compileTeal, Mode
from algosdk.logic import get_application_address
from algosdk import logic
from algosdk.logic import address as logic_address



import sys
import json


load_dotenv()

# === ALGOD SETUP ===
ALGOD_TOKEN = os.getenv("TESTNET_ALGOD_TOKEN")
ALGOD_URL = os.getenv("TESTNET_ALGOD_URL")
ALGOD_CLIENT = algod.AlgodClient(ALGOD_TOKEN, ALGOD_URL)
ADDRESS = os.getenv("ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")


# === COMPILE TEAL ON CHAIN ===
def compile_teal_source(teal_source):
    compile_response = ALGOD_CLIENT.compile(teal_source)
    return base64.b64decode(compile_response['result'])


# === DEPLOY STATEFUL ===
def deploy_stateful_approval_clear(approval_teal, clear_teal):
    approval_prog = compile_teal_source(approval_teal)
    clear_prog = compile_teal_source(clear_teal)

    global_schema = StateSchema(num_uints=1, num_byte_slices=1)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)

    params = ALGOD_CLIENT.suggested_params()
    txn = transaction.ApplicationCreateTxn(
        sender=ADDRESS,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC.real,
        approval_program=approval_prog,
        clear_program=clear_prog,
        global_schema=global_schema,
        local_schema=local_schema,
    )

    signed_txn = txn.sign(PRIVATE_KEY)
    tx_id = ALGOD_CLIENT.send_transaction(signed_txn)
    txn_response = transaction.wait_for_confirmation(ALGOD_CLIENT, tx_id, 5)

    app_id = txn_response['application-index']
    return app_id


# === DEPLOY STATELESS ===
def deploy_stateless(teal_source):
    logic = compile_teal_source(teal_source)
    return logic_address(logic)
    #return account.address_from_program(logic)

    #logic_address = logic.address(logic)
    #return logic_address


# === MAIN DEPLOY FUNCTION ===
def deploy_contract(code, contract_type, lang):
    try:
        if lang.lower() == "pyteal":
            namespace = {}
            exec(code, namespace)

            if contract_type.lower() == "stateful":
                approval_fn = namespace.get("approval")
                clear_fn = namespace.get("clear")
                if not approval_fn or not clear_fn:
                    return "❌ Error: PyTeal must define 'approval()' and 'clear()' functions"

                approval_teal = compileTeal(approval_fn(), mode=Mode.Application)
                clear_teal = compileTeal(clear_fn(), mode=Mode.Application)
                app_id = deploy_stateful_approval_clear(approval_teal, clear_teal)
                return f"✅ Deployed Stateful PyTeal Contract with App ID: {app_id}"

            elif contract_type.lower() == "stateless":
                logic_fn = namespace.get("logic")
                if not logic_fn:
                    return "❌ Error: PyTeal must define a 'logic()' function for stateless"
                teal = compileTeal(logic_fn(), mode=Mode.Signature)
                address = deploy_stateless(teal)
                return f"✅ Deployed Stateless PyTeal Contract at Address: {address}"

        elif lang.lower() == "teal":
            if contract_type.lower() == "stateful":
                # Split TEAL code assuming a marker between approval and clear
                if "// CLEAR_PROGRAM" not in code:
                    return "❌ Error: Please separate approval and clear TEAL with '// CLEAR_PROGRAM' marker"
                approval_teal, clear_teal = code.split("// CLEAR_PROGRAM", 1)
                app_id = deploy_stateful_approval_clear(approval_teal.strip(), clear_teal.strip())
                return f"✅ Deployed Stateful TEAL Contract with App ID: {app_id}"
            elif contract_type.lower() == "stateless":
                address = deploy_stateless(code)
                return f"✅ Deployed Stateless TEAL Contract at Address: {address}"

        return "❌ Error: Invalid type or language"

    except Exception as e:
        return f"❌ Deployment failed: {str(e)}"

if __name__ == "__main__":
    for line in sys.stdin:
        try:
            #request = json.loads(line)
            request = { "action": "deploy", "code": "from pyteal import *\ndef logic(): return And(Txn.receiver() == Addr(\"ZZNVNYBXZBQP22BNCZFMSMNT6ZGDOPWWUOJBXRGPLT7DKRD5GKBAWJ4NAM\"), Txn.amount() > Int(0))", "contract_type": "stateless", "lang": "pyteal" }
            if request.get("action") == "deploy":
                code = request.get("code")
                contract_type = request.get("contract_type")
                lang = request.get("lang")

                if not all([code, contract_type, lang]):
                    raise ValueError("Missing one or more required fields: code, contract_type, lang")

                result = deploy_contract(code, contract_type, lang)
                print(json.dumps({ "response": result }))
                sys.stdout.flush()

            else:
                raise ValueError("Unknown action")

        except Exception as e:
            print(json.dumps({ "error": str(e) }))
            sys.stdout.flush()
