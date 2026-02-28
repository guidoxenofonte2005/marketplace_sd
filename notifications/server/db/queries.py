from 

async def saveEvent(connection, event):
    await connection.execute()

async def searchHistory(connection, user_id: str, limit: int = 10):
    pass