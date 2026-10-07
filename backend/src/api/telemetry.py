import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor

logger = logging.getLogger("azure-multimodal-compliance")


def setup_telemetry():
    """Connect the application to Azure Monitor when the existing .env value is set."""
    connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")

    if not connection_string:
        logger.warning("Azure Monitor is disabled because no connection string was found.")
        return

    try:
        configure_azure_monitor(connection_string=connection_string)
        logger.info("Azure Monitor is enabled.")
    except Exception as error:
        logger.error("Azure Monitor could not be started: %s", error)
