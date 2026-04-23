from vk_api import VkApi


def form_api_dict(groups_info: list[list[int, str]]) -> dict[int, VkApi]:
    api_dict = dict()

    for info in groups_info:
        api_dict[info[0]] = VkApi(token=info[1])
    
    return api_dict

def get_user_info(groups_api: dict, event) -> dict:
    user_id = event.obj.message["from_id"]

    parametrs = {
        "user_ids": user_id, 
        "fields": "first_name,last_name"
    }

    user_names = groups_api[event.group_id].method("users.get", parametrs)

    return {
        "user_id": user_id,
        "first_name": user_names[0].get("first_name"),
        "last_name": user_names[0].get("last_name")
    }