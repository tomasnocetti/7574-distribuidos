import json
import ast

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
    def __init__(self, code, client_id, message_id=''):
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

    @classmethod
    def decode(cls, buffer):
        base, buffer = super().decode(buffer)

        return MessageEnd(base.client_id, base.message_id)


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
        file_name, file_content = next_packed_element(buffer)
        # file_content, buffer = next_packed_element(buffer)

        return FileMessage(base.client_id, base.message_id, file_name, file_content)


class VideoMessage(BaseMessage):
    def __init__(self, client_id, message_id, content: dict) -> None:
        super().__init__(MESSAGE_VIDEO, client_id, message_id)

        self.content = content

    def pack(self) -> str:
        return f'{super().pack()}{SEPARATOR}{json.dumps(self.content)}'

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_VIDEO

    @classmethod
    def decode(cls, buffer: str):
        base, json_content = super().decode(buffer)

        return VideoMessage(base.client_id, base.message_id, json.loads(json_content))


class BaseResult(BaseMessage):
    def __init__(self, code, client_id, message_id,  content) -> None:
        super().__init__(code, client_id, message_id)
        self.content = content

    def pack(self) -> str:
        return f'{super().pack()}{SEPARATOR}{self.content}'


class CategoryMessage(BaseResult):
    def __init__(self, client_id, content) -> None:
        super().__init__(MESSAGE_CATEGORY_COUNT, client_id, '', content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == MESSAGE_CATEGORY_COUNT

    @classmethod
    def decode(cls, buffer: str):
        base, content = super().decode(buffer)

        return CategoryMessage(base.client_id, content)


class Result1(BaseResult):
    def __init__(self, client_id, message_id, content) -> None:
        super().__init__(RESULT_1, client_id, message_id, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_1

    @classmethod
    def decode(cls, buffer: str):
        base, content = super().decode(buffer)

        return Result1(base.client_id, base.message_id, content)


class BinaryFile():
    def __init__(self, file_name, file_content):
        self.file_name = file_name
        self.file_content = file_content

    def pack(self):
        length = len(self.file_content)
        return f'{self.file_name}{SEPARATOR}{length}{SEPARATOR}{self.file_content}'

    @classmethod
    def decode(self, buffer):
        file_name, buffer = next_packed_element(buffer)
        file_length, file_content = next_packed_element(buffer)

        parsed_content = ast.literal_eval(file_content)

        assert (len(parsed_content) == int(file_length))

        return BinaryFile(file_name, parsed_content)


class Result2(BaseResult):
    def __init__(self, client_id, message_id, content: str) -> None:
        super().__init__(RESULT_2, client_id, message_id, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_2

    @classmethod
    def decode(cls, buffer):
        base, content = super().decode(buffer)

        return Result2(base.client_id, base.message_id, content)


class Result3(BaseResult):
    def __init__(self, client_id, message_id, content) -> None:
        super().__init__(RESULT_3, client_id, message_id, content)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == RESULT_3

    @classmethod
    def decode(cls, buffer: str):
        base, content = super().decode(buffer)

        return Result3(base.client_id, base.message_id, content)


class EndResult1(BaseMessage):
    def __init__(self, client_id, message_id) -> None:
        super().__init__(END_RESULT_1, client_id, message_id)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == END_RESULT_1


class EndResult2(BaseMessage):
    def __init__(self, client_id, message_id) -> None:
        super().__init__(END_RESULT_2, client_id, message_id)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == END_RESULT_2


class EndResult3(BaseMessage):
    def __init__(self, client_id, message_id) -> None:
        super().__init__(END_RESULT_3, client_id, message_id)

    @staticmethod
    def is_message(buffer) -> bool:
        return buffer[0] == END_RESULT_3
