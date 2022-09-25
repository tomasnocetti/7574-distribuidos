SEPARATOR = '|'

MESSAGE_START = 'S'
MESSAGE_END = 'E'
MESSAGE_FILE = 'F'


class BaseMessage:
    def pack(self):
        return f'{self.CODE}'


class FileMessageStart(BaseMessage):
    def __init__(self) -> None:
        self.CODE = MESSAGE_START

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_START


class FileMessageEnd(BaseMessage):
    def __init__(self) -> None:
        self.CODE = MESSAGE_END

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_END


class FileMessage():

    def __init__(self, file_name, file_content) -> None:
        self.CODE = MESSAGE_FILE
        self.file_name = file_name
        self.file_content = file_content

    def pack(self):
        return f'{self.CODE}{SEPARATOR}{self.file_name}{SEPARATOR}{self.file_content}'

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_FILE

    @classmethod
    def decode(cls, buffer: str):
        content = buffer[2:]
        index = content.find(SEPARATOR)

        return FileMessage(content[:index], content[index+1:])


class VideoMessage():
    def __init__(self, content) -> None:
        pass
