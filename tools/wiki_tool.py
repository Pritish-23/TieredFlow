import logging
import wikipediaapi

logger = logging.getLogger(__name__)


class WikipediaTool:

    def __init__(self):
        self._wiki = wikipediaapi.Wikipedia(
            language="en",
            user_agent="TieredFlow/1.0"
        )

    def search(self, query: str) -> str:
        logger.info(f"[Wiki] Searching: {query}")

        try:
            page = self._wiki.page(query)

            if not page.exists():
                return f"No Wikipedia article found for '{query}'."

            # Return first 1000 chars of summary
            summary = page.summary
            return (
                f"Wikipedia: {page.title}\n\n"
                f"{summary}\n\n"
                f"Source: {page.fullurl}"
            )

        except Exception as e:
            logger.error(f"[Wiki] Failed: {e}")
            return f"Wikipedia search failed: {str(e)}"


# Singleton
_wiki_instance = None


def get_wiki_tool() -> WikipediaTool:
    global _wiki_instance
    if _wiki_instance is None:
        _wiki_instance = WikipediaTool()
    return _wiki_instance