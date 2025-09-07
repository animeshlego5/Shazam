import psycopg2

connection_string = "postgresql://postgres.nesbwlqukdinudtwpbtu:Faltu%40993@aws-1-us-east-2.pooler.supabase.com:5432/postgres"

def insert_song(title, artist):
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO songs (title, artist) VALUES (%s, %s) RETURNING song_id;",
                (title, artist)
            )
            song_id = cur.fetchone()[0]
        conn.commit()
    return song_id

def insert_fingerprints(song_id, fingerprints):
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            for hash_val, time_offset in fingerprints:
                cur.execute(
                    "INSERT INTO fingerprints (song_id, hash, time_offset) VALUES (%s, %s, %s);",
                    (int(song_id), str(hash_val), int(time_offset))
                )
        conn.commit()
    print(f"✅ Inserted {len(fingerprints)} fingerprints for Song ID {song_id}")

def get_fingerprints_for_song(song_id):
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT hash, time_offset FROM fingerprints WHERE song_id = %s;", (int(song_id),))
            results = cur.fetchall()
    return results
def match_fingerprints(query_fingerprints):
    """
    query_fingerprints: a list of (hash, time_offset)
    Returns: a dict mapping song_id to match count
    """
    import psycopg2
    from collections import defaultdict

    connection_string = "postgresql://postgres.nesbwlqukdinudtwpbtu:Faltu%40993@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
    # Extract only the hash values
    hash_values = [str(h) for h, t in query_fingerprints]
    results = defaultdict(int)

    if not hash_values:
        return results

    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            # Use SQL's ANY to match all fingerprints in one query
            cur.execute(
                """
                SELECT song_id, COUNT(*) as match_count
                FROM fingerprints
                WHERE hash = ANY(%s)
                GROUP BY song_id
                ORDER BY match_count DESC
                """,
                (hash_values,)
            )
            matches = cur.fetchall()

    # Convert results to dict: {song_id: count}
    for song_id, count in matches:
        results[song_id] = count

    return results
def get_song_info(song_id):
    import psycopg2
    connection_string = "postgresql://postgres.nesbwlqukdinudtwpbtu:Faltu%40993@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT title, artist FROM songs WHERE song_id = %s;", (int(song_id),))
            song = cur.fetchone()
    return song  # returns (title, artist)
def match_fingerprints_time_coherent(query_fingerprints):
    """
    Returns: dict mapping (song_id, delta_t) -> count of matching fingerprints
    and dict mapping song_id -> highest count for any delta_t
    """
    import psycopg2
    from collections import defaultdict

    connection_string = "postgresql://postgres.nesbwlqukdinudtwpbtu:Faltu%40993@aws-1-us-east-2.pooler.supabase.com:5432/postgres"
    # Convert to dict for faster lookup
    query_hash_to_time = {str(h): int(t) for h, t in query_fingerprints}
    results = defaultdict(lambda: defaultdict(int))  # {song_id: {delta_t: count}}

    with psycopg2.connect(connection_string) as conn:
        with conn.cursor() as cur:
            # Only query for hashes in query
            hashes = list(query_hash_to_time.keys())
            if not hashes:
                return {}, {}
            cur.execute(
                """
                SELECT song_id, hash, time_offset FROM fingerprints
                WHERE hash = ANY(%s)
                """,
                (hashes,)
            )
            for song_id, hash_val, db_time in cur.fetchall():
                q_time = query_hash_to_time[hash_val]
                delta_t = db_time - q_time
                results[song_id][delta_t] += 1

    # Find, for each song, the max count for any delta_t (strongest alignment)
    song_best_alignment = {song_id: max(delta_counts.values()) for song_id, delta_counts in results.items()}
    return results, song_best_alignment
