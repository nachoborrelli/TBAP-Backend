import web3, json, os
from web3.auto import w3
from eth_account import Account
from eth_account.messages import encode_defunct
from django_base.settings import CONTRACT_ADDRESS, SIGNER_WALLET_PRIV_KEY
from blockchain.models import Signature
# WALLET_PUB_ADDRESS="0x7db0FAD6B9e2fB362bAD6fB43F1e3aDd48F744D5"

def get_contract_abi(rel_path):
    script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
    abs_file_path = os.path.join(script_dir, rel_path)
    file = open(abs_file_path, "r")
    abi=json.load(file)
    return abi

def is_valid_address(address):
    return web3.Web3.is_address(address)

#------------DATA PARSING METHODS----------------
def blockchain_to_dict(elem):
    print(elem)
    return {
            'title' : elem[0],
            'issuerId' : elem[1],
            'createdAt' : elem[2],
            'uri' : elem[3]
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
    # print(verify_message(message, signature, WALLET_PUB_ADDRESS))
    return signature

def verify_message(message, signature, address):
    return w3.eth.account.recover_message(message, signature=signature) == address


def get_new_nonce():
    last_nonce = Signature.objects.last().nonce if Signature.objects.last() else 0
    return last_nonce + 1

def get_id_from_uri(uri):
    return int(uri.split('/')[-1])

def update_user_tokens_and_signatures_in_db(user):
    from blockchain.models import UserToken, Signature
    from blockchain.repository import get_parsed_rewards_data_for_address

    blockchain_data = get_parsed_rewards_data_for_address(user.user_profile.wallet_address)
    for blockchain_token in blockchain_data:
        print(blockchain_token)
        user_token_id= get_id_from_uri(blockchain_token['uri'])
        user_token = UserToken.objects.get(id=user_token_id)
        if user_token:
            user_token.tokenId = blockchain_token['tokenId']
            user_token.is_claimed = True
            user_token.save()
        signature = Signature.objects.get(user=user, uri=user_token_id)
        if signature:
            signature.was_used = True
            signature.save()
