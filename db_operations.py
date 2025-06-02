import sqlite3


class DbOperations:

    def connect_to_db(self):
        conn=sqlite3.connect('my_database.db')
        return conn
    

    def create_table(self,table_name="password_info"):
        conn=self.connect_to_db()
        query=f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                Created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                website TEXT NOT NULL,
                username Varchar(200),
                password VARCHAR(50)
            );
        '''


        with conn as conn:
            cursor=conn.cursor()
            cursor.execute(query)


    def create_record (self,data,table_name="password_info"):
        website=data['website']
        username=data['username']
        password=data['password']
        conn=self.connect_to_db()
        query=f'''
            INSERT INTO {table_name}('website','username','password') VALUES
            ( ?, ?, ?);
        '''

        with conn as conn:
            cursor=conn.cursor()
            cursor.execute(query,(website,username,password))
           
    

    def show_records(self,table_name="password_info"):
        conn=self.connect_to_db()
        query=f'''
            SELECT * FROM {table_name};
        '''

        with conn as conn:
            cursor=conn.cursor()
            list_records= cursor.execute(query)
            return list_records
        

    
    def update_records(self,data,table_name="password_info"):
        ID=data['ID']
        website=data['website']
        username=data['username']
        password=data['password']
        conn=self.connect_to_db()
        query=f'''
          UPDATE {table_name} SET website = ?, username = ?, password = ? WHERE ID = ?;
        '''

        with conn as conn:
            cursor=conn.cursor()
            cursor.execute(query,(website,username,password,ID))
        

    def delete_records(self,ID,table_name="password_info"):
        conn=self.connect_to_db()
        query=f'''
          DELETE FROM  {table_name} WHERE ID = ?;
        '''

        with conn as conn:
            cursor=conn.cursor()
            cursor.execute(query,(ID,))    


    def search_records(self, search_term, table_name="password_info"):
        conn = self.connect_to_db()
        query = f'''
        SELECT * FROM {table_name} 
        WHERE website LIKE ? OR username LIKE ?;
    '''
        with conn as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
            return cursor.fetchall()  # Return matched records as a list
        