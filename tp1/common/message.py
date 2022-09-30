import json


SEPARATOR = '|'

MESSAGE_START = 'S'
MESSAGE_END = 'E'
MESSAGE_FILE = 'F'
MESSAGE_VIDEO = 'V'

END_RESULT_1 = 'A'
END_RESULT_2 = 'B'
END_RESULT_3 = 'C'
RESULT_1 = '1'
RESULT_2 = '2'
RESULT_3 = '3'


class BaseMessage:
    def pack(self):
        return f'{self.CODE}'


class MessageStart(BaseMessage):
    def __init__(self) -> None:
        self.CODE = MESSAGE_START

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_START


class MessageEnd(BaseMessage):
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
    def __init__(self, content: dict) -> None:
        self.CODE = MESSAGE_VIDEO
        self.content = content

    def pack(self) -> str:
        return f'{self.CODE}{SEPARATOR}{json.dumps(self.content)}'

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_VIDEO

    @classmethod
    def decode(cls, buffer: str):
        content = buffer[2:]

        return VideoMessage(json.loads(content))


class BaseResult:
    def __init__(self, code, content) -> None:
        self.code = code
        self.content = content

    def pack(self) -> str:
        return f'{self.code}{SEPARATOR}{self.content}'


class Result1(BaseResult):
    def __init__(self, content) -> None:
        super().__init__(RESULT_1, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_1

    @classmethod
    def decode(cls, buffer: str):
        content = buffer[2:]

        return Result1(content)


class Result2(BaseResult):
    def __init__(self, content) -> None:
        super().__init__(RESULT_2, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_2

    @classmethod
    def decode(cls, buffer: str):
        content = buffer[2:]

        return Result2(content)


class Result3(BaseResult):
    def __init__(self, content) -> None:
        super().__init__(RESULT_3, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_3

    @classmethod
    def decode(cls, buffer: str):
        content = buffer[2:]

        return Result3(content)


class EndResult1(BaseMessage):
    def __init__(self) -> None:
        super().__init__()
        self.CODE = END_RESULT_1

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == END_RESULT_1


class EndResult2(BaseMessage):
    def __init__(self) -> None:
        super().__init__()
        self.CODE = END_RESULT_2

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == END_RESULT_2


class EndResult3(BaseMessage):
    def __init__(self) -> None:
        super().__init__()
        self.CODE = END_RESULT_3

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == END_RESULT_3
