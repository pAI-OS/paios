# Import necessary modules
import os
import asyncio
import aiosqlite
import structlog
import logging
from structlog.processors import JSONRenderer, TimeStamper, CallsiteParameterAdder
from structlog.stdlib import LoggerFactory
from structlog.dev import ConsoleRenderer
from backend.paths import log_path, log_db_path

# Configure structlog
structlog.configure(
    processors=[
        # If log level is too low, abort pipeline and throw away log entry.
        structlog.stdlib.filter_by_level,
        # Add the name of the logger to event dict.
        structlog.stdlib.add_logger_name,
        # Add log level to event dict.
        structlog.stdlib.add_log_level,
        # Perform %-style formatting.
        structlog.stdlib.PositionalArgumentsFormatter(),
        # Add a timestamp in ISO 8601 format.
        TimeStamper(fmt="ISO", utc=True),
        # If the "stack_info" key in the event dict is true, remove it and
        # render the current stack trace in the "stack" key.
        structlog.processors.StackInfoRenderer(),
        # If the "exc_info" key in the event dict is either true or a
        # sys.exc_info() tuple, remove "exc_info" and render the exception
        # with traceback into the "exception" key.
        structlog.processors.format_exc_info,
        # If some value is in bytes, decode it to a Unicode str.
        structlog.processors.UnicodeDecoder(),
        # Add callsite parameters.
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.MODULE,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
        ConsoleRenderer(colors=True),  # Use colored console renderer
        JSONRenderer(),
        #StructlogAsyncSQLiteHandler(db_path=log_db_path),
        # Transform event dict into `logging.Logger` method arguments.
        # "event" becomes "msg" and the rest is passed as a dict in
        # "extra". IMPORTANT: This means that the standard library MUST
        # render "extra" for the context to appear in log entries! See
        # warning below.
        structlog.stdlib.render_to_log_kwargs,
    ],
    # TODO: DeprecationWarning: `structlog.threadlocal` is deprecated, please use `structlog.contextvars` instead.
    #context_class=dict, # wrap_dict() deprecated, but contextvars are not safe for hybrid applications like our host, Starlette!
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    cache_logger_on_first_use=True,
)

# Create a logger instance
logger = structlog.get_logger()

def get_logger():
    return logger

if __name__ == "__main__":
    async def hello_world():
        await logger.awarn("Hello, World!")

    logger = get_logger()

    asyncio.run(hello_world())
