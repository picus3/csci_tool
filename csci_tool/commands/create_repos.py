import argparse
import logging
import os
import sys

from .base import BaseCommand
from ..config import Config
from ..repo import Repo
from ..student import Student

logger = logging.getLogger(__name__)


class CreateReposCommand(BaseCommand):
    NAME = 'create-repos'
    HELP = 'create student repos'

    def populate_args(self):
        self.add_argument('students', nargs='?', type=argparse.FileType('r'),
                          default=sys.stdin)

    def run(self, args):
        if args.students == sys.stdin:
            if sys.stdout.isatty():
                print('Please enter students emails and GitHub names one per ' +
                      'line separated by a space')
                print('Repos will be created after EOF')

        students = args.students.readlines()
        students = [s.strip().split(' ') for s in students]
        students = [Student(email=s[0], github=s[1]) for s in students]

        logger.info('Creating repos for %d students', len(students))

        config = Config.load_config()

        # make a commit with the new students in the meta repo
        meta_repo = Repo.meta_repo()
        cwd = os.getcwd()
        os.chdir(config.meta_path)

        with open('students.txt', 'a') as github_file:
            lines = [s.email + ' ' + s.github for s in students]
            github_file.writelines(lines)

        logger.debug('Adding students.txt to index')
        meta_repo.index.add('students.txt')
        logger.debug('Commiting changes')
        meta_repo.index.commit('Added {} students'.format(len(students)))
        logger.debug('Pushing to remote')
        meta_repo.remote().push()

        os.chdir(cwd)

        logger.info('Created repos, pushed updated meta to GitHub')