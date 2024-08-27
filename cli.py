from dctsteg import *
import argparse


def main():

    parser = argparse.ArgumentParser(description="Steganographic application CLI for use with JPEG compressed images")
    subparsers = parser.add_subparsers(dest="task")

    # Check task parser                        
    check = subparsers.add_parser('check', help='check cover image embedding capacity')
    check.add_argument('-sf', '--secret-file', type=str, help='input secret file name')
    check.add_argument('-ci', '--cover-image', type=str, help='input cover image name', required=True)
    check.add_argument('--channel', type=str, default="Y", help='set YCbCr color channel for use')
    
    # Embed task parser
    embed = subparsers.add_parser('embed', help='embed secret file inside cover image')
    embed.add_argument('-sf', '--secret-file', type=str, help='input secret file name', required=True)
    embed.add_argument('-ci', '--cover-image', type=str, help='input cover image name', required=True)
    embed.add_argument('-si', '--stego-image', type=str, help='output stego image name', required=True)
    embed.add_argument('--channel', type=str, default="Y", help='set YCbCr color channel for use')

    # Extract task parser
    extract = subparsers.add_parser('extract', help='extract secret file from stego image')
    extract.add_argument('-si', '--stego-image', type=str, help='input stego image name', required=True)
    extract.add_argument('-sf', '--secret-file', type=str, help='output secret file name', required=True)
    extract.add_argument('--channel', type=str, default="Y", help='set YCbCr color channel for use')

    args = parser.parse_args()

    if args.task == 'embed':

        # Initialize the secret file object
        file = SecretFile(args.secret_file)
        # Initialize stego image from cover image values
        stego = StegoImage(args.stego_image, args.cover_image)

        password = input("password: ").strip()
        stego.embed(file.embedding_bits, password, args.channel)
        stego.write()

    elif args.task == 'extract':

        # Initialize the secret file object
        file = SecretFile(args.secret_file)
        # Initialize an existing stego image
        stego = StegoImage(args.stego_image)

        password = input("password: ").strip()

        # Extract bits and assign them to secret file
        file.extracted_bits = stego.extract(password, args.channel)
        file.save()

    elif args.task == 'check':
        
        cover = StegoImage(args.cover_image) 
        count = cover.capacity(args.channel) # Capacity in bytes

        if args.secret_file is not None:
            file_size = os.path.getsize(args.secret_file)
            print(f"file can be embedded: {file_size + 3 < count}")
            
            file_size = "{:,}".format(file_size)
            print(f"input file size: {file_size.rjust(10)} B")

        count = "{:,}".format(count)
        print(f"cover hide size: {count.rjust(10)} B")
        
    else:
        parser.print_help()

main()
