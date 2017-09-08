import subprocess
import sys

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) != 1:
        print('Unexpected number of arguments. Release name is expected.')

    release_name = args[0]
    process = subprocess.Popen(['git', 'tag', release_name],
                               stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['git', 'push', 'origin', release_name],
                               stdout=subprocess.PIPE)
    output = process.communicate()[0]
    process = subprocess.Popen(['git', 'push', 'origin', 'master'],
                               stdout=subprocess.PIPE)
    output = process.communicate()[0]
