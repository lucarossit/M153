import psycopg2
from config import ConfigReader
import logging
from helper import pause
from psycopg2 import sql

class App(ConfigReader):

    def __init__(self, configfile, section):
        logging.basicConfig(filename='error.log', level=logging.ERROR)
        super().__init__(configfile='database.ini', section='postgresql')
        try:
            params = super().config()
            self.conn = psycopg2.connect(**params)
            self.cur = self.conn.cursor()
        except psycopg2.OperationalError as e:
            logging.error(e)
            raise e

    def __repr__(self):
        dsn_parameters = self.conn.get_dsn_parameters()
        return f"Connected to database '{dsn_parameters['dbname']}' on host '{dsn_parameters['host']}' as user '{dsn_parameters['user']}'"    

    def __del__(self):
        if hasattr(self, "cur"):
            self.cur.close()
            self.conn.close()

    def create_tables(self):
        sql = """
            CREATE TABLE category (
                id                          SERIAL PRIMARY KEY,
                name                        VARCHAR(255)
            );

            CREATE TABLE team (
                id                          SERIAL PRIMARY KEY,
                name                        VARCHAR(255), 
                points                      INT,
                category_id                 INTEGER REFERENCES category(id) ON DELETE CASCADE
            );

            CREATE TABLE player (
                id                          SERIAL PRIMARY KEY,
                first_name                  VARCHAR(100), 
                last_name                   VARCHAR(255),
                age                         INT,
                team_id                     INTEGER REFERENCES team(id) ON DELETE CASCADE
            );

            CREATE TABLE game (
                id                          SERIAL PRIMARY KEY,
                first_team                  INTEGER REFERENCES team(id) ON DELETE CASCADE,
                second_team                 INTEGER REFERENCES team(id) ON DELETE CASCADE,
                first_score                 INT,
                second_score                INT
            );
            """
        try:
            self.cur.execute(sql)
            self.conn.commit()
            print(f'Table category, team, player, game created!')
        except psycopg2.Error as e:
            logging.error(e)
            self.conn.rollback()
            print(f'Tables category, team, player, game could not be created:\n{e}')
        pause(True)

    def create_category(self):
        print('What is the name of the category')
        name = input()
        sql = """INSERT INTO category (name) VALUES (%s)"""
        try:
            self.cur.execute(sql, (name,))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def get_categories(self):
        sql = "SELECT id, name FROM category;"
        try:
            self.cur.execute(sql)
            categories = self.cur.fetchall()
            valid = False
            print('Choose a category')
            print('\nCATEGORIES:')
            while(valid == False):
                for category in categories:
                        print(str(category[0]) + "\t" + category[1])
                id = input()
                for category in categories:
                    if (str(category[0])==id):
                        valid = True
                if (valid == False):
                    print('Not valid. Try again.')
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        return id

    def create_team(self):
        print('What is the name of the team')
        name = input()
        print('In which category do they play')
        category = self.get_categories()
        sql = """INSERT INTO team (name, category_id, points) VALUES (%s, %s, %s)"""
        try:
            self.cur.execute(sql, (name, category, '0',))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def create_game(self):
        teams = self.get_teams()
        valid = False
        while(valid == False):
            print('Select first team\n')
            for team in teams:
                print(str(team[0]) + "\t" + team[1])
            team1 = input()
            for team in teams:
                if (str(team[0]) == team1):
                    valid = True
            if (valid == False):
                print('Not valid. Try again.')
        valid = False
        while(valid == False):
            print('Type in score for team 1')
            score1 = input()
            valid = score1.isdigit()
            if (valid == False):
                print('Not valid. Try again.')
        valid = False
        while(valid == False):
            print('Select second team\n')
            for team in teams:
                if (str(team[0]) != team1):
                    print(str(team[0]) + "\t" + team[1])
            team2 = input()
            for team in teams:
                if (str(team[0]) == team2):
                    valid = True
            if (valid == False):
                print('Not valid. Try again.')
        valid = False
        while(valid == False):
            print('Type in score for team 2')
            score2 = input()
            valid = score2.isdigit()
            if (valid == False):
                print('Not valid. Try again.')
        sql = """INSERT INTO game (first_team, second_team, first_score, second_score) VALUES (%s, %s, %s, %s)"""
        try:
            self.cur.execute(sql, (team1, team2, score1, score2,))
            self.conn.commit()
            if (score1 > score2):
                self.give_points(team1, 3)
            elif(score1 < score2):
                self.give_points(team2, 3)
            else:
                self.give_points(team1, 1)
                self.give_points(team2, 1)
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def give_points(self, team, points):
        oldPoints = self.get_points(team)
        newPoints = int(oldPoints) + int(points)
        sql = """UPDATE team SET points = %s WHERE id = %s"""
        try:
            self.cur.execute(sql, (str(newPoints), team,))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)

    def get_points(self, team):
        sql = """SELECT points FROM team WHERE id = %s"""
        try:
            self.cur.execute(sql, (team,))
            points = self.cur.fetchone()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        return points[0]
    
    def get_teams(self):
        category = self.get_categories()
        sql = """SELECT id, name FROM team WHERE category_id = %s ORDER BY id"""
        try:
            self.cur.execute(sql, (category,))
            teams = self.cur.fetchall()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        return teams
    
    def print_standings(self):
        category = self.get_categories()
        sql = """SELECT name, points FROM team WHERE category_id = %s ORDER BY points DESC"""
        try:
            self.cur.execute(sql, (category,))
            teams = self.cur.fetchall()
            i = 1
            print('\nSTANDINGS:')
            for team in teams:
                print(str(i) + ".\t" + team[0] + "\t" + str(team[1]))
                i = i + 1
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def print_games(self):
        category = self.get_categories()
        sql = """SELECT first_team, second_team, first_score, second_score FROM game INNER JOIN team on first_team = team.id WHERE team.category_id = %s"""
        try:
            self.cur.execute(sql, (category,))
            games = self.cur.fetchall()
            print('\nGAMES:')
            for game in games:
                team1 = self.get_teamName(game[0])
                team2 = self.get_teamName(game[1])
                print(team1 + "\t" + str(game[2]) + "\t" + ":\t" + str(game[3]) + "\t" + team2)
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def get_teamName(self, team):
        sql = """SELECT name FROM team WHERE id = %s"""
        try:
            self.cur.execute(sql, (team,))
            name = self.cur.fetchone()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        return name[0]
    
    def create_player(self):
        teams = self.get_teams()
        valid = False
        while(valid == False):
            print('Choose your team')
            for team in teams:
                print(str(team[0]) + "\t" + team[1])
            id = input()
            for team in teams:
                if (str(team[0]) == id):
                    valid = True
            if (valid == False):
                print('Not valid. Try again.')
        print("What's your first name?")
        first_name = input()
        print("What's your last name?")
        last_name = input()
        valid = False
        while(valid == False):
            print('How old are you')
            age = input()
            valid = age.isdigit()
            if (valid == False):
                print('Not valid. Try again.')
        sql = """INSERT INTO player (first_name, last_name, age, team_id) VALUES (%s, %s, %s, %s)"""
        try:
            self.cur.execute(sql, (first_name, last_name, age, id,))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def print_playersByTeam(self):
        teams = self.get_teams()
        valid = False
        while(valid == False):
            print('\nTEAMS:')
            for team in teams:
                print(str(team[0]) + "\t" + team[1])
            id = input()
            for team in teams:
                if (str(team[0]) == id):
                    valid = True
            if (valid == False):
                print('Not valid. Try again.')
        sql = """SELECT id, first_name, last_name, age FROM player WHERE team_id = %s"""
        try:
            self.cur.execute(sql, (id,))
            players = self.cur.fetchall()
            print('\nPLAYERS:')
            for player in players:
                print(str(player[0]) + "\t" + player[1] + "\t" + player[2] + "\t" + str(player[3]))
        except psycopg2.Error as e:
            logging.error(e)
            print(e)

    def print_players(self):
        sql = """SELECT * FROM player"""
        try:
            self.cur.execute(sql)
            players = self.cur.fetchall()
            print('\nPLAYERS:')
            for player in players:
                print(str(player[0]) + "\t" + player[1] + "\t" + player[2] + "\t" + str(player[3]))
        except psycopg2.Error as e:
            logging.error(e)
            print(e)

    def edit_player(self):
        print('\nChoose player to edit')
        player = self.search_player()
        print('New team')
        teams = self.get_teams()
        valid = False
        while(valid == False):
            print('\nTEAMS:')
            for team in teams:
                print(str(team[0]) + "\t" + team[1])
            id = input()
            for team in teams:
                if (str(team[0]) == id):
                    valid = True
            if (valid == False):
                print('Not valid. Try again.')
        valid = False
        while(valid == False):
            print("New first name?")
            first_name = input()
            if (first_name != ""):
                valid = True
            else:
                print('first name cannot be empty')
        valid = False
        while(valid == False):
            print("New last name?")
            last_name = input()
            if (last_name != ""):
                valid = True
            else:
                print('last name cannot be empty')
        valid = False
        while(valid == False):
            print('New age')
            age = input()
            valid = age.isdigit()
            if (valid == False):
                print('Not valid. Try again.')
        sql = """UPDATE player SET first_name = %s, last_name = %s, age = %s, team_id = %s WHERE id = %s"""
        try:
            self.cur.execute(sql, (first_name, last_name, age, id, player))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def search_player(self):
        print('How do you wanna search?')
        print('1    first name')
        print('2    second name')
        chosen = input()
        if (chosen == '1'):
            print("What's the first name of the player?")
            name = input()
            name = "%" + name + "%"
            sql = """SELECT * FROM player WHERE first_name ILIKE %s"""
        else:
            print("What's the last name of the player?")
            name = input()
            name = "%" + name + "%"
            sql = """SELECT * FROM player WHERE last_name ILIKE %s"""
        try:
            self.cur.execute(sql, (name,))
            players = self.cur.fetchall()
            print('\nPLAYERS:')
            for player in players:
                team = self.get_teamName(player[4])
                print(str(player[0]) + "\t" + player[1] + "\t" + player[2] + "\t" + str(player[3]) + "\t" + team)
            player = input()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        return player
    
    def reset_games(self):
        sql = """TRUNCATE game;
            UPDATE team SET points = 0"""
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)

    def delete_player(self):
        print('\nChoose player to delete')
        player = self.search_player()
        sql = """DELETE FROM player WHERE id = %s"""
        try:
            self.cur.execute(sql, (player, ))
            self.conn.commit()
        except psycopg2.Error as e:
            logging.error(e)
            print(e)
        pause(True)