async def checkIfProcessed(connection, event_id) -> bool:
    response = await connection.fetchrow(
        """SELECT event_id FROM processed_events WHERE event_id = $1""", event_id
    )

    return True if response else False


async def markAsProcessed(connection, event_id) -> None:
    await connection.execute(
        """INSERT INTO processed_events (event_id) VALUES ($1) ON CONFLICT (event_id) DO NOTHING""",
        event_id,
    )
