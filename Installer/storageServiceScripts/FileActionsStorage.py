from DateTimeConverter import DateTimeConverter
import json
import os
import sqlite3
import time


class FileActionsStorage:
    def __init__(self, dbName, journalDirectory="journals"):
        self.dbName = dbName
        self.conn = sqlite3.connect(self.dbName)
        self.createTable()
        self.journalDirectory = journalDirectory

    def createTable(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS fileActions (
                storageId TEXT,
                filepath TEXT,
                action TEXT,
                result TEXT,
                timestamp DATETIME,
                contentType TEXT,
                jsonData TEXT
            )
        """
        )
        self.conn.commit()
        cursor.close()

    def saveJournalFile(self, fileName, jsonObject):
        currentDir = os.path.dirname(os.path.abspath(__file__))
        subDir = os.path.join(currentDir, self.journalDirectory)

        if not os.path.exists(subDir):
            os.makedirs(subDir)
        filePath = os.path.join(subDir, fileName)

        with open(filePath, "w") as jsonFile:
            json.dump(jsonObject, jsonFile, indent=4)

    def addFileActionFromJson(self, jsonObject):
        time.sleep(0.001)
        timeStamp = time.time_ns()
        # DateTimeConverter.getBase26TimeStamp()

        journalFileName = f'{jsonObject["storageId"]}.{timeStamp}.json'

        jsonObject["timeStamp"] = timeStamp

        self.saveJournalFile(journalFileName, jsonObject)

        self.addFileAction(
            jsonObject["storageId"],
            jsonObject["filePath"],
            jsonObject["action"],
            jsonObject["result"],
            jsonObject["timeStamp"],
            jsonObject["contentType"],
            json.dumps(jsonObject, indent=4),
        )

        return {"timeStamp": timeStamp}

    def addFileAction(
        self, storageId, filepath, action, result, timestamp, contentType, jsonData
    ):
        print("preparing cursor...")
        self.conn = sqlite3.connect(self.dbName)
        cursor = self.conn.cursor()

        print("cursor.execute()...")
        cursor.execute(
            """
            INSERT INTO
                fileActions
                (storageId, filepath, action, result, timestamp, contentType, jsonData)
                VALUES
                (?, ?, ?, ?, ?, ?, ?)
            """,
            (storageId, filepath, action, result, timestamp, contentType, jsonData),
        )

        print("cursor.commit()...")
        self.conn.commit()

        print("cursor.close()...")
        cursor.close()

    def getIncompleteRecordSetsFromJson(self, jsonObject):
        retVal = self.getIncompleteRecordSets(
            jsonObject["criteria"], jsonObject["contentType"]
        )

        return retVal

    def getIncompleteRecordSets(self, criteriaList, contentType, recordCountLimit=1):
        self.conn = sqlite3.connect(self.dbName)
        cursor = self.conn.cursor()

        sql = """
            SELECT
                storageId,
                GROUP_CONCAT(action) AS concatenated_actions
            FROM
                fileActions
            WHERE
                contentType = ?
            GROUP BY
                storageId
            HAVING
                COUNT(*) < ?
                AND (
            """

        # Build the dynamic OR conditions for each action value
        for i, action in enumerate(criteriaList):
            sql += "action LIKE ?"
            if i < len(criteriaList) - 1:
                sql += " OR "
        if recordCountLimit > 0:
            # Complete the query
            sql += f")  LIMIT {recordCountLimit};"
        else:
            sql += ");"
        # print(sql)

        sqlParams = (contentType, len(criteriaList), *criteriaList)

        # Execute the query with dynamic parameters
        cursor.execute(sql, sqlParams)

        result = cursor.fetchall()
        cursor.close()

        retVal = []

        for storageId, action in result:
            retVal.append(storageId)
        return retVal

    def getByStorageIdValueFromJson(self, jsonObject):
        retVal = self.getByStorageIdValue(jsonObject["storageId"])

        return retVal

    def getByStorageIdValue(self, value):
        self.conn = sqlite3.connect(self.dbName)
        cursor = self.conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM fileActions
            WHERE storageId = ?
            """,
            (value,),
        )

        # Get column names
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        result = []

        for row in rows:
            rowData = {}
            for i, columnName in enumerate(columns):
                if "json" in columnName:
                    rowData[columnName] = json.loads(row[i])
                else:
                    rowData[columnName] = row[i]
            result.append(rowData)

        cursor.close()

        # Create a JSON object with the table name and rows
        jsonObject = {"tableName": result}

        return jsonObject

    def purgeByStorageId(self, storageId):
        self.conn = sqlite3.connect(self.dbName)
        cursor = self.conn.cursor()
        cursor.execute(
            """
            DELETE FROM fileActions
            WHERE storageId = ?
            """,
            (storageId,),
        )
        self.conn.commit()
        cursor.close()

    def purgeAllRecords(self):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM fileActions")
        self.conn.commit()
        cursor.close()


if __name__ == "__main__":
    from MinuteCodes import MinuteCodes

    payload = {
        "storageId": None,
        "action": "store",
        "result": "successful",
        "contentType": "video",
        "minuteCodes": [],
        "description": "fake file that refers to nothing",
        "filePath": "",
    }

    db = FileActionsStorage("store.db")
    # db.purgeAllRecords()

    for i in range(1, 1000, 1):
        minCodes = MinuteCodes.getCurrentBlockOfCodes()
        payload["action"] = "store"
        payload["storageId"] = DateTimeConverter.getBase26TimeStamp()
        payload["minuteCodes"] = minCodes
        payload["filePath"] = f"/home/diyaqua/Videos/{minCodes[0]}.m4v"
        db.addFileActionFromJson(payload)
        if i % 3 == 0:
            payload["action"] = "ioa"
            db.addFileActionFromJson(payload)
        if i % 100 == 0:
            print(f"Record count: {i}")
