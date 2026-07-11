# Lesson 2: Data and Binary

## Bits and Bytes

Computers store all information as sequences of bits. A bit is the smallest unit of
data and has exactly two possible values: 0 or 1. A byte is a group of eight bits.
Because each bit doubles the number of possible patterns, one byte can represent 256
different values (2 to the power of 8). Larger units build on the byte: a kilobyte is
about a thousand bytes, a megabyte about a million, and a gigabyte about a billion.

## Binary Numbers

The binary number system is a base-2 positional system. Each digit position represents
a power of two, just as each position in the decimal system represents a power of ten.
For example, the binary number 1011 equals 8 + 0 + 2 + 1 = 11 in decimal. To convert a
decimal number to binary, repeatedly divide by two and record the remainders. Binary
suits computers because electronic circuits reliably distinguish two states, such as
high and low voltage.

## Hexadecimal

Hexadecimal is a base-16 system that uses digits 0-9 and letters A-F. One hexadecimal
digit represents exactly four bits, so two hexadecimal digits describe one byte. This
makes hexadecimal a compact, human-friendly way to write binary values. For example,
the byte 11111111 is FF in hexadecimal and 255 in decimal. Hexadecimal appears in
color codes, memory addresses, and error messages.

## Representing Text

Text is stored by assigning a number to every character. ASCII, standardized in 1963,
assigns numbers to 128 characters: English letters, digits, punctuation, and control
codes. The capital letter A is 65 in ASCII. Unicode extends this idea to cover more
than 140,000 characters from the world's writing systems, plus symbols and emoji.
UTF-8, the dominant encoding on the web, stores common characters in a single byte and
rarer characters in up to four bytes, and it is backward compatible with ASCII.

## Representing Images and Color

A digital image is a grid of pixels. Each pixel stores a color, most commonly as three
numbers for red, green, and blue intensity — the RGB color model. With one byte per
channel, each channel ranges from 0 to 255, giving about 16.7 million possible colors.
Image resolution is the number of pixels in the grid; higher resolution means more
detail and larger file sizes. Compression formats such as JPEG reduce file size by
discarding detail the human eye barely notices.

## File Sizes and Compression

File size follows directly from data representation: a 1000 by 1000 pixel image with
three bytes per pixel needs about three megabytes uncompressed. Compression reduces
storage and transmission cost. Lossless compression (such as ZIP) preserves the data
exactly, while lossy compression (such as JPEG or MP3) achieves much smaller files by
permanently discarding some information.
