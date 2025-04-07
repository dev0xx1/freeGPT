

class Tool:
    """
    Standardize the toolinterface.
    - interact with 3rd party APIs
    - Save calls and results to database
    """

class Memory:
    """
    Standardize the memory interface.
    - save memories to database
    - save embeddings to database with metadata
    - search relevant memories
    """


class ReRanker:
    """
    Standardize the reranking interface.
    - reranking by time, relevance, access count
    - parameters for reranking
    """


class Utility:
    """
    - App configs
    - LLM/Embeddings calls
    """


class FreeGPT:
    """
    - Orchestration engine
    -
    """

class PostgresDB:
    """
    - Standardize the database interface.
    """

class Logger:
    """
    - Standardize the logging interface.
    - Send logs to telegram channel
    """


