import web3, json, os
from web3.auto import w3
from eth_account import Account
from eth_account.messages import encode_defunct
from django_base.settings import CONTRACT_ADDRESS, SIGNER_WALLET_PRIV_KEY
# WALLET_PUB_ADDRESS="0x7db0FAD6B9e2fB362bAD6fB43F1e3aDd48F744D5"

def get_contract_abi(rel_path):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, rel_path)
    file = open(abs_file_path, "r")
    abi=json.load(file)
    return abi

def is_valid_address(address):
    return web3.Web3.isAddress(address)

#------------DATA PARSING METHODS----------------
def blockchain_to_dict(elem):
    return {
            'title' : elem[0],
            'issuerId' : elem[1],
            'createdAt' : elem[2]
            }

#------------SIGNATURE METHODS----------------
def get_address_from_signature(signature, message = None):
    if message == None:
        message = "Welcome to TBAP!\n\nThis is just a signed message to verify your identity.\n\nThis request will not trigger a blockchain transaction or cost any gas fees."
    message = encode_defunct(text=message)
    verification = Account.recover_message(message,signature=signature)
    return verification

def create_mint_signature(title, issuerId, nonce, uri):
    """ 
    Signature fo contract method:
        function mint(string calldata title, uint16 issuerId, uint256 nonce, string memory uri, bytes calldata signature )
    """
    sig = web3.Web3.solidity_keccak([ "string", "uint16", "uint256", "string", "address" ],
                                [ title, issuerId, nonce, uri, CONTRACT_ADDRESS])
    message = encode_defunct(sig)
    signed_message = w3.eth.account.sign_message(message, SIGNER_WALLET_PRIV_KEY)
    signature = web3.Web3.to_hex(signed_message.signature)
    print(signature)
    # print(verify_message(message, signature, WALLET_PUB_ADDRESS))
    return signature

def verify_message(message, signature, address):
    return w3.eth.account.recover_message(message, signature=signature) == address


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

# example hardhat js method
# function signMintData(tokenData){
#     const account = getSignerAccount();
#     const message = ethers.utils.solidityKeccak256(
#         [ "string", "uint16", "uint256", "string", "address" ], 
#         [ tokenData.title, tokenData.issuerId, tokenData.nonce, tokenData.uri, getEnvVariable("NFT_CONTRACT_ADDRESS") ]);
#     return account.signMessage(ethers.utils.arrayify(message));
# }