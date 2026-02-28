async def saveEvent(connection, event) -> None:
    await connection.execute(
        "INSERT INTO events (event_id, event_type, target_user, payload, lamport_ts, emmited_time) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT (event_id) DO NOTHING",
        event.event_id,
        event.event_type,
        event.target_user,
        event.payload,
        event.lamport_ts,
        event.emitted_time,
    )


async def getUserHistory(connection, user_id: str, limit: int = 10):
    response = await connection.fetch(
        "SELECT event_id, event_type, target_user, payload, lamport_ts, emmited_time FROM events WHERE target_user = $1 ORDER BY lamport_ts DESC LIMIT $2",
        user_id,
        limit,
    )
    return response
