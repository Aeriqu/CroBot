#!/usr/bin/env python3
import asyncio
import CroBot.features.sdvxin.sdvx
import CroBot.features.sdvxin.database

async def upd():
    await CroBot.features.sdvxin.database.recreate_db()
    await CroBot.features.sdvxin.sdvx.update()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(upd())

main()
