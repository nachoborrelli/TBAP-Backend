import web3, json, os
from web3.auto import w3
from eth_account import Account
from eth_account.messages import encode_defunct
from django_base.settings import CONTRACT_ADDRESS, SIGNER_WALLET_PRIV_KEY
WALLET_PUB_ADDRESS="0x7db0FAD6B9e2fB362bAD6fB43F1e3aDd48F744D5"

#example backend method
# def sign_item_crafting(self, address, item_data):
#     nonce = w3_data_repository.get_new_crafting_nonce()
#     contract_address = ITEM_CONTRACT_ADDRESS
#     sig = web3.Web3.soliditySha3([ "address", "uint16", "uint16", "uint8", "uint256", "address" ],
#                                             [ address, item_data['classId'], item_data['itemId'],
#                                                 item_data['tier'], nonce, contract_address ])
#     message = encode_defunct(hexstr=sig.hex())
#     signed_message = w3.eth.account.sign_message(message, os.environ.get('TESTNET_W3_WALLET_PRIV_KEY'))
#     signature = web3.Web3.toHex(signed_message.signature)
#     return signature, nonce

#contract method:
#function mint(string calldata title, uint16 issuerId, uint256 nonce, string memory uri, bytes calldata signature )
def create_mint_signature(title, issuerId, nonce, uri):
    print(CONTRACT_ADDRESS)
    sig = web3.Web3.solidity_keccak([ "string", "uint16", "uint256", "string", "address" ],
                                [ title, issuerId, nonce, uri, CONTRACT_ADDRESS])
    message = encode_defunct(hexstr=sig.hex())           
    signed_message = w3.eth.account.sign_message(message, SIGNER_WALLET_PRIV_KEY)
    signature = web3.Web3.to_hex(signed_message.signature)
    print(verify_message(message, signature, WALLET_PUB_ADDRESS))
    return signature

def create_test_signature(title):
    
    sig = web3.Web3.solidity_keccak([ "uint16", "address" ],
                                [ title, CONTRACT_ADDRESS])
    message = encode_defunct(hexstr=sig.hex())           
    signed_message = w3.eth.account.sign_message(message, SIGNER_WALLET_PRIV_KEY)
    signature = web3.Web3.to_hex(signed_message.signature)
    print(verify_message(message, signature, WALLET_PUB_ADDRESS))
    return signature

def verify_message(message, signature, address):
    return w3.eth.account.recover_message(message, signature=signature) == address