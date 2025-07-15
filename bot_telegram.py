import asyncio
import schedule
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
from classes.Database import Database
from main import scrap_and_insert_new_product, track_all_products

# Estados para ConversationHandler
ASK_NEW_URL, ASK_DELETE_URL = range(2)

db = Database()

# --- Handlers de comandos ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy el bot de PriceTracker 🛒\n"
        "Conmigo podés seguir el precio de tus productos favoritos en MercadoLibre.\n"
        "Usá /help para ver los comandos disponibles."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 *Comandos disponibles:*\n"
        "/newproduct - Ingresar una URL (MercadoLibre) para trackear\n"
        "/productlist - Ver lista de productos trackeados\n"
        "/deleteproduct - Eliminar un producto ingresando su URL\n"
        "/updateallproducts - Actualizar precios de todos los productos\n"
        "/help - Mostrar esta ayuda",
        parse_mode="Markdown"
    )

async def newproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📎 Enviá la URL del producto que querés agregar:")
    return ASK_NEW_URL

async def recibir_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    success = scrap_and_insert_new_product(url)
    if success:
        await update.message.reply_text(f"✅ Producto agregado con éxito:\n{url}")
    else:
        await update.message.reply_text("⚠️ No se pudo agregar el producto (¿ya está registrado?).")
    return ConversationHandler.END

async def deleteproduct(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🗑 Enviá la URL del producto que querés eliminar:")
    return ASK_DELETE_URL

async def recibir_url_eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    success = db.delete_product(url)
    if success:
        await update.message.reply_text(f"🗑 Producto eliminado:\n{url}")
    else:
        await update.message.reply_text("❌ No se encontró el producto con esa URL.")
    return ConversationHandler.END

async def productlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    productos = db.fetch_all_products()
    if not productos:
        await update.message.reply_text("No hay productos registrados.")
        return

    msg = "📦 *Lista de productos trackeados:*\n\n"
    for p in productos:
        prod = dict(p)
        msg += (
            f"🔗 [{prod['title']}]({prod['url']})\n"
            f"💰 Precio actual: ${prod['current_price']:.2f}\n"
            f"🏷 Mejor precio: ${prod['best_price']:.2f}\n\n"
        )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def updateallproducts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    success = track_all_products()
    if success:
        await update.message.reply_text("✅ Todos los productos han sido actualizados.")
    else:
        await update.message.reply_text("⚠️ Ocurrió un error al actualizar los productos.")

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Operación cancelada.")
    return ConversationHandler.END

# --- Tarea programada diaria ---
def principal_task():
    track_all_products(True)

async def scheduler_loop():
    print("📅 TAREA PROGRAMADA: Actualización diaria a las 21 07 (hora local)")
    schedule.every().day.at("21:09").do(principal_task)
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

# --- Main ---
async def main():
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    # Configurar handlers
    conv_new = ConversationHandler(
        entry_points=[CommandHandler("newproduct", newproduct)],
        states={ASK_NEW_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_url)]},
        fallbacks=[CommandHandler("cancel", cancelar)],
    )
    conv_delete = ConversationHandler(
        entry_points=[CommandHandler("deleteproduct", deleteproduct)],
        states={ASK_DELETE_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, recibir_url_eliminar)]},
        fallbacks=[CommandHandler("cancel", cancelar)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("productlist", productlist))
    app.add_handler(CommandHandler("updateallproducts", updateallproducts))
    app.add_handler(conv_new)
    app.add_handler(conv_delete)

    # Inicializar y correr bot + scheduler en paralelo
    await app.initialize()
    await app.start()
    await asyncio.gather(
        app.updater.start_polling(),
        scheduler_loop()
    )
    await app.stop()
    await app.shutdown()

# Ejecutar
if __name__ == '__main__':
    asyncio.run(main())
