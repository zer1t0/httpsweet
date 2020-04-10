from abc import ABC, abstractmethod
import base64


class EncoderFactory(object):

    @classmethod
    def create(cls, encoding):
        if encoding == "64":
            return Base64Encoder()
        else:
            return EmptyEncoder()


class Encoder(ABC):

    @abstractmethod
    def encode(self, data):
        raise NotImplementedError()

    @abstractmethod
    def decode(self, data):
        raise NotImplementedError()


class EmptyEncoder(Encoder):

    def encode(self, data):
        return data

    def decode(self, data):
        return data


class Base64Encoder(Encoder):

    def encode(self, data):
        return base64.b64encode(data)

    def decode(self, data):
        data = self._normalize_url_data(data)
        return base64.b64decode(data)

    def _normalize_url_data(self, data):
        missing_padding = len(data) % 4
        if missing_padding:
            data += b'=' * (4 - missing_padding)

        return data.replace(b"-", b"+").replace(b"/", b"-")
