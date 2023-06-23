import psycopg2
from os import system
import logging
from backend import App
from helper import pause

class AppGui():
    @classmethod
    def run(self):
        try:
            DAO = App('database.ini', 'postgresql')
        except psycopg2.OperationalError as e:
            print(f'Unable to connect to database: {e}')
            logging.error(e)
            print('Exiting...')
            pause(True)
            exit()

        choice = ''
        while choice != 'q':
            system('cls')
            print('What do you want to do:')
            print('c        create table')
            print('cc       create category')
            print('t        create team')
            print('g        create game')
            print('p        create player')
            print('ep       edit player')
            print('s        print standings')
            print('pg       print games')
            print('pp       print players')
            print('sp       search players')
            print('r        reset games')
            print('q        quit')

            choice = input()
            if choice == 'c':
                DAO.create_tables()
            elif choice == 'cc':
                DAO.create_category()
            elif choice == 't':
                DAO.create_team()           
            elif choice == 'g':
                DAO.create_game()
            elif choice == 'p':
                DAO.create_player()
            elif choice == 'ep':
                DAO.edit_player()
            elif choice == 's':
                DAO.print_standings()
            elif choice == 'pg':
                DAO.print_games()
            elif choice == 'pp':
                DAO.print_playersByTeam()
                pause(True)
            elif choice == 'sp':
                DAO.search_player()
            elif choice == 'r':
                DAO.reset_games()
            elif choice == 'q':
                print('Bye bye!')
            else:
                print('Wrong command')
                pause()
        pause(True)