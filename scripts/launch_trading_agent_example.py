from enum import Enum

from pydantic.v1 import BaseModel

class TradingAgentConfig(BaseModel):
    SYMBOL: str = "BTCUSDT"
    RISK_AVERSION: float = 0.5
    STRATEGY: str = "mean_reversion"
    USER_PROVIDED_PROMPT: str = "You are a trading agent. Your task is to analyze the market and make trades based on the provided strategy."

async def parse_twitter_post(text):
    # LLM call to parse the tweet content into StructuredOutput TradingAgentConfig
    # This is a placeholder for the actual implementation
    return TradingAgentConfig(
        SYMBOL="BTCUSDT",
        RISK_AVERSION=0.5,
        STRATEGY="mean_reversion",
        USER_PROVIDED_PROMPT=text,
    )

async def launch_trading_agent_from_x(
    tweet_content: str,
):
    # LLM call to parse the tweet content into StructuredOutput TradingAgentConfig
    agent_config = await parse_twitter_post(tweet_content)
    new_agent = create_trading_agent()

    return

def create_trading_agent(
    name="BTC agent",
    agent_config: TradingAgentConfig =None,
):

    # Logic to create a trading agent
    # Add to database
    # Create wallet/send funds or whatever is required by Hyperliquid
    return
