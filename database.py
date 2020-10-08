import mysql.connector

_db = mysql.connector.connect(
    host="localhost",
    user="root",
    database="listedhere"
)

_db_cursor = _db.cursor()

class Cell:
    def __init__(self, column_name, value):
        self.column_name = column_name
        self.value = value

# Sends an insert request to the MySQL database
# cells is a list of cells that will be placed into the new row on the table
# table_name is the table that is being manipulated
# Returns no response
def sendInsertQuery(table_name, cells):
    query1 = ""
    query2 = ""
    for i in range(0, len(cells)):
        if i == 0:
            query1 += cells[i].column_name
            query2 += "'%s'" % (cells[i].value)
        else:
            query1 += ", " + cells[i].column_name
            query2 += ", '%s'" % (cells[i].value)
    
    whole_query = "INSERT INTO %s (%s) VALUES(%s)" % (table_name, query1, query2)
    _db_cursor.execute(whole_query)
    _db.commit()

# Sends an update request to the MySQL database
# identifier_cell is the cell that identifies a specific row to update
# cells is a list of cells that will be placed into the new row on the table
# table_name is the table that is being manipulated
# Returns no response
def sendUpdateQuery(table_name, identifier_cell, cells):
    query1 = ""
    query2 = identifier_cell.column_name + "='%s'" % (identifier_cell.value)
    for i in range(0, len(cells)):
        if i == 0:
            query1 += cells[i].column_name + "='%s'" % (cells[i].value)
        else:
            query1 += ", " + cells[i].column_name + "='%s'" % (cells[i].value)
    
    whole_query = "UPDATE %s SET %s WHERE %s" % (table_name, query1, query2)
    _db_cursor.execute(whole_query)
    _db.commit()

# Searches the database table for any items that have a column with the given cell info
# Returns True of False
def containedInDatabase(table_name, cell):
    _db_cursor.execute("SELECT * FROM %s WHERE %s='%s'" % (table_name, cell.column_name, cell.value))
    if len(_db_cursor.fetchall()) == 1:
        return True
    return False

# Searches the database table for any items that have a column with the given cell info
# Returns the output of the database
def getFromDatabase(table_name, cell):
    _db_cursor.execute("SELECT * FROM %s WHERE %s='%s'" % (table_name, cell.column_name, cell.value))
    return _db_cursor.fetchall()