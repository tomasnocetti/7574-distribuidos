SEPARATOR = '|'


class BaseMessage:
    def pack(self):
        return f'{self.CODE}'


class FileMessageStart(BaseMessage):
    def __init__(self) -> None:
        self.CODE = 'S'


class FileMessageEnd(BaseMessage):
    CODE = 'E'


class FileMessage():
    CODE = 'F'

    def __init__(self, file_name, file_content) -> None:
        self.file_name = file_name
        self.file_content = file_content

    def pack(self):
        return f'{self.CODE}{SEPARATOR}{self.file_name}{SEPARATOR}{self.file_content}'
