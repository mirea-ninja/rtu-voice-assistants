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
    def button_sber(title: str, action: str=None):
        button = {
            'title': title,
        }

        if action is not None:
            button['actions'] = [
                {
                    "text": title,
                    "type": "text"
                }
            ]

        return button
