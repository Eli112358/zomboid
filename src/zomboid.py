from dataclasses import dataclass
from datetime import datetime
from glob import glob
from os import getcwd
from os.path import getctime
from pathlib import Path
from shutil import make_archive, unpack_archive

BACKUP_FORMAT = '%Y-%m-%d-%H-%M'
GAME_FILES = Path.home() / 'Zomboid'
GAME_MODES = {
    'a': 'Apocalypse',
    's': 'Survivor',
    'b': 'Builder',
    'c': 'Sandbox'
}
STORE_TRUE = 'store_true'


def present(name):
    return type(name) is str and name != ''


@dataclass
class Save:
    type: str
    name: str

    @classmethod
    def from_cwd(cls):
        """
        Raises `ValueError` if not in a directory relative to game files
        :return: Derive from current working directory
        """
        cwd = Path(getcwd())
        if cwd.is_relative_to(GAME_FILES):
            return Save(*cwd.parts[-2:])
        raise ValueError('Invalid path')

    def __repr__(self):
        return f'{self.type}, {self.name}'

    @property
    def backups(self) -> Path:
        return GAME_FILES / 'backups' / self.type / self.name

    @property
    def dir(self) -> Path:
        return GAME_FILES / 'saves' / self.type / self.name

    def backup(self, name: str):
        zip_name = name if present(name) else datetime.now().strftime(BACKUP_FORMAT)
        zip_path = GAME_FILES / 'backups' / self.type / self.name / zip_name
        make_archive(str(zip_path), 'zip', self.dir)

    def restore(self, name: str):
        zip_path = self.backups / name if present(name) else max(glob(str(self.backups / '*.zip')), key=getctime)
        unpack_archive(zip_path, self.dir)

    def process(self, args):
        if args.backup:
            self.backup(args.backup)
        elif args.restore:
            self.restore(args.restore)


def get_args():
    """
    Set up an ArgumentParser and use it on sys.argv

    :return: Parsed args
    """
    from argparse import ArgumentParser
    from sys import argv

    parser = ArgumentParser(description='Manage backups for Project Zomboid')
    parser.add_argument('-t', '--type', choices=GAME_MODES.keys(), default=list(GAME_MODES.keys())[-1],
                        help='Type of save game, required unless ran from within save type folder')
    parser.add_argument('-n', '--name', default='',
                        help='Name of save game, required unless ran from within save game folder')
    cmd = parser.add_mutually_exclusive_group()
    cmd.add_argument('-b', '--backup', default='', nargs='?', const=True,
                     help='Save a backup, default name is the current date-time')
    cmd.add_argument('-r', '--restore', default='', nargs='?', const=True,
                     help='Restore from a backup, default is the most recent')
    cmd.add_argument('-l', '--list', action=STORE_TRUE,
                     help='List available backups, the default action')
    return parser.parse_args(argv[1:])


def list_backups():
    """
    WIP
    """
    raise NotImplementedError


def main():
    args = get_args()
    if args.list:
        list_backups()
    else:
        try:
            if args.name:
                save = Save(GAME_MODES[args.type], args.name)
            else:
                save = Save.from_cwd()
            print(save)
            save.process(args)
        except ValueError as ve:
            print(ve)


if __name__ == '__main__':
    main()
