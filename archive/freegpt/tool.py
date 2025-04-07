from pydantic import BaseModel, Field

class PostTweet(BaseModel):
    """
    Use this tool to post a new tweet to your audience
    """
    content: str = Field(..., description="text to be posted")

    @classmethod
    async def run_tool(self, content):
        return "success"
