CREATE TABLE
  IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    event_id TEXT UNIQUE NOT NULL,
    event_type TEXT NOT NULL,
    target_user TEXT NOT NULL,
    payload TEXT,
    lamport_ts BIGINT NOT NULL,
    emmited_time TIMESTAMP NOT NULL,
    receive_time TIMESTAMP DEFAULT NOW ()
  );

CREATE INDEX IF NOT EXISTS id_events_target_user ON events (target_user);

CREATE TABLE
  IF NOT EXISTS processed_events (
    event_id TEXT PRIMARY KEY,
    processed_time TIMESTAMP DEFAULT NOW ()
  );