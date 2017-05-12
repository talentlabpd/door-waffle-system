#!/usr/bin/python

import MySQLdb as sql

class TLSqlAPI:
    db = None
    cursor = None
    __tipi_socio = ['Senior','Standard']



    """
    Costruttore, richiede host, nome utente, password e nome del db a cui connettersi.
    Se la tabella delle peresenze non è presente viene inizializzata.
    """
    def __init__(self,host,user,pwd,db):
        if(host=='localhost'):
            self.db = sql.connect(user=user,passwd=pwd,db=db,unix_socket='/opt/lampp/var/mysql/mysql.sock')
        else:
            self.db = sql.connect(host,user,pwd,db)
        self.cursor = self.db.cursor()
        self.cursor.execute('SELECT * FROM information_schema.tables WHERE table_name="Presenze"')
        if(not self.cursor.fetchone()):
            try :
                self.cursor.execute("""CREATE TABLE Presenze (
                    access_id INT NOT NULL AUTO_INCREMENT,
                    user_id INT,
                    login_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (access_id),
                    FOREIGN KEY (user_id) REFERENCES Users(user_id)
                )""")
                self.db.commit()
            except Exception as e:
                print(e)
                self.db.rollback()


    def __del__(self):
        self.db.close()

    """
    Metodo per chiudere la connessione al db
    """
    def close(self):
        self.db.close()

    """
    Metodo che esegue una query generica senza troppi controlli, debug poi verrà rimosso probabilmente
    """
    def execute(self,query):
        self.cursor.execute(query)
        data= self.cursor.fetchall()
        return data

    """
    Metodo per ritornare la versione del db
    """
    def version(self):
        self.cursor.execute('SELECT VERSION()')
        data = self.cursor.fetchone()
        return data


    """
    Accesso al TL, unico parametro che richiede è il codice di accesso, se è presente tra i codici dei soci viene aggiunto l'accesso alla tabella
    e ritorna True se il codice è corretto ed è stato inserito negli accessi, false altrimenti. Accessi ripetuti dello stesso codice vengono salvati con timestamp diversi
    """
    def enter(self,code):
        if(not(type(code) is str)):
            code = str(code)
        self.cursor.execute('SELECT user_id,nome,cognome,password_login FROM Users WHERE password_login='+`code`)
        entered = self.cursor.fetchone()
        if(entered is not None):
            try :
                self.cursor.execute('INSERT INTO Presenze(user_id) VALUES ('+str(entered[0])+')')
                self.db.commit()
                return True
            except Exception as e:
                print(e)
                self.db.rollback()
                return False
        return False

    """
    Uscita dal TL, unico parametro che richiede è il codice di accesso, se è presente tra i codici dei soci viene rimosso l'accesso alla tabella
    e ritorna True se il codice è corretto ed è stato rimosso dagli accessi, false altrimenti. Rimuove sempre l'accesso più vecchio
    """
    def exit(self,code):
        if(not(type(code) is str)):
            code = str(code)
        self.cursor.execute('SELECT user_id FROM Presenze WHERE password_login='+`code`)
        exited = self.cursor.fetchone()
        if(exited is not None):
            try :
                self.cursor.execute('DELETE FROM Presenze WHERE user_id='+str(user_id)+' LIMIT 1')
                self.db.commit()
                return True
            except Exception as e:
                print(e)
                self.db.rollback()
                return False
        return False

    """
    Ritorna la lista delle presenze uniche. Se è specificato un tipo di socio ("Senior" o "Standard") ritorna la lista dei soci di quel tipo, altrimenti torna la lista di tutte le presenze
    """
    def list(self,tipo=None):
        query = 'SELECT DISTINCT Presenze.user_id,nome,cognome,tipo_socio FROM Presenze JOIN Users on Presenze.user_id = Users.user_id'
        if(tipo in self.__tipi_socio):
            query = query + ' WHERE tipo_socio="'+tipo+'"'
        self.cursor.execute(query)
        presenze  = self.cursor.fetchall()
        return presenze
