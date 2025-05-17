import os
import yaml
from configuration.log_load_setting import logger


class DatabaseForYamlLoadOfSetting:
    """
    Handles loading configurations from 'db_setting.yaml'.
    Ensures proper path resolution for cross-platform compatibility.
    """

    # Define the absolute path to the setting files
    DATABASE_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "db_setting.yaml")

    @staticmethod
    def load_config():
        """
        Reads and loads a YAML configuration file.
        """
        if not os.path.exists(DatabaseForYamlLoadOfSetting.DATABASE_CONFIG_PATH):
            logger.error(f"Configuration file 'yaml' not found: {DatabaseForYamlLoadOfSetting.DATABASE_CONFIG_PATH}")
            raise FileNotFoundError(f"Missing configuration file: {DatabaseForYamlLoadOfSetting.DATABASE_CONFIG_PATH}")

        try:
            with open(DatabaseForYamlLoadOfSetting.DATABASE_CONFIG_PATH, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            logger.error(f"Error reading YAML configuration: {e}")
            raise Exception(f"Invalid YAML configuration file: {e}")


# ===================== DATABASE CONFIGURATION =====================

# Load configuration from database setting file
configDatabase = DatabaseForYamlLoadOfSetting.load_config()

# Go up two levels from the current folder to point to `database/`
BASE_DIR_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database"))

# Build the absolute path of the database file
DATABASE_PATH = os.path.join(BASE_DIR_DB, configDatabase["database"]["path_database"])

# Check if the database file exists
#logger.info("BackEnd: INITIAL LOADING OF GLOBAL - DATABASE")
