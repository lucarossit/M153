import psycopg2
from os import system
import logging
from app import App
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
            print('1        create table')
            print('2        create category')
            print('3        create team')
            print('4        create game')
            print('5        create player')
            print('6        edit player')
            print('7        delete player')
            print('8        print standings')
            print('9        print games')
            print('10       print players')
            print('11       search players')
            print('12       reset games')
            print('q       quit')

            choice = input()
            if choice == '1':
                DAO.create_tables()
            elif choice == '2':
                DAO.create_category()
            elif choice == '3':
                DAO.create_team()           
            elif choice == '4':
                DAO.create_game()
            elif choice == '5':
                DAO.create_player()
            elif choice == '6':
                DAO.edit_player()
            elif choice == '7':
                DAO.delete_player()
            elif choice == '8':
                DAO.print_standings()
            elif choice == '9':
                DAO.print_games()
            elif choice == '10':
                DAO.print_playersByTeam()
                pause(True)
            elif choice == '11':
                DAO.search_player()
            elif choice == '12':
                DAO.reset_games()
            elif choice == 'q':
                print('Bye bye!')
            else:
                print('Wrong command')
                pause()
        pause(True)