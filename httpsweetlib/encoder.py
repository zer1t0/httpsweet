from abc import ABC, abstractmethod
import base64


class EncoderFactory(object):
    """To create different encoders in function of the selecting encoding
    """

    @classmethod
    def create(cls, encoding):
        if "64" in str(encoding):
            return Base64Encoder()

        return EmptyEncoder()


class Encoder(ABC):
    """Interface to define the methods provide for an encoder"""

    @abstractmethod
    def encode(self, data):
        raise NotImplementedError()

    @abstractmethod
    def decode(self, data):
        raise NotImplementedError()


class EmptyEncoder(Encoder):
    """Encoder that do not perform any encoding function, for compatibility
    purposes.
    """

    def encode(self, data):
        return data

    def decode(self, data):
        return data


class Base64Encoder(Encoder):
    """Encoder that performs base64 encoding and decoding. Supports URL base64
    decoding.
    """

    def encode(self, data):
        """Encode binary data into base64, by using the regular dictionary"""
        return base64.b64encode(data)

    def decode(self, data):
        """Decode base64 data. Supports the regular dictionary as well as url
        base64.
        """
        data = self._normalize_url_data(data)
        return base64.b64decode(data)

    def _normalize_url_data(self, data):
        """Translate, if it is required, the url base64 dictionary, to the
        regular one.
        """

        missing_padding = len(data) % 4
        if missing_padding:
            data += b'=' * (4 - missing_padding)

        return data.replace(b"-", b"+").replace(b"/", b"-")
