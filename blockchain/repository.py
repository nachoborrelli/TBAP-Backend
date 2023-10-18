import web3, json, os
from django_base.settings import CONTRACT_ADDRESS,BLOCKCHAIN_RPC_NETWORK, BASE_URL
from blockchain import utils
network = web3.Web3(web3.HTTPProvider(BLOCKCHAIN_RPC_NETWORK))
contract_abi = utils.get_contract_abi('assets/RewardToken.json')
contract = network.eth.contract(address=CONTRACT_ADDRESS, abi=contract_abi['abi'])

def execute_function(function_name, *args):
    """ 
        Executes a function on the blockchain and returns the result.
        @param function_name: name of the function to execute
        @param args: arguments to pass to the function
    """
    # return contract.functions[function_name](*args).call()
    try:
        return contract.functions[function_name](*args).call()
    except:
        raise Exception("Blockchain network not available.")
    
def get_reward_overview(tokenId):
    """Returns the reward overview for a given tokenId"""
    data = None
    try:
        data = execute_function("getRewardOverview",int(tokenId))
    except Exception as e:
        if e == "ERC721URIStorage: URI query for nonexistent token":
            pass
    return utils.blockchain_to_dict(data) if data else None    

def get_reward_overview_from_uri(user_token_id):
    """Returns the reward overview for a given user_token_id"""
    data = None
    try:
        data = execute_function("tokenOfURI",str(user_token_id))
        print("DATA:", data)
    except Exception as e:
        if e == "ERC721URIStorage: URI query for nonexistent token":
            pass
    if data:
        data = utils.blockchain_to_dict(data) 
        data['uri'] = create_uri_from_id(data['uri'])
    return data
                                    
def get_rewards_data_for_address(address):
    """Returns the rewards *RAW* data for a given address"""
    return execute_function("getUserRewards",address)
                                    
def get_parsed_rewards_data_for_address(address):
    """Returns the rewards *PARSED* data for a given address"""
    response = get_rewards_data_for_address(address)
    data= []
    if response:    
        data = list(map(utils.blockchain_to_dict, response))
    return data

def get_token_from_uri(uri):
    """Returns the token id from a given uri"""
    return int(uri.split('/')[-1])

def create_uri_from_id(id):
    return BASE_URL + "api/blockchain/uri/" + str(id)
# print(get_parsed_rewards_data_for_address("0xf1dD71895e49b1563693969de50898197cDF3481"))
# print(get_reward_overview(100))
print(get_reward_overview_from_uri('11'))