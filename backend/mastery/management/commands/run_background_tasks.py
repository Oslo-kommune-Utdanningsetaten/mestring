from django.core.management.base import BaseCommand
from mastery.data_import.run_background_tasks import BackgroundTaskRunner
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs the background task dispatcher until interrupted"

    def add_arguments(self, parser):
        parser.add_argument(
            "--once",
            action="store_true",
            help="Run a single iteration and exit",
        )

    def handle(self, *args, **options):
        runner = BackgroundTaskRunner()
        if options.get("once"):
            logger.info("Running single background task iteration...")
            try:
                runner.run_once()
            finally:
                logger.info("Single iteration finished.")
            return

        try:
            logger.info("Starting background task runner...")
            runner.run_forever()
        except KeyboardInterrupt:
            logger.info("Interrupt detected, shutting down background task runner...")
            runner.shutdown()
        finally:
            logger.info("Background task runner stopped.")
