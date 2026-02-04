"""
Database module for storing malicious IPs.
"""
import sqlite3
from typing import List, Dict, Any
from datetime import datetime
import logging


class IPDatabase:
    """
    SQLite database for managing malicious IP addresses.
    """

    def __init__(self, db_path: str = "data/ips.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.logger = logging.getLogger("database")
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create malicious_ips table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS malicious_ips (
                    ip_address TEXT PRIMARY KEY,
                    sources TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    last_seen TIMESTAMP NOT NULL,
                    created_at TIMESTAMP NOT NULL
                )
            """)
            
            # Create index for faster queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_seen 
                ON malicious_ips(last_seen)
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized at {self.db_path}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise

    def add_ips(self, ips: List[Dict[str, Any]]):
        """
        Add or update IPs in the database.
        
        Args:
            ips: List of IP dictionaries from collectors
        """
        if not ips:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for ip_data in ips:
                ip = ip_data['ip']
                source = ip_data['source']
                score = ip_data['score']
                last_seen = ip_data['last_seen']
                
                # Check if IP exists
                cursor.execute(
                    "SELECT sources, score FROM malicious_ips WHERE ip_address = ?",
                    (ip,)
                )
                result = cursor.fetchone()
                
                if result:
                    # Update existing IP
                    existing_sources = result[0]
                    existing_score = result[1]
                    
                    # Merge sources
                    sources_list = existing_sources.split(',')
                    if source not in sources_list:
                        sources_list.append(source)
                    new_sources = ','.join(sources_list)
                    
                    # Update score (take maximum)
                    new_score = max(existing_score, score)
                    
                    cursor.execute("""
                        UPDATE malicious_ips 
                        SET sources = ?, score = ?, last_seen = ?
                        WHERE ip_address = ?
                    """, (new_sources, new_score, last_seen, ip))
                    
                else:
                    # Insert new IP
                    cursor.execute("""
                        INSERT INTO malicious_ips 
                        (ip_address, sources, score, last_seen, created_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (ip, source, score, last_seen, datetime.now()))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Added/updated {len(ips)} IPs in database")
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to add IPs: {e}")

    def get_all_ips(self, min_score: int = 0) -> List[str]:
        """
        Get all IP addresses from database.
        
        Args:
            min_score: Minimum score threshold
            
        Returns:
            List of IP addresses
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT ip_address FROM malicious_ips WHERE score >= ? ORDER BY score DESC",
                (min_score,)
            )
            
            ips = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            
            self.logger.info(f"Retrieved {len(ips)} IPs from database (min_score={min_score})")
            return ips
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get IPs: {e}")
            return []

    def cleanup_old_ips(self, days: int = 30):
        """
        Remove IPs not seen in the last N days.
        
        Args:
            days: Number of days threshold
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now().timestamp() - (days * 86400)
            
            cursor.execute(
                "DELETE FROM malicious_ips WHERE last_seen < datetime(?, 'unixepoch')",
                (cutoff_date,)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned up {deleted_count} old IPs (older than {days} days)")
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to cleanup old IPs: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with stats
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total IPs
            cursor.execute("SELECT COUNT(*) FROM malicious_ips")
            total_ips = cursor.fetchone()[0]
            
            # IPs by source
            cursor.execute("""
                SELECT sources, COUNT(*) as count
                FROM malicious_ips
                GROUP BY sources
                ORDER BY count DESC
            """)
            sources = {row[0]: row[1] for row in cursor.fetchall()}
            
            conn.close()
            
            return {
                'total_ips': total_ips,
                'sources': sources
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get stats: {e}")
            return {'total_ips': 0, 'sources': {}}
