def register():
    class SpeechPlugin:
        def before_reply(self, text):
            return text

        def after_reply(self, text):
            return text

    return SpeechPlugin()
