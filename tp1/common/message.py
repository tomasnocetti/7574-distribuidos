import json


SEPARATOR = '|'

MESSAGE_START = 'S'
MESSAGE_END = 'E'
MESSAGE_FILE = 'F'
MESSAGE_VIDEO = 'V'
MESSAGE_CATEGORY_COUNT = 'C'

END_RESULT_1 = 'A'
END_RESULT_2 = 'B'
END_RESULT_3 = 'C'
RESULT_1 = '1'
RESULT_2 = '2'
RESULT_3 = '3'

'''
    Returns the first element that matches the separator and the rest of the buffer
'''


def next_packed_element(buffer):
    index = buffer.find(SEPARATOR)
    if (index == -1):
        return buffer, None

    return buffer[:index], buffer[index + 1:]


class BaseMessage:
    def __init__(self, code, client_id, message_id):
        self.code = code
        self.client_id = client_id
        self.message_id = message_id

    def pack(self):
        return f'{self.code}{SEPARATOR}{self.client_id}{SEPARATOR}{self.message_id}'

    @staticmethod
    def decode(buffer):
        code, buffer = next_packed_element(buffer)

        client_id, buffer = next_packed_element(buffer)

        message_id, buffer = next_packed_element(buffer)

        return BaseMessage(code, client_id, message_id), buffer


class MessageEnd(BaseMessage):
    def __init__(self, client_id, message_id) -> None:
        super().__init__(MESSAGE_END, client_id, message_id)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_END


class FileMessage(BaseMessage):

    def __init__(self, client_id, message_id, file_name, file_content) -> None:
        super().__init__(MESSAGE_FILE, client_id, message_id)

        self.file_name = file_name
        self.file_content = file_content

    def pack(self):
        return f'{super().pack()}{SEPARATOR}{self.file_name}{SEPARATOR}{self.file_content}'

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_FILE

    @classmethod
    def decode(cls, buffer: str):
        base, buffer = super().decode(buffer)
        file_name, buffer = next_packed_element(buffer)
        file_content, buffer = next_packed_element(buffer)

        return FileMessage(base.client_id, base.message_id, file_name, file_content)


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


class CategoryMessage(BaseResult):
    def __init__(self, content) -> None:
        super().__init__(MESSAGE_CATEGORY_COUNT, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_CATEGORY_COUNT

    @classmethod
    def decode(cls, buffer: str):
        content = buffer[2:]

        return CategoryMessage(content)


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
    def __init__(self, file_name, content) -> None:
        super().__init__(RESULT_2, content)
        self.file_name = file_name

    def pack(self) -> str:
        length = len(self.content)
        return f'{self.code}{SEPARATOR}{self.file_name}{SEPARATOR}{length}{SEPARATOR}{self.content}'

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_2

    @classmethod
    def decode(cls, buffer):
        content = buffer[2:]
        index = content.find(SEPARATOR)
        file_name = content[:index]
        content = content[index+1:]
        length_separator = content.find(SEPARATOR)
        length = int(content[:length_separator])
        content = content[length_separator+1:]

        return Result2(file_name, content)


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
