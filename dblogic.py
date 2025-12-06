import sqlite3

class InfoDB:
    def __init__(self, database):
        self.database = database

    def tablecreate(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            CREATE TABLE IF NOT EXISTS infoDB (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            cookies INTEGER DEFAULT 0,
            water INTEGER DEFAULT 0,
            last_action_time INTEGER DEFAULT 0,
            last_reset_date TEXT,
            last_cookie TEXT,
            last_water TEXT)''')
            conn.commit()

    def registration(self, user_id, user_name, date):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('INSERT INTO InfoDB VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (user_id, user_name, 0, 0, 0, 0, date, date))
            conn.commit()

    def get_users(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT * FROM InfoDB''')
            return [x[0] for x in cur.fetchall()]
        
    # Leaderboard

    def get_water_leaderboard(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''
        SELECT user_id, username, ROUND(water, 3) 
        FROM InfoDB 
        ORDER BY water DESC
        LIMIT 10''')
        return cur.fetchall()
    
    def get_cookies_leaderboard(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''
        SELECT user_id, username, ROUND(cookies, 3) 
        FROM InfoDB 
        ORDER BY cookies DESC
        LIMIT 10''')
        return cur.fetchall()
        
        
    # Amount of Water
    
    def update_water(self, user_id, amount):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            UPDATE InfoDB SET water = water + ? WHERE user_id = ?
            ''', (amount, user_id))
            conn.commit()

    def get_amount(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''SELECT ROUND(water, 3), ROUND(cookies, 3) FROM InfoDB WHERE user_id = ?''', (user_id))
        return cur.fetchall()[0]


    # Update Amount of Cookies
    
    def update_cookies(self, user_id, amount):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            UPDATE InfoDB SET cookies = cookies + ? WHERE user_id = ?
            ''', (amount, user_id))
            conn.commit()

    #Cookie

    def update_last_time_cookie(self, date_now, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            UPDATE InfoDB SET last_cookie = ? WHERE user_id = ?
            ''', (date_now, user_id))
            conn.commit()

    def get_last_time_cookie(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(''' 
                SELECT last_cookie FROM InfoDB
                WHERE user_id = ?''', (user_id))
            return cur.fetchall()[0][0]
        
    #Water

    def update_last_time_water(self, date_now, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''
            UPDATE InfoDB SET last_water = ? WHERE user_id = ?
            ''', (date_now, user_id))
            conn.commit()

    def get_last_time_water(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute(''' 
                SELECT last_water FROM InfoDB
                WHERE user_id = ?''', (user_id))
            return cur.fetchall()[0][0]

if __name__ == '__main__':
    manager = InfoDB('InfoDB')
    #manager.tablecreate()
    #manager.update_last_time('10:00', 4900255)
    #manager.registration(4900255, 'gsgsgghw')
    #print(manager.get_last_time_water([(1692557632)]))
    #print(manager.get_water_leaderboard())
    #print(manager.get_amount([(1692557632)]))