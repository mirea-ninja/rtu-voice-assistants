class ReponseUtils:
    @staticmethod
    def button(title, payload=None, url=None, hide=False):
        button = {
            'title': title,
            'hide': hide,
        }

        if payload is not None:
            button['payload'] = payload

        if url is not None:
            button['url'] = url

        return button
