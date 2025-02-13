"""
Script to run the Scene+ monitoring system.
"""
import os
import subprocess
import time
from pathlib import Path
import yaml
from prometheus_client import start_http_server
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", "9090"))
GRAFANA_PORT = int(os.getenv("GRAFANA_PORT", "3000"))
METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))

# Paths
MONITORING_DIR = Path(__file__).parent
PROMETHEUS_CONFIG = MONITORING_DIR / "prometheus.yml"
GRAFANA_CONFIG = MONITORING_DIR / "grafana.ini"
DASHBOARDS_DIR = MONITORING_DIR / "dashboards"


def create_prometheus_config():
    """Create Prometheus configuration file."""
    config = {
        "global": {
            "scrape_interval": "15s",
            "evaluation_interval": "15s"
        },
        "scrape_configs": [
            {
                "job_name": "scene_plus",
                "static_configs": [
                    {
                        "targets": [f"localhost:{METRICS_PORT}"]
                    }
                ]
            }
        ]
    }
    
    with open(PROMETHEUS_CONFIG, "w") as f:
        yaml.dump(config, f)
    
    logger.info("Created Prometheus configuration")


def create_grafana_config():
    """Create Grafana configuration file."""
    config = f"""
[server]
http_port = {GRAFANA_PORT}

[security]
admin_user = admin
admin_password = scene_plus_admin

[auth.anonymous]
enabled = true
org_role = Viewer

[dashboards]
default_home_dashboard_path = {DASHBOARDS_DIR}/scene_plus_dashboard.json
"""
    
    with open(GRAFANA_CONFIG, "w") as f:
        f.write(config)
    
    logger.info("Created Grafana configuration")


def start_prometheus():
    """Start Prometheus server."""
    try:
        subprocess.Popen([
            "prometheus",
            f"--config.file={PROMETHEUS_CONFIG}",
            f"--web.listen-address=:{PROMETHEUS_PORT}",
            "--storage.tsdb.retention.time=15d"
        ])
        logger.info(f"Started Prometheus on port {PROMETHEUS_PORT}")
        
    except Exception as e:
        logger.error(f"Failed to start Prometheus: {e}")
        raise


def start_grafana():
    """Start Grafana server."""
    try:
        subprocess.Popen([
            "grafana-server",
            f"--config={GRAFANA_CONFIG}",
            f"--homepath={DASHBOARDS_DIR}"
        ])
        logger.info(f"Started Grafana on port {GRAFANA_PORT}")
        
    except Exception as e:
        logger.error(f"Failed to start Grafana: {e}")
        raise


def main():
    """Run the monitoring system."""
    try:
        # Create configuration files
        create_prometheus_config()
        create_grafana_config()
        
        # Start Prometheus metrics server
        start_http_server(METRICS_PORT)
        logger.info(f"Started metrics server on port {METRICS_PORT}")
        
        # Start monitoring services
        start_prometheus()
        start_grafana()
        
        # Keep the script running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down monitoring system")
        
    except Exception as e:
        logger.error(f"Error running monitoring system: {e}")
        raise


if __name__ == "__main__":
    main() 