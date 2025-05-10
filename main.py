import asyncio
import aiohttp

BOT_TOKEN = "7689068998:AAFgiPlwVuch8S6jK9O9v6KfKjxvwjis37U"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
get_url = f"{BASE_URL}/getUpdates"

last_offset = None

async def send_req(session, req_url, params):
    async with session.post(req_url, params=params) as response:
        return await response.json()

async def main():
    global last_offset
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                params = {
                    "timeout": 50,
                    "offset": last_offset + 1 if last_offset is not None else -1
                }
                
                # Get updates
                async with session.get(get_url, params=params, timeout=60) as resp:
                    response = await resp.json()
                
                if not response.get('result'):
                    await asyncio.sleep(5)
                    continue
                
                last_offset = response['result'][-1]['update_id']

                # Process updates
                for update in response['result']:
                    message = update.get('message', {})
                    
                    # Check for member changes
                    if (message.get('new_chat_member') or message.get('new_chat_members') or
                        message.get('left_chat_member') or message.get('left_chat_participant')):
                        
                        url = f"{BASE_URL}/deleteMessage"
                        params = {
                            "chat_id": str(message['chat']['id']),
                            "message_id": str(message['message_id'])
                        }
                        
                        print('Deleting message...')
                        asyncio.create_task(send_req(session, url, params))
                        print('Delete request sent')
                
                await asyncio.sleep(1)  # Small delay between checks
            
            except aiohttp.ClientError as e:
                print(f"Network error: {e}")
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Unexpected error: {e}")
                await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())