import sqlite3
import re

class Database:
    def __init__(self, dbName):
        self.__db_conn = sqlite3.connect(dbName)
        self.cursor = self.__db_conn.cursor()
        
        
    def tableExists(self, tableName):
        """
        Проверяет существует ли таблица
        
        :param tableName: имя ттаблицы
        """
        self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (tableName,)
        )
        return self.cursor.fetchone() is not None
    
    
    def createTable(self, tableName, columns):
        """
        Создает новую таблицу
        
        :param tableName: Имя таблицы
        :param columns: Массив объектов с name - имя свойства, params - его настройки 
        (например: name: 'id', params: 'integer primary key autoincrement')
        """
        if not tableName.isidentifier():
            raise ValueError("Invalid table name")
        
        if self.tableExists(tableName=tableName):
            raise ValueError(f"Table {tableName} is already exists")
        
        sqlColumns = ", ".join(
            f"{column.name} {column.params}" for column in columns
        )
        
        sql = f"CREATE TABLE {tableName} ({sqlColumns})"
        
        self.cursor.execute(sql)
        self.__db_conn.commit()
    
    
    def insertIntoTable(self, tableName, datas):
        """
        Вставляет данные в существующую таблицу
        
        :param tableName: Имя таблицы
        :param datas: Массив объектов, где name - имя свойства, value - его значение
        """
        if not self.tableExists(tableName=tableName):
            raise ValueError(f"Table {tableName} is not exists")
        
        sqlValueNames = ", ".join(
            f"{data.name}" for data in datas
        )
        sqlValues = ", ".join(
            "?" for _ in datas
        )
        values = [data.value for data in datas]
            
        
        sql = f"INSERT INTO {tableName} ({sqlValueNames}) VALUES ({sqlValues})"
        self.cursor.execute(sql, values)
        self.__db_conn.commit()
        
    def getFromTable(self, tableName, selectOperator, valueName, value):
        """
        Возвращает данные из таблицы
        
        :param tableName: Имя таблицы
        :param selectOperator: Оператор сравнения: >, <, >=, <=, =
        :param valueName: Имя переменной для сравнения
        :param value: Искомое значение
        """
        if not self.tableExists(tableName=tableName):
            raise ValueError(f"Table {tableName} does not exist")
        
        sql = f"SELECT * FROM {tableName} WHERE {valueName} {selectOperator} ?"
        self.cursor.execute(sql, [value])
        return self.cursor.fetchall()

    def getAggregate(
            self,
            tableName,
            aggregate,      # COUNT, SUM, AVG, MIN, MAX
            columnName="*", # к чему применяется агрегат
            valueName=None,
            operator=None,
            value=None
        ):
            """
            Возвращает агрегированный результат из таблицы
            """

            if not self.tableExists(tableName):
                raise ValueError(f"Table {tableName} does not exist")

            sql = f"SELECT {aggregate}({columnName}) FROM {tableName}"
            params = []

            if valueName and operator and value is not None:
                # если value похоже на дату, используем date()
                if isinstance(value, str) and re.match(r"\d{4}-\d{2}-\d{2}", value):
                    sql += f" WHERE date({valueName}) {operator} ?"
                else:
                    sql += f" WHERE {valueName} {operator} ?"
                params.append(value)

            # выполняем запрос
            print("Запрос к БД: " + sql)
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            return result[0] if result else 0
