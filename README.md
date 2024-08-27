# jpeg-steg

## Introduction

With increasing privacy and security threats, hiding and exhanging information securely becomes a challenge. This repository contains Python scripts developed for embedding (hiding) secret files inside images compressed using the popular JPEG algorithm, mainly for the purpose of exploring and learning about steganographic algorithms for my university digital signal and image processing project. It consists of two scripts:

- ***dctsteg.py*** - contains image and file processing algorithms
- ***cli.py***  - a script for interactive application through terminal, inspired by how a popular tool called *StegHide* is used


## Steganography background

Any type of digital file can be read as a sequence of bits, ranging from a simple text file (message) to something like a compressed zip file. These bits can be embedded inside image data in different ways. For BMPs and PNGs (lossless image formats) it can be done simply by embedding these bits inside image pixel values. What the LSB (Least Signifant Bit) steganographic method suggests is to exploit the human eyes weakness to notice small changes (+ or - 1) inside pixel values. Main idea is to read pixel RGB values (numbers in range 0-255 representend by 8 bits in binary), substitute the LSB for a bit of file (or message) data and save it as a new pixel value. Simple as that, but unfortunately for JPEG compressed images (which are far more frequent in daily use) this won't work - beacuse anything embedded inside pixel values will get lost due to lossy recompression after saving the file. However, the LSB method can be applied in the image frequency domain (where images are processed like signals as well :)

Essential part of the JPEG compression is the Discrete Cosine Transform (DCT), where the lossy part occurs during quantization of these coefficients. **Embedding operation revolves around reading the image quantized DCT coefficients (after lossy compression), and substituting least significant bits from a (pseudo) random selection of these coefficients for a bit of secret file data - doing it in the image frequency domain!** By embedding DCT coefficients, secret file is scattered over a wider image area. However, there are two conditions for which ones to avoid modifying:

- coefficients having value 0 or 1
- the zero frequency coefficient ("solid color effect" in an image block)

Those conditions for selecting coefficients to embed data form the basis of "*JSteg*", a steganographic algorithm for JPEG compressed images. This implementation is a variant of JSteg, which uses pseudo random selection of coefficients for embedding (like *Outguess*, another steganographic algorithm for JPEGs), where a password is used to set the state of a pseudo random number generator (PRNG).

Youtube channel *Computerphile* has two great video which cover [the Discrete Cosine transform (DCT)](https://www.youtube.com/watch?v=Q2aEzeMDHMA) and [digital image steganography](https://www.youtube.com/watch?v=TWEXCYQKyDc) in greater detail.

## Prerequisites

The script doing the image processing job relies on having additional **numpy** and **jpeglib** python packages, both of which can be installed in a python environment using the **pip** command:

`pip install numpy jpeglib`

Other used modules should come preinstalled with Python (argparse, shutil, hashlib, random, sys).

## Use

The ***cli.py*** script is structured using argparse module, which makes it easy to get help for any task. The script runs with python, so to get information on what can it do, use the command:

`python cli.py -h` or `python cli.py --help`

which outputs three tasks:

- `check` to check cover image embedding capacity
- `embed` to embed secret file inside cover image
- `extract` to extract secret file from stego image

**Note:** it's best to use the script with required files in the same directory (folder), which saves terminal line space by not having to specify file paths

### Check embedding capacity

Used to display information about image embedding capacity and optionally to check wheter a file with given name can be embedded.

The following command can be used for getting help and information on which arguments it takes:

`python cli.py check -h`

**Note:** After task selection, user has the option to specify arguments using either short or long form (e.g. `--cover-image` compared to `--ci`)

An example of use would be for an image with name "*image.jpg*":

`python cli.py check --cover-image image.jpg`

**The output will be image embedding capacity in bytes.** Additonally, a secret file for embedding can be given as well to check if it can be done successfully. An example would be using a file named "*file.zip*":

`python cli.py check --cover-image image.jpg --secret-file file.zip`

The `check` task by default looks into the **Y** (luminance) color channel of an image, which has the highest embedding capacity. Other two are chrominance channels (**Cb** or **Cr**), which can be accessed using an aditional argument like `--channel Cb` or `--channel Cr`.

### Embedding

Used to actually embed a file inside an image. It is best to check before wheter it can be done successfully. To display information about which arguments `embed` task accepts use:

`python cli.py embed -h`

Embedding requires a cover image and a secret file. Output stego image name is set during use, for instance:

`python cli.py embed --secret-file file.zip --cover-image image.jpg --stego-image output.jpg`

The command will try to embed a secret file ("*file.zip*") into a cover image ("*image.jpg*") copy and name it "*output.jpg*". Before doing so it will prompt the user to set a password.

**Embedding can be done for files of any extension (.txt, .zip, .exe, ...). As long as the file can be embedded completely, it can be retrieved using the same password used for embedding.**

#### More details on what gets embedded

Secret file size is read in bytes, an integer which gets also embedded inside the image (as 3 bytes of data to store it - or 24 bits, which is more than enough to represent how much can be embedded). This way during the extraction of embedded file, it's size gets extracted first - based on which is possible to calculate how many iterations are needed to extract the file data (how many random coefficients have to be generated). File size is embedded over a choice of (pseudo) random coefficients, together with other bits of file content. This was a workaround in order to avoid choosing strings of characters used to indicate end of embedded data during the extraction process (which might work for a file of one format, but cause problems for extracting others)

### Extracting

To display information about which arguments `extract` task accepts, use:

`python cli.py extract -h`

Command output shows it uses a few arguments. A stego image containing an embedded file is required. User then specifies the output file for extraction, as well as the image color channel (if the default Y wasn't used). 

**In order to successfully extract and write a file, it is required to know embeded file extension as well as used password.** For example if a "*file.zip*" was embedded, something like "*extracted.zip*" can be used for specifying output file name.

`python cli.py extract --secret-file extracted.zip --stego-image stego.jpg`

After command execution, user will be prompted for a password used for embedding. If the operation is successful, secret file will be extracted completely with a given name.
