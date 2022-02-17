class ReponseUtils:
    @staticmethod
    def button(title: str, payload: str=None, url: str=None, hide: bool=False):
        button = {
            'title': title,
            'hide': hide,
        }

        if payload is not None:
            button['payload'] = payload

        if url is not None:
            button['url'] = url

        return button
    
    @staticmethod
    def button_sber(title: str, action: str=None, actions: list=None):
        button = {
            'title': title,
        }

        if action is not None:
            button['action'] = action

        if actions is not None:
            button['actions'] = actions

        return button
