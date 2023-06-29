from pyrogram import Client , filters
from pyrogram.types import InlineKeyboardMarkup , InlineKeyboardButton
import asyncio
import config
import os

dev = 111111 #devoloper telegram chat id
admin = 11111 #admin telegram chat id

from db_helper import DBHelper

db = DBHelper()

in_process = []


import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
LOGGER = logging.getLogger(__name__)

import  text_helper
app = Client(config.bot_name,api_id=config.api_id,api_hash=config.api_hash,bot_token=config.token)



async def membership(user_id):
    try :
        for chat_id in config.channel_ads :
            status = await app.get_chat_member(chat_id,user_id)
            if str(status.status) not in ['ChatMemberStatus.OWNER','ChatMemberStatus.ADMINISTRATOR','ChatMemberStatus.MEMBER'] :
                return False
        return True
    except Exception as e:
        # await app.send_message(dev,str(e))
        return False

async def check_file_name(file_name,file_date,mim_type):
    new_file_name = file_name
    new_file_date = 'video_' + str(file_date)
    try :
        if file_name == 'false':
            if ' ' in new_file_date :
                new_file_date = new_file_date.replace(' ','ـ')
            else :
                return new_file_date+'.'+mim_type
            return new_file_date+'.'+mim_type
        else :
            if ' ' in file_name :
                new_file_name = new_file_name.replace(' ','ـ')
            elif '💥' in file_name :
                new_file_name = new_file_name.replace('💥','ـ')
            if '"' in file_name :
                new_file_name = new_file_name.replace('"','ـ')
            else :
                return new_file_name
            return new_file_name
    except Exception as e :
        await app.send_message(dev, f'Error in check_file_name : {str(e)}')



async def get_file_name(message):
    chat_id = message.chat.id
    file_name = 'None'
    try:
        if message.video:
            if str(message.video.file_name) == 'None':
                file_name = await check_file_name('false',message.video.file_unique_id,message.video.mime_type.split('/')[1])
                return file_name
            else  :
                file_name = await check_file_name(message.video.file_name,message.video.file_unique_id,'false')
                return file_name
        if message.audio:
            file_name = await check_file_name(message.audio.file_name,'false','false')
        if message.document:
            file_name = await check_file_name(message.document.file_name,'false','false')
        return file_name
    except Exception as e :
        await app.send_message(dev,f'Error in get_file_name : {str(e)}')


async def media_downloader(message,chat_id , logid, msg_id):
    file_name = await get_file_name(message)
    file_type = 'Video' if message.video else 'Document' if message.document else 'Audio'
    file_size = message.video.file_size / (1024*1024) if message.video else message.document.file_size / (1024*1024) if message.document else message.audio.file_size / (1024*1024)
    try:
        await app.edit_message_text(
            chat_id,
            logid,
            text_helper.media_info.format(
                file_name,
                file_type,
                '{0:0.1f}'.format(file_size),
                'Downloading From TG Servers ...'
            )
        )
        await app.download_media(message , config.path+file_name)
        #os.popen(f'chmod 655 {config.path}{file_name}')
        await app.send_message(
            chat_id,
            text_helper.direct_link.format(config.domain,file_name,'90',config.bot_name),
            reply_to_message_id = msg_id
        )
        await app.edit_message_text(
            chat_id,
            logid,
            text_helper.media_info.format(
                file_name,
                file_type,
                '{0:0.1f}'.format(file_size),
                'Success 🟢'
            )
        )
        in_process.remove(chat_id)
    except Exception as e :
        in_process.remove(chat_id)
        await app.edit_message_text(
            chat_id,
            logid,
            text_helper.media_info.format(
                file_name,
                file_type,
                '{0:0.1f}'.format(file_size),
                'Unsuccess 🔴'
            )
        )
        await app.send_message(dev,str(e))
        
@app.on_message()
async def message_handler(_,message):
    chat_id = message.chat.id
    msgid = message.id

    if message.text :
        msg = message.text
        if msg == '/start':
            await app.send_message(chat_id,text_helper.start_text.format(message.from_user.mention),reply_to_message_id=msgid)
            db.AddNewUser(chat_id)
        elif msg == '/id' :
            await app.send_message(chat_id,f'Your ID : {chat_id}',reply_to_message_id=msgid)
        elif msg == '/rs' and chat_id in [dev,admin]:
            await app.send_message(chat_id,f'Number of members : {db.NumberOfUsers()}',reply_to_message_id=msgid)
        elif msg == 'check':
            await membership(chat_id)
        elif msg.startswith('ban') and chat_id in [dev,admin]:
            _ , user_id = msg.split(' ')
            db.Ban(user_id)
            await app.send_message(
                chat_id,
                f' user {user_id} Banned  ',
                reply_to_message_id=msgid
            )
        elif msg.startswith('unban'):
            _ , user_id = msg.split(' ')
            db.Unban(user_id)
            await app.send_message(
                chat_id,
                f'User {user_id} Unbaned ',
                reply_to_message_id=msgid
            )
        
    elif message.video or message.document or message.audio :
        if db.BanStatus(chat_id) == 1 :
            await app.send_message(
                chat_id,
                "You don't allow to use this bot"
            )
            return
        if not await membership(chat_id):
            await app.send_message(chat_id,text_helper.join_text)
            return
        if chat_id in in_process :
            await app.send_message(chat_id,'Please wait until your previous process complete.')
            return
        
        file_name = await get_file_name(message)
        file_type = 'Video' if message.video else 'Document' if message.document else 'Audio'
        file_size = message.video.file_size / (1024*1024) if message.video else message.document.file_size / (1024*1024) if message.document else message.audio.file_size / (1024*1024)

        await app.send_message(
            chat_id,
            text_helper.media_info.format(
                file_name,
                file_type,
                '{0:0.1f}'.format(file_size),
                'Waiting For User ...'
            ),
            reply_markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text='Cancel 🔴',callback_data='Cancel'),
                        InlineKeyboardButton(text=' Get Link 🔗',callback_data='DL')
                    ]
                ]
            ),
            reply_to_message_id = msgid


        )


@app.on_callback_query()
async def callback_handler(_,callback_query):
    query = callback_query.data
    chat_id = callback_query.message.chat.id
    if query == 'DL':
        if chat_id in in_process :
            await app.send_message(chat_id,'Please wait until your previous process complete.')
            return
        file = callback_query.message.reply_to_message
        in_process.append(chat_id)
        asyncio.create_task(media_downloader(file,chat_id,callback_query.message.id,callback_query.message.reply_to_message.id))
    elif query == 'Cancel':
        await app.delete_messages(
            chat_id,
            callback_query.message.id
        )
        await callback_query.answer('Operation Canceled')
db.setup()
app.run()