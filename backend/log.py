import os
import aiosqlite
import structlog
import logging
import logging.handlers
import multiprocessing
import atexit
import asyncio
from structlog.processors import JSONRenderer, TimeStamper, CallsiteParameterAdder
from structlog.stdlib import LoggerFactory
from structlog.threadlocal import wrap_dict
from structlog.dev import ConsoleRenderer
from backend.paths import log_path, log_db_path

# Asynchronous SQLite handler
class AsyncSQLiteHandler(logging.Handler):
    def __init__(self, db_path='file:log?mode=memory&cache=shared'):
        super().__init__()
        self.db_path = db_path

    async def _initialize_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS log (
                    timestamp TEXT,
                    level TEXT,
                    message TEXT,
                    module TEXT,
                    funcName TEXT,
                    lineno INTEGER,
                    context TEXT
                )
            ''')
            await db.commit()

    async def emit(self, record):
        context = getattr(record, 'context', {})
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO log (timestamp, level, message, module, funcName, lineno, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (record.created, record.levelname, record.msg, record.module, record.funcName, record.lineno, str(context)))
            await db.commit()

# Configure structlog
structlog.configure(
    processors=[
        TimeStamper(fmt="ISO", utc=True),
        CallsiteParameterAdder(),
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        ConsoleRenderer(colors=True),  # Use colored console renderer
        JSONRenderer()
    ],
    context_class=wrap_dict(dict),
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configure standard logging
log_queue = multiprocessing.Queue(-1)

class QueueHandler(logging.Handler):
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        self.log_queue.put(record)

queue_handler = QueueHandler(log_queue)

# Configure log rotation
os.makedirs(log_path, exist_ok=True)
file_handler = logging.handlers.TimedRotatingFileHandler(
    log_path / 'system.log', when='midnight', interval=1, backupCount=7
)
file_handler.setFormatter(logging.Formatter('%(message)s'))

logging.basicConfig(level=logging.DEBUG, handlers=[
    file_handler,
    queue_handler
])

logger = structlog.get_logger()

# Add AsyncSQLiteHandler to the logging configuration
async def setup_logging():
    # Initialize the database handler
    db_handler = AsyncSQLiteHandler(db_path=log_db_path)
    await db_handler._initialize_db()

    # Add the handler to the root logger
    logging.getLogger().addHandler(db_handler)

# Worker to process log queue
async def log_worker(queue, db_path):
    handler = AsyncSQLiteHandler(db_path)
    await handler._initialize_db()
    while True:
        record = queue.get()
        if record is None:
            break
        await handler.emit(record)

# Start log worker process
def start_log_worker(db_path):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_logging())
    loop.run_until_complete(log_worker(log_queue, db_path))

if __name__ == '__main__':
    log_worker_process = multiprocessing.Process(target=start_log_worker, args=(log_db_path,))
    log_worker_process.start()

    # Clean up log worker process on exit
    def cleanup():
        log_queue.put(None)
        log_worker_process.join()

    atexit.register(cleanup)
    