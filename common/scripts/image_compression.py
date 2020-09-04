import os
import argparse
from PIL import Image

FILE_EXTENSIONS = {'JPEG': ('.jpg', '.jpeg')}


def main(args):
    print('Launch compression script')
    for path, dirs, files in os.walk(args.work_dir):
        for f in files:
            for extension in FILE_EXTENSIONS:
                if f.lower().endswith(FILE_EXTENSIONS[extension]):
                    image_path = os.path.join(path, f)
                    image = Image.open(image_path)
                    image.save(image_path, extension, quality=args.quality)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work_dir', required=False, default='../../../Work')
    parser.add_argument('--quality', required=False, default=75)
    args = parser.parse_args()

    args.work_dir = os.path.realpath(
        os.path.join(__file__, os.path.pardir, args.work_dir))

    main(args)
