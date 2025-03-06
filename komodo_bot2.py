import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

TOKEN = "7901697973:AAEwYJWXs3JeAw8HbGKYmsOk9hYYuD6lGfg"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
CHAT_ID = "-1002278663540"


async def reply(update: Update, context: CallbackContext):
    message_text = update.message.text  # Ambil teks dari pesan pengguna

    if "SC_ORDER" in message_text:
        order_code = message_text.split("SC_ORDER")[1].strip()
        print("order code: ", order_code)
        await get_status(order_code)


async def send_msg(text):
    """Mengirim pesan ke chat ID tertentu."""
    parameters = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}
    response = requests.get(BASE_URL, params=parameters)
    # print(response.text)


async def get_status(order_code):
    """Mengambil status order dari API eksternal dan mengirimkan respons ke chat ID tertentu."""
    url = "https://wfm.telkom.co.id/jw/web/json/plugin/org.telkom.co.id.GetWorkorderList/service"
    body = {"filters": {"C_SCORDERNO": order_code}}

    try:
        response = requests.post(url, json=body)
        response.raise_for_status()
        workorders = response.json().get("workorders", [])
        # print("work order: ", workorders)

        if not workorders:
            msg = f"ORDER {order_code} TIDAK DITEMUKAN !!! :("
            await send_msg(msg)
            return

        # Ambil workorder terbaru
        data = sorted(
            workorders, key=lambda x: x.get("datemodified", ""), reverse=True
        )[0]

        print("last workorder: ", data)

        # if data:  # Check if data is not None or an empty dictionary
        #     await send_msg("Data tidak kosong")
        # else:
        #     await send_msg("Data kosong")

        output = f"""
*SC ORDER*      : {order_code}
*DESKRIPSI*     : {data.get('c_description', 'N/A')}
*DATE MODIFIED* : {data.get('datemodified', 'N/A')}
*STATUS*        : {data.get('c_status', 'N/A')}
*ORDER TYPE*    : {data.get('c_crmordertype', 'N/A')}
*OWNER GROUP*   : {data.get('c_ownergroup', 'N/A')}
*WORKORDER*     : {data.get('c_wonum', 'N/A')}
*REGIONAL*      : {data.get('c_siteid', 'N/A')}
"""

        await send_msg(output)

    except requests.exceptions.RequestException:
        print(f"Exception: {requests.exceptions.RequestException}")
        await send_msg("exception: ORDER TIDAK DITEMUKAN!!! :(")


def main():
    app = Application.builder().token(TOKEN).build()

    # Menambahkan handler untuk menangkap semua pesan teks
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    print("Bot sedang berjalan...")
    app.run_polling()


if __name__ == "__main__":
    main()
