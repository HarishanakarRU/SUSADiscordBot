import sqlite3
import os

class DatabaseService:
    """
    Handles persistence for user verification states using SQLite.
    Designed to be easily swappable with a PostgreSQL driver if needed.
    """
    def __init__(self, db_path: str = "data/susa.db"):
        # Ensure the data directory exists (crucial for containerized environments like Wisp)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._initialize_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verifications (
                    user_id INTEGER PRIMARY KEY,
                    email TEXT NOT NULL,
                    first_name TEXT NOT NULL,  -- New column
                    code TEXT NOT NULL,
                    verified BOOLEAN DEFAULT FALSE
                )
            """)
            conn.commit()

    def store_pending_verification(self, user_id: int, email: str, first_name: str, code: str) -> None:
        """Stores or overwrites a pending verification code for a user."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO verifications (user_id, email, first_name, code, verified)
                VALUES (?, ?, ?, ?, FALSE)
                ON CONFLICT(user_id) DO UPDATE SET
                email=excluded.email,
                first_name=excluded.first_name,
                code=excluded.code,
                verified=FALSE
            """, (user_id, email, first_name, code))
            conn.commit()

    def check_and_verify_code(self, user_id: int, submitted_code: str) -> dict:
        """Checks the code. Returns a dict with success status and first_name if verified."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT code, first_name FROM verifications WHERE user_id = ? AND verified = FALSE", 
                (user_id,)
            )
            result = cursor.fetchone()
            
            if result and result[0] == submitted_code:
                cursor.execute(
                    "UPDATE verifications SET verified = TRUE WHERE user_id = ?", 
                    (user_id,)
                )
                conn.commit()
                return {"success": True, "first_name": result[1]}
            return {"success": False, "first_name": None}