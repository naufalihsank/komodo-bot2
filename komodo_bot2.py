import requests
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext

TOKEN = os.getenv("BOT_TOKEN")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
CHAT_ID = os.getenv("CHAT_ID")


async def reply(update: Update, context: CallbackContext):
    message_text = update.message.text  # Ambil teks dari pesan pengguna

    if "SC_ORDER" in message_text:
        order_code = message_text.split("SC_ORDER")[1].strip()
        print("order code: ", order_code)
        await get_status(order_code)


def escape_markdown_v2(text):
    """
    Melakukan escape karakter spesial MarkdownV2 agar tidak menyebabkan error dalam pesan Telegram.
    """
    special_chars = r"\_[]()~`>#+-=|{}.!"
    return "".join(f"\\{char}" if char in special_chars else char for char in text)


async def send_msg(text):
    """Mengirim pesan ke chat ID tertentu dengan MarkdownV2 escape yang lebih aman."""

    safe_text = escape_markdown_v2(text)

    parameters = {
        "chat_id": CHAT_ID,
        "text": safe_text,
        "parse_mode": "MarkdownV2",  # Gunakan MarkdownV2 untuk menghindari error
    }

    try:
        response = requests.get(BASE_URL, params=parameters)
        response.raise_for_status()  # Deteksi error HTTP
        # print(response.json())  # Lihat response dari Telegram
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")  # Cetak error untuk debugging


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
        print("=" * 60)

        # if data:  # Check if data is not None or an empty dictionary
        #     await send_msg("Data tidak kosong")
        # else:
        #     await send_msg("Data kosong")

        output = f"""
*SC ORDER*      : {order_code}
*WORKORDER*     : {data.get('c_wonum', 'N/A')}
*COSTUMER NAME* : {data.get('c_customer_name', 'N/A')}
*PRODUCT NAME*  : {data.get('c_productname', 'N/A')}
*DESKRIPSI*     : {data.get('c_description', 'N/A')}
*DATE MODIFIED* : {data.get('datemodified', 'N/A')}
*ORDER TYPE*    : {data.get('c_crmordertype', 'N/A')}
*STATUS*        : {data.get('c_status', 'N/A')}
*OWNER GROUP*   : {data.get('c_ownergroup', 'N/A')}
*WORK ZONE*     : {data.get('c_workzone', 'N/A')}
*REGIONAL*      : {data.get('c_siteid', 'N/A')}
"""
        # print(output)
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
