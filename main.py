import httpx
import asyncio

from uuid import uuid4

class TotersScraper:
    """
    A scraper for Toters data.
    """

    def __init__(self):
        """
        Initialize the TotersScraper with default headers and base URL.
        """
        self.headers = {
            'Connection': 'keep-alive',
            'Version': '3.7.022',
            'Accept': 'application/x.toters.v1+json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Algolia-Application-Id': '2L3R97RZVD',
            'X-Algolia-API-Key': '626e721e1f9f7b21a764447203553305',
            'User-Agent': 'Toters/1 CFNetwork/1410.0.3 Darwin/22.6.0',
            'device-uuid': str(uuid4()),
            'os-version': '16.6.1'
        }
        self.base_url = 'https://2l3r97rzvd-dsn.algolia.net/1/indexes/production_stores'
        self.store_data = None

    async def fetch_store_data(self, query, num_hits=5):
        """
        Fetch store data from Algolia API based on a search query.

        Args:
            query (str): The search query.
            num_hits (int): Number of hits to retrieve (default is 5).

        Returns:
            dict: Retrieved store data.
        """
        params = {
            'query': query,
            'hitsPerPage': num_hits
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("hits"):
                self.store_data = data['hits']

    async def fetch_store_items(self, store_id):
        """
        Fetch store items for a selected store based on its ID.

        Args:
            store_id (int): The store's unique ID.

        Returns:
            dict: Retrieved store items data.
        """
        if not self.store_data:
            print('No store data found.')
            return

        selected_store = None

        for store in self.store_data:
            if store["id"] == store_id:
                selected_store = store
                break

        if not selected_store:
            print('Store not found.')
            return

        print(f'Selected Store: {selected_store["ref"]}')
        print('Fetching store items...\n')

        params = ''
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'https://api.toters-api.com/api/mobile/stores/{store_id}/additional-categories',
                params=params,
                headers=self.headers,
            )

            subcategories = response.json().get("data", {}).get("subcategories", [])
            for subcategory in subcategories:
                print(f'Category: {subcategory["ref"]}')
                items = subcategory.get("items", [])
                if not items:
                    print('No items available in this category.')
                for item in items:
                    print(f'  Item: {item["ref"]}')
                    print(f'  Description: {item["description"]}')
                    print(f'  Image: {item["image"]}')
                    print(f'  Unit Price: {item["unit_price"]}')
                    print(f'  Is Popular: {item["is_popular"]}')
                    print(f'  Is Available: {item["is_available"]}')
                    print('\n')

    async def display_data(self, query, num_hits=5):
        """
        Display store data and allow the user to select a store for item retrieval.

        Args:
            query (str): The search query.
            num_hits (int): Number of hits to display (default is 5).
        """
        await self.fetch_store_data(query, num_hits)
        if not self.store_data:
            return

        print(f'Total Stores Found: {len(self.store_data)}')
        print('Stores:')
        for index, store in enumerate(self.store_data, start=1):
            print(f'{index}. {store["ref"]}')
        
        while True:
            try:
                store_choice = int(input('\nChoose a store (enter the number): '))
                if 1 <= store_choice <= len(self.store_data):
                    await self.fetch_store_items(self.store_data[store_choice - 1]["id"])
                    break
                else:
                    print('Invalid choice. Please enter a valid number.')
            except ValueError:
                print('Invalid input. Please enter a valid number.')

if __name__ == "__main__":
    scraper = TotersScraper()
    query = input('Enter your search query: ')
    num_hits = int(input('Enter the number of hits to display: '))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(scraper.display_data(query, num_hits))
