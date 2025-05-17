import logging
import logging.config
import yaml
import os


class LogConfig:
    """
    Manages logging (python) configuration using an external YAML file 'log_setting.yaml'.
    Ensures logs are correctly formatted and written to both console and file.
    """


    log_dir = os.path.join(os.path.dirname(__file__), "..", "..", "log")
    os.makedirs(log_dir, exist_ok=True) 


    # Define absolute paths for logging file(log_setting.yaml) and log file(logOffChainApp.log)
    LOGGING_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "log_setting.yaml")
    LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "log/logOffChainApp.log")

    @staticmethod
    def setup_logger():
        """
        1-Clears the content of the log file at the start of each execution.
        2-Loads logging settings from the YAML configuration file.
        3-Configures handlers for console and file logging.
        """

        # Clear the content of the log file(logOffChainApp.log) instead of deleting it
        if os.path.exists(LogConfig.LOG_FILE_PATH):
            with open(LogConfig.LOG_FILE_PATH, "w") as file:
                file.truncate(0)  # Clear the file content

        # Verify that the logging file(log_setting.yaml) configuration file exists
        if not os.path.exists(LogConfig.LOGGING_CONFIG_PATH):
            raise FileNotFoundError(f"Logging configuration file not found: {LogConfig.LOGGING_CONFIG_PATH}")

        try:
            # Load logging file(log_setting.yaml) configuration from YAML file
            with open(LogConfig.LOGGING_CONFIG_PATH, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                if not config or "logging" not in config:
                    raise KeyError("Missing 'logging' section in log_setting.yaml or the file is empty")

                # Check if file logging file(log_setting.yaml) is enabled in the configuration
                enable_file_logging = config["logging"].get("enable_file_logging", False)

                # Define active handlers, console is always enabled
                active_handlers = ["console"]
                if enable_file_logging:
                    active_handlers.append("file")

                    # Ensure file handler overwrites the log file(logOffChainApp.log) on each execution
                    if "file" in config["logging"]["handlers"]:
                        config["logging"]["handlers"]["file"]["mode"] = "w"  # Overwrite mode

                # Apply handlers to the application logger and root logger
                config["logging"]["loggers"]["app_logger"]["handlers"] = active_handlers
                config["logging"]["root"]["handlers"] = active_handlers

                # Apply logging(log_setting.yaml) configuration
                logging.config.dictConfig(config["logging"])
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading log_setting.yaml: {str(e)}")

        # Retrieve and initialize the application logger
        logger = logging.getLogger("app_logger")
        logger.info("BackEnd: INITIAL LOADING OF GLOBAL - LOGGER")
        logger.info("BackEnd: Logger initialized successfully (File logging: " + (
            "enabled" if enable_file_logging else "disabled") + ")")
        return logger


# ===================== LOGGING CONFIGURATION =====================

# Initialize the global logger instance
logger = LogConfig.setup_logger()
