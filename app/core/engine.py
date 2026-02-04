"""
Core engine for dynamic-firewall.
"""
import logging
import time
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .config import Config
from .database import IPDatabase
from ..collectors import get_collector
from ..syncers import get_syncer


class Engine:
    """
    Core engine that orchestrates collectors and syncers.
    """

    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the engine.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger("engine")
        
        # Load configuration
        self.config = Config(config_path)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize database
        db_path = self.config.get('global.db_path', 'data/ips.db')
        self.db = IPDatabase(db_path)
        
        # Initialize collectors
        self.collectors = []
        self._init_collectors()
        
        # Initialize syncers
        self.syncers = []
        self._init_syncers()
        
        # Initialize scheduler
        self.scheduler = BackgroundScheduler()
        
        self.logger.info("Engine initialized successfully")

    def _setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('global.log_level', 'INFO')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def _init_collectors(self):
        """Initialize all enabled collectors."""
        collectors_config = self.config.get_collectors_config()
        
        for name, config in collectors_config.items():
            if config.get('enabled', False):
                try:
                    collector = get_collector(name, config)
                    self.collectors.append(collector)
                    self.logger.info(f"Initialized collector: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize collector {name}: {e}")

    def _init_syncers(self):
        """Initialize all enabled syncers."""
        syncers_config = self.config.get_syncers_config()
        
        for name, config in syncers_config.items():
            if config.get('enabled', False):
                try:
                    syncer = get_syncer(name, config)
                    self.syncers.append(syncer)
                    self.logger.info(f"Initialized syncer: {name}")
                except Exception as e:
                    self.logger.error(f"Failed to initialize syncer {name}: {e}")

    def collect_ips(self):
        """Collect IPs from all enabled collectors."""
        self.logger.info("=" * 60)
        self.logger.info("Starting IP collection cycle...")
        
        all_ips = []
        
        for collector in self.collectors:
            try:
                ips = collector.fetch()
                all_ips.extend(ips)
                self.logger.info(f"Collected {len(ips)} IPs from {collector.name}")
            except Exception as e:
                self.logger.error(f"Error collecting from {collector.name}: {e}")
        
        # Add IPs to database
        if all_ips:
            self.db.add_ips(all_ips)
            self.logger.info(f"Total IPs collected: {len(all_ips)}")
        else:
            self.logger.warning("No IPs collected in this cycle")
        
        # Show stats
        stats = self.db.get_stats()
        self.logger.info(f"Database stats: {stats['total_ips']} total IPs")

    def sync_firewalls(self):
        """Sync IPs to all enabled syncers."""
        self.logger.info("=" * 60)
        self.logger.info("Starting firewall sync cycle...")
        
        # Get all IPs from database
        min_score = self.config.get('global.min_score', 3)
        ips = self.db.get_all_ips(min_score=min_score)
        
        if not ips:
            self.logger.warning("No IPs to sync")
            return
        
        self.logger.info(f"Syncing {len(ips)} IPs to firewalls...")
        
        # Sync to all enabled syncers
        for syncer in self.syncers:
            try:
                success = syncer.sync(ips)
                if success:
                    self.logger.info(f"Successfully synced to {syncer.name}")
                else:
                    self.logger.error(f"Failed to sync to {syncer.name}")
            except Exception as e:
                self.logger.error(f"Error syncing to {syncer.name}: {e}")

    def run_once(self):
        """Run collection and sync once."""
        self.logger.info("Running one-time collection and sync...")
        self.collect_ips()
        self.sync_firewalls()
        self.logger.info("One-time run completed")

    def start(self):
        """Start the engine with scheduled tasks."""
        self.logger.info("Starting dynamic-firewall engine...")
        
        # Run once immediately
        self.run_once()
        
        # Schedule periodic tasks
        update_interval = self.config.get('global.update_interval', 3600)
        
        self.scheduler.add_job(
            self.collect_ips,
            trigger=IntervalTrigger(seconds=update_interval),
            id='collect_ips',
            name='Collect malicious IPs',
            replace_existing=True
        )
        
        self.scheduler.add_job(
            self.sync_firewalls,
            trigger=IntervalTrigger(seconds=update_interval),
            id='sync_firewalls',
            name='Sync to firewalls',
            replace_existing=True
        )
        
        # Start scheduler
        self.scheduler.start()
        
        self.logger.info(f"Scheduler started (interval: {update_interval}s)")
        self.logger.info("Engine is running. Press Ctrl+C to stop.")
        
        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            self.logger.info("Shutting down...")
            self.scheduler.shutdown()
            self.logger.info("Engine stopped")

    def stop(self):
        """Stop the engine."""
        self.logger.info("Stopping engine...")
        if self.scheduler.running:
            self.scheduler.shutdown()
        self.logger.info("Engine stopped")
