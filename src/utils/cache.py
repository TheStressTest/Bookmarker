import asyncpg


class Cache:
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')

    async def single_cache(self, table, value):
        values = await self.db.fetch(f'SELECT $1 FROM {table}', value)
        print(values)

    async def double_cache(self, table, value1, value2):
        values = await self.db.fetch('SELECT $1, $2 FROM $3', value1, value2, table)
        return values
