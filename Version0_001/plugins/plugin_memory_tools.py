def register():
    class MemoryTools:
        def before_reply(self, text):
            return text
    return MemoryTools()
