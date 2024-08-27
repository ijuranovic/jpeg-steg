import os.path
import shutil
import jpeglib
import hashlib
import random
import sys
import numpy as np


"""
The following functions are defined and used as methods for SecretFile class

SecretFile class is defined for file manipulation in steganographic purposes
Main features and abilities are:
    * to read secret file (by path or name) contents in a form of byte array
    * to convert file size and content bytes to a sequence of embedding bits
    * to write file content from extracted bits
"""


# Convert a string of bits to a byte array
def to_byte_arr(bits_str):
    byte_list = [int(bits_str[i:i+8], 2) for i in range(0, len(bits_str), 8)]
    return bytearray(byte_list)


# Convert a byte array to a string of bits
def to_bits_str(byte_arr):
    return ''.join(f'{b:08b}' for b in byte_arr)


# Read file and return byte contents
def read_file(self):
    with open(self.name, 'rb') as f:
        return bytearray(f.read())


# Save file with extracted content (extracted_bits)
def save_file(self):
    self.content = to_byte_arr(self.extracted_bits)
    with open(self.name, "wb") as f:
        f.write(self.content)


# Embedding bits for hiding: file size info and content data bytes
def get_embedding_bits(self):
    # 3 bytes to store secret file size information - up to 16 MBs
    file_size = (len(self.content)).to_bytes(3, byteorder='big')

    return to_bits_str(file_size + self.content)


class SecretFile:

    # Initialize SecretFile object
    def __init__(self, file_name):
        self.name = file_name

        # Read a file for embedding
        if os.path.isfile(self.name):
            self.content = read_file(self)
            self.embedding_bits = get_embedding_bits(self)
        # Initialize for extraction
        else:
            self.content = bytearray()
            self.extracted_bits = ''

    # Save file with extracted byte content
    save = save_file


"""
The following functions are defined and used as methods for StegoImage class

StegoImage class is defined for image manipulation with steganographic tasks
Main features and abilities are to:
    * initialize object for a non existing stego image (before embedding)
        - creates a cover image copy with equal image DCT values
    * initialize object for an existing stego image (for file extraction)
    * embed image values with file bits and save modified values to an image
"""


# Get embeddable DCT coefficient positions
def get_embeddable_positions(coefficients):

    # Array of DCT coefficient positions
    positions = np.arange(coefficients.size)

    # Every 64th occurance is a DC coefficient position
    # Boolean mask with removed DC coefficient positions
    mask_pos = positions % 64 != 0
    # Boolean mask with removed 1 and 0 value positions
    mask_val = (coefficients != 0) & (coefficients != 1)

    # Boolean mask with all conditions met, True if:
    # coefficient at position is not a DC coefficent
    # coefficient value is not equal to 0 or 1
    mask_all = mask_pos & mask_val

    # Return array with possible embedding positions
    return positions[mask_all]


# Get a given number of random array indices
def get_rand_indices(array, number, password):

    # Use a password to set PRNG seed value
    seed = hashlib.sha256(password.encode()).hexdigest()
    random.seed(seed)

    return random.sample(range(array.size), number)


# Embed bits of file data in DCT coefficient LSB values
def embed_bits(self, embedding_bits, password, channel):

    # DCT coefficients for selected YCbCr color channel
    cfs = getattr(self.dct, channel)

    # Get embeddable positions from flat coefficients array
    flat_cfs = cfs.flatten()
    flat_pos = get_embeddable_positions(flat_cfs)

    # Number of DCT coefficients for embedding
    n_cfs = len(embedding_bits)

    if n_cfs > flat_pos.size:
        print("file is to large for embedding...")
        sys.exit(0)

    # Get random indices for embeddable positions array
    rand_idxs = get_rand_indices(flat_pos, n_cfs, password)
    embed_pos = flat_pos[rand_idxs]

    for n in range(len(embed_pos)):
        bit = int(embedding_bits[n])
        pos = embed_pos[n]
        val = flat_cfs[pos]
        # Embed LSB and overwrite with modified value
        flat_cfs[pos] = (val & ~1) | bit

    # Reshapes a DCT component array to original size
    cfs = flat_cfs.reshape(np.shape(cfs))
    # Update image DCT component with modified values
    setattr(self.dct, channel, cfs)
   

# Extract bits of file data from DCT coefficient LSB values
def extract_bits(self, password, channel):

    # DCT coefficients for selected YCbCr color channel
    cfs = getattr(self.dct, channel)

    # Get embeddable positions from flat coefficients array
    flat_cfs = cfs.flatten()
    flat_pos = get_embeddable_positions(flat_cfs)

    # First 24 positions embedded with file size number
    rand_idxs = get_rand_indices(flat_pos, 24, password)
    embed_pos = flat_pos[rand_idxs]
    
    f_size = []
    for pos in embed_pos:
        val = flat_cfs[pos]
        bit = val & 1
        f_size.append(str(bit))

    # Convert extracted f_size bits to an integer
    f_size = int("".join(f_size), 2)
    # Total number of embedded DCT coefficients
    n_cfs = 24 + f_size * 8

    # Exit if impossible file size gets extracted
    if n_cfs > flat_pos.size:
        print("possible wrong password or image")
        print("failed to extract")
        sys.exit(0)
 
    # Get all embedded DCT coefficient array positions
    rand_idxs = get_rand_indices(flat_pos, n_cfs, password)
    embed_pos = flat_pos[rand_idxs]
    
    # Extracting embedded file content data bits
    f_data = []
    for pos in embed_pos[24:]:
        val = flat_cfs[pos]
        # Get coefficient LSB and append to list
        bit = val & 1
        f_data.append(str(bit))
    
    return "".join(f_data)
    

class StegoImage:

    # Cover image name is by default an empty string
    # If provided it will be used for initialization
    def __init__(self, stego_image, cover_image=''):
        self.name = stego_image

        # Read quantized DCT if stego image exists
        if os.path.isfile(self.name):
            self.dct = jpeglib.read_dct(self.name)
        # Create initial stego image as cover copy
        else:
            shutil.copy(cover_image, self.name)
            self.dct = jpeglib.read_dct(self.name)

    # Predefined functions used as methods for class
    embed = embed_bits
    extract = extract_bits

    # Method returns stego image embedding capacity in bytes
    def capacity(self, channel):

         # DCT coefficients for selected YCbCr color channel
        cfs = getattr(self.dct, channel)
        # Flatten coefficients, get embedding positions array
        flat_cfs = cfs.flatten()
        flat_pos = get_embeddable_positions(flat_cfs)

        return flat_pos.size // 8

    # Write modified stego DCT values to stego image
    def write(self):
        self.dct.write_dct(self.name)
