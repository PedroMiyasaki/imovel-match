
import asyncio
import duckdb
import mlflow
import re
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.agents.real_estate_agent import real_state_agent
from app.agents.guard_rail_agent import guard_rail_agent
from app.models.user_models import UserInput
from app.models.real_estate_models import RealStateAgentOutput
from app.utils.general import load_config


def escape_markdown_v2(text: str) -> str:
    """Escapes characters for Telegram's MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


mlflow.pydantic_ai.autolog()
mlflow.set_experiment("imovel-match-telegram")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Olá! Eu sou seu assistente imobiliário. Como posso te ajudar a encontrar o imóvel dos seus sonhos hoje?")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming text messages from the user."""
    user_input = update.message.text
    user_name = update.message.from_user.first_name
    
    if not user_input.strip():
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')

    message_history = context.user_data.get("message_history", [])
    
    try:
        guard_rail_response = await guard_rail_agent.ainvoke({"input": user_input, "history": message_history})
        if guard_rail_response.rules_are_being_broken:
            await update.message.reply_text("Desculpe, só posso ajudar com questões relacionadas a imóveis.")
            return
            
        agent_run = await real_state_agent.run(
            user_input, 
            deps=UserInput(connection=context.bot_data["db_connection"], user_name=user_name), 
            message_history=message_history
        )
        message_history.extend(agent_run.new_messages())
        context.user_data["message_history"] = message_history

        output: RealStateAgentOutput = agent_run.output
        
        message_parts = []
        
        if output.response:
            message_parts.append(escape_markdown_v2(output.response))

        if output.properties and output.properties != context.user_data.get("last_shown_properties"):
            message_parts.append("\n\n*Imóveis encontrados:*\n")
            message_parts.append(f"```\n{output.properties}\n```")
            context.user_data["last_shown_properties"] = output.properties

        if output.slots and output.slots != context.user_data.get("last_shown_slots"):
            message_parts.append("\n\n*Horários disponíveis:*\n")
            message_parts.append(f"```\n{output.slots}\n```")
            context.user_data["last_shown_slots"] = output.slots
            
        final_message = "".join(message_parts).strip()

        if final_message:
            await update.message.reply_text(final_message, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await update.message.reply_text("Não obtive uma resposta. Por favor, tente novamente.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
        await update.message.reply_text("Ocorreu um erro ao processar sua solicitação. Por favor, tente novamente mais tarde.")


async def main() -> None:
    """Starts the Telegram bot."""
    config = await load_config("config/config.yml")
    telegram_config = config.get("telegram", {})
    bot_token = telegram_config.get("bot_token")

    if not bot_token:
        print("Telegram bot token not found in config.yml")
        return

    application = Application.builder().token(bot_token).build()
    
    application.bot_data["db_connection"] = duckdb.connect(config["database"])

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Telegram bot is running...")
    
    try:
        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        # Keep the bot running until interrupted
        while True:
            await asyncio.sleep(3600) # Sleep for a long time
    finally:
        if application.updater.is_running():
            await application.updater.stop()
        if application.running:
            await application.stop()
        await application.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by the user") 