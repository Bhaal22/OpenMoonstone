from struct import iter_unpack, unpack

from attr import attrib, attrs

from extract import each_bit_in_byte, extract_file


def sum_bits(bits, bit_mask=0):
    '''Calculate byte from bit values and bit positions

    args:
        bits (list of bool): binary values for each position.
        bit_mask (int): values of bits we want to sum

    returns (int/byte): byte value
    '''

    original_byte = sum(bit << x for x, bit in enumerate(bits))
    return original_byte & bit_mask


def sum_bits_duplicates(bits, duplicate_position=4, bit_mask=None):
    '''Calculate byte from bit values and bit positions

    args:
        bit_mask (list of ints): each int represents the position of its
            respective bit value in bits. e.g [3, 4] indicates the first and
            second element of bits should be shifted to the third and forth
            positon of the final byte output.
        bits (list of bool): binary values for each position.
        duplicate_position (int): The bit in duplicate position is the ORed
            value of all of bit positions. e.g bit_mask=[0, 1],
            duplicate_position=4 indicates that bit 4 in the final byte should
            be bit 0 | bit 1 of the final byte.

    returns (int/byte): byte value
    '''
    if bit_mask is None:
        bit_mask = [0, 1]

    total = sum(
        bit << bit_mask[bit_pos] for bit_pos, bit in enumerate(bits)
    )
    duplicate = any(bits) << duplicate_position
    total += duplicate
    return total


def valid_blit_type(instance, attribute, blit_type):
    if not 0 <= blit_type <= 32:
        raise ValueError('{} is not a valid blit type'.format(blit_type))


@attrs
class ImageHeader(object):
    padding = attrib()
    data_address = attrib()
    width = attrib()
    height = attrib()
    x_adjust = attrib()
    blit_type = attrib(validator=valid_blit_type)


class SpriteSheetFile(object):
    def __init__(self, file_data):
        self.image_count = unpack('>H', file_data[0:2])[0]
        self.header_length = self.image_count * 10 + 10

        self.file_length = unpack('>H', file_data[4:6])[0]
        self.file_data = file_data[self.header_length:]

        header_data = file_data[10:self.header_length]
        self.headers = [ImageHeader(*xs)
                        for xs in iter_unpack('>4H2B', header_data)]

        self.extracted = extract_file(self.file_length, self.file_data)

        self.images = []

    def get_image(self, image_number):
        header = self.headers[image_number]
        image_data_location = header.data_address + self.header_length
        image_width = header.width + 0xf
        packed_image_width = image_width // 16 * 2

        packed_image_length = packed_image_width * header.height
        bit_planes = [image_data_location + (packed_image_length * i)
                      for i in range(0, 5)]

        pixels = self.recombine_bit_planes(header.blit_type, bit_planes,
                                           packed_image_length)
        return header, pixels

    def recombine_bit_planes(self, blit_type, bit_plane_positions, length):
        output = [None] * (length * 8)
        o = len(output)

        if blit_type == 32:
            bit_length = 2
            sum_function = sum_bits_duplicates
        else:
            bit_length = blit_type.bit_length()
            sum_function = sum_bits

        bit_planes = []
        for position in bit_plane_positions[0:bit_length]:
            pos = position - self.header_length
            bit_planes.append(self.extracted[pos:pos + length])

        # get the nth byte of every bit_plane
        for i, bytes_list in enumerate(zip(*bit_planes)):
            # get the nth set of bits of those bytes
            as_bits = [each_bit_in_byte(byte) for byte in bytes_list]

            for j, bits in enumerate(zip(*as_bits)):
                # reconstruct the output byte from those bits
                output[i * 8 + j] = sum_function(bits=bits, bit_mask=blit_type)

        assert o == len(output)
        return output
