from dataclasses import dataclass
from datetime import datetime
from glob import glob
from os import getcwd, listdir
from os.path import getctime, exists
from pathlib import Path
from shutil import make_archive, unpack_archive
from sys import argv

from configargparse import ArgumentParser, Namespace
from send2trash import send2trash

BACKUP_FORMAT = '%Y-%m-%d-%H-%M'
FILE_EXIST = 'InGameMap.ini'
GAME_FILES = Path.home() / 'Zomboid'
GAME_MODES = {
    'a': 'Apocalypse',
    's': 'Survivor',
    'b': 'Builder',
    'c': 'Sandbox'
}
PATH_ERROR = 'Invalid path for save. Please either specify (-t -n) or enter folder (cd)'


def present(name: str) -> bool:
    return type(name) is str and name != ''


def get_args() -> tuple[ArgumentParser, Namespace]:
    """
    Set up an ArgumentParser and use it on sys.argv

    :return: Parsed args
    """

    parser = ArgumentParser(description='Manage backups for Project Zomboid')
    parser.add_argument('-t', '--type', choices=GAME_MODES.keys(), default=list(GAME_MODES.keys())[-1],
                        help='Type of save game, required unless ran from within save type folder')
    parser.add_argument('-n', '--name', default='',
                        help='Name of save game, required unless ran from within save game folder')
    cmd = parser.add_mutually_exclusive_group()
    cmd.add_argument('-b', '--backup', nargs='?', const=True,
                     help='Save a backup, default name is the current date-time')
    cmd.add_argument('-r', '--restore', nargs='?', const=True,
                     help='Restore from a backup, default is the most recent')
    cmd.add_argument('-l', '--list', nargs='?', const=5, type=int,
                     help='List available backups, default is 5 (-1=all)')
    cmd.add_argument('-c', '--clean', nargs='?', const=1, type=int,
                     help='Clean up oldest backups, default is 1')
    return parser, parser.parse_args(argv[1:])


@dataclass
class Save:
    type: str
    name: str

    @classmethod
    def from_cwd(cls) -> "Save":
        """
        Raises `ValueError` if not in a directory relative to game files
        :return: Derive from current working directory
        """
        cwd = Path(getcwd())
        if cwd.is_relative_to(GAME_FILES) and exists(cwd / FILE_EXIST):
            return Save(*cwd.parts[-2:])
        raise ValueError(PATH_ERROR)

    def __repr__(self) -> str:
        return f'{self.type}, {self.name}'

    @property
    def backups(self) -> Path:
        return GAME_FILES / 'backups' / self.type / self.name

    @property
    def dir(self) -> Path:
        return GAME_FILES / 'saves' / self.type / self.name

    def backup(self, name: str):
        zip_name = name if present(name) else datetime.now().strftime(BACKUP_FORMAT)
        zip_path = self.backups / zip_name
        print(f'Creating backup: {zip_name} for {self}')
        make_archive(str(zip_path), 'zip', self.dir)

    def restore(self, name: str):
        zip_path = self.backups / name if present(name) else Path(max(glob(str(self.backups / '*.zip')), key=getctime))
        print(f'Restoring from: {zip_path.name} for {self}')
        unpack_archive(zip_path, self.dir)

    def clean(self, count: int):
        print(f'Cleaning oldest backups: {count} from {self}')
        files = sorted(glob(str(self.backups / '*.zip')), key=getctime)
        if count >= len(files):
            count = len(files) - 1
        files = files[:count]
        for file in files:
            print(Path(file).name)
            send2trash(file)

    def list(self, count: int):
        backups = listdir(self.backups)
        backups.reverse()
        print(f'Available backups for {self}')
        lines = [b.strip('.zip') for b in backups[:count if count > 0 else len(backups)]]
        print(*lines, sep='\n')
        if count > 0:
            print(f'And {len(backups) - count} more...')

    def process(self, parser: ArgumentParser, args: Namespace):
        if args.backup:
            self.backup(args.backup)
        elif args.restore:
            self.restore(args.restore)
        elif args.clean:
            self.clean(args.clean)
        elif args.list:
            self.list(args.list)
        else:
            parser.print_usage()


def main():
    parser, args = get_args()
    try:
        if present(args.name):
            save = Save(GAME_MODES[args.type], args.name)
        else:
            save = Save.from_cwd()
        save.process(parser, args)
    except ValueError as ve:
        print(ve)


if __name__ == '__main__':
    main()
