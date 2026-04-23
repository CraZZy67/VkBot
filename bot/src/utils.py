from vk_api import VkApi

def form_api_dict(groups_info: list[list[int, str]]) -> dict[int, VkApi]:
    api_dict = dict()

    for info in groups_info:
        api_dict[info[0]] = VkApi(token=info[1])
    
    return api_dict
    