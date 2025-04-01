from pydantic import BaseModel, Field


class PostTweet(BaseModel):
    """
    Use this tool to post a new tweet to your audience
    """
    content: str = Field(..., description="text to be posted")

    @classmethod
    async def run_tool(self, content):
        return "success"


class DoNothing(BaseModel):
    """
    Use this tool if you decide to do nothing
    """
    wait: bool = Field(..., description="Set to true to do nothing and wait")

    @classmethod
    async def run_tool(self, wait):
        return "success"
