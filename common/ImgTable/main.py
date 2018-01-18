import jinja2
import os
import argparse
import hashlib

def create_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', required=False)

    return parser

def main():
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('main', 'templates'),
        autoescape=jinja2.select_autoescape(['html'])
    )
    template = env.get_template('index.html')
    args = create_argparser().parse_args()
    

    folders = []
    files_hash = {}
    files_list = {}

    for baseline in os.listdir(args.input_path):
        baseline_path = os.path.join(args.input_path, baseline)
        if os.path.isdir(baseline_path):
            folders.append(baseline)
    
            for path, dirs, files in os.walk(baseline_path):
                for file in files:
                    if not file in files_list:
                        files_list.update({file: 'init'})

                    files_hash.update({
                        baseline + file:
                        hashlib.md5( open(os.path.join(path,file), 'rb').read() ).hexdigest()
                    })

    first = next(iter(files_list))
    for baseline in os.listdir(args.input_path):
        if os.path.isdir(os.path.join(args.input_path, baseline)):
            for file in files_list:
                if files_hash[baseline + file] != files_hash[baseline + first]:
                    files_list.update({ file: 'NOT EQUALS' })

    html_result = template.render(title='Baselines compare', files_hash=files_hash, folders=folders, files_list=files_list)

    with open(os.path.join(args.input_path, 'compare.html'), 'w') as html_file:
        html_file.write(html_result)


if __name__ == '__main__':
    main()
