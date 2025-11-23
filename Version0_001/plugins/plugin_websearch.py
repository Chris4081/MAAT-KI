def register():
    class WebPlugin:
        def before_reply(self, text):
            return text
    return WebPlugin()

