import time
import logging
from Config import Config
from pyrogram import Client, filters
from sql_helpers import forceSubscribe_sql as sql
from pyrogram.types import ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, UsernameNotOccupied, ChatAdminRequired, PeerIdInvalid

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(lambda _, __, query: query.data == "onUnMuteRequest")
@Client.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
  user_id = cb.from_user.id
  chat_id = cb.message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    channel = chat_db.channel
    chat_member = client.get_chat_member(chat_id, user_id)
    if chat_member.restricted_by:
      if chat_member.restricted_by.id == (client.get_me()).id:
          try:
            client.get_chat_member(channel, user_id)
            client.unban_chat_member(chat_id, user_id)
            if cb.message.reply_to_message.from_user.id == user_id:
              cb.message.delete()
          except UserNotParticipant:
            client.answer_callback_query(cb.id, text="❗ Rejoignez la chaîne mentionnée et appuyez à nouveau sur le bouton 'Me débloquer'.", show_alert=True)
      else:
        client.answer_callback_query(cb.id, text=text="❗ Vous avez été mis en sourdine par les administrateurs pour d'autres raisons.", show_alert=True)
    else:
      if not client.get_chat_member(chat_id, (client.get_me()).id).status == 'administrator':
        client.send_message(chat_id, f"❗ **{cb.from_user.mention} essaie de se débloquer mais je ne peux pas le faire car je ne suis pas admin. Ajoutez-moi à nouveau en tant qu'admin.**\n__#Je quitte ce groupe...__")
        client.leave_chat(chat_id)
      else:
        client.answer_callback_query(cb.id, text="❗ Attention : Ne cliquez pas sur ce bouton si vous pouvez déjà parler librement.", show_alert=True)



@Client.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
  chat_id = message.chat.id
  chat_db = sql.fs_settings(chat_id)
  if chat_db:
    user_id = message.from_user.id
    if not client.get_chat_member(chat_id, user_id).status in ("administrator", "creator") and not user_id in Config.SUDO_USERS:
      channel = chat_db.channel
      try:
        client.get_chat_member(channel, user_id)
      except UserNotParticipant:
        try:
          sent_message = message.reply_text(
              "{}, vous n'êtes **pas encore abonné** à ma [chaîne](https://t.me/{}) . Veuillez la [rejoindre](https://t.me/{}) et **appuyer sur le bouton ci-dessous** pour pouvoir parler.".format(message.from_user.mention, channel, channel),
              disable_web_page_preview=True,
              reply_markup=InlineKeyboardMarkup(
                  [[InlineKeyboardButton("Me débloquer", callback_data="onUnMuteRequest")]]
              )
          )
          client.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False))
        except ChatAdminRequired:
          sent_message.edit("❗ **Je ne suis pas administrateur ici.**\n__Donnez-moi les droits de bannir des utilisateurs et ajoutez-moi à nouveau.\n#Je quitte ce groupe...__")
          client.leave_chat(chat_id)
      except ChatAdminRequired:
        client.send_message(chat_id, text=f"❗ **Je ne suis pas administrateur dans @{channel}**\n__Mettez-moi admin de la chaîne et ajoutez-moi à nouveau.\n#Je quitte ce groupe...__")
        client.leave_chat(chat_id)


@Client.on_message(filters.command(["forcesubscribe", "fsub"]) & ~filters.private)
def config(client, message):
  user = client.get_chat_member(message.chat.id, message.from_user.id)
  if user.status is "creator" or user.user.id in Config.SUDO_USERS:
    chat_id = message.chat.id
    if len(message.command) > 1:
      input_str = message.command[1]
      input_str = input_str.replace("@", "")
      if input_str.lower() in ("off", "no", "disable"):
        sql.disapprove(chat_id)
        message.reply_text("❌ **L'abonnement forcé a été désactivé avec succès.**")
      elif input_str.lower() in ('clear'):
        sent_message = message.reply_text('**Rétablissement de la parole pour tous les membres que j'ai bloqués...**')
        try:
          for chat_member in client.get_chat_members(message.chat.id, filter="restricted"):
            if chat_member.restricted_by.id == (client.get_me()).id:
                client.unban_chat_member(chat_id, chat_member.user.id)
                time.sleep(1)
          sent_message.edit('✅ **Tous les membres bloqués par le bot ont été rétablis.**')
        except ChatAdminRequired:
          sent_message.edit('❗ **I am not an admin in this chat.**\n__I can\'t unmute members because i am not an admin in this chat make me admin with ban user permission.__')
      else:
        try:
          client.get_chat_member(input_str, "me")
          sql.add_channel(chat_id, input_str)
          message.reply_text(f"✅ **Abonnement forcé activé**\n__L'abonnement forcé est activé, tous les membres du groupe doivent s'abonner à cette [chaîne](https://t.me/{input_str}) pour pouvoir envoyer des messages ici.__", disable_web_page_preview=True)
        except UserNotParticipant:
          message.reply_text(f"❗ **Pas admin dans la chaîne**\n__Je ne suis pas admin dans la [chaîne](https://t.me/{input_str}). Ajoutez-moi comme admin pour activer le ForceSubscribe.__", disable_web_page_preview=True)
        except (UsernameNotOccupied, PeerIdInvalid):
          message.reply_text(f"❗ **Nom d'utilisateur de chaîne invalide.**")
        except Exception as err:
          message.reply_text(f"❗ **ERROR:** ```{err}```")
    else:
      if sql.fs_settings(chat_id):
        message.reply_text(f"✅ **L'abonnement forcé est activé dans ce groupe.**\n__Pour cette [Chaîne](https://t.me/{sql.fs_settings(chat_id).channel})__", disable_web_page_preview=True)
      else:
        message.reply_text("❌ **L'abonnement forcé a été désactivé dans ce chat.**")
  else:
      message.reply_text("❗ **Créateur du groupe requis**\n__Vous devez être le créateur du groupe pour faire cela.__")
