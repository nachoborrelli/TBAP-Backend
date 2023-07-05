import web3, json, os
from django_base.settings import CONTRACT_ADDRESS,BLOCKCHAIN_RPC_NETWORK
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
    try:
        return contract.functions[function_name](*args).call()
    except:
        raise Exception("Blockchain network not available.")
    
def get_reward_overview(tokenId):
    """Returns the reward overview for a given tokenId"""
    return utils.blockchain_to_dict(execute_function("getRewardOverview",int(tokenId)))
                                    
def get_rewards_data_for_address(address):
    """Returns the rewards *RAW* data for a given address"""
    return execute_function("getUserRewards",address)
                                    
def get_parsed_rewards_data_for_address(address):
    """Returns the rewards *PARSED* data for a given address"""
    response = get_rewards_data_for_address(address)
    data= []
    if response:    
        for i in range(len(response[0])):
            data.append({
                        "tokenId": response[0][i],
                        "tokenData" : utils.blockchain_to_dict(response[1][i]),
                        })
    return data

