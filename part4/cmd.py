import argparse


def main():
    parser = argparse.ArgumentParser(description="RPA命令行交互程序")

    parser.add_argument("-i", "--input", help="输入扫描目录，必需", required=True)
    parser.add_argument("-o", "--output", help="输出结果目录，非必需，默认为当前目录output文件夹")
    parser.add_argument("-ocr", "--ocr", type=str, help="ocr的url，非必需，默认为集团ocr地址")

    args = parser.parse_args()

    if args.verbose:
        print(f"将文件 {args.input_file} 复制到 {args.output_file}")

    with open(args.input_file, "r") as input_file, open(args.output_file, "w") as output_file:
        output_file.write(input_file.read())

    print("复制完成！")


main()