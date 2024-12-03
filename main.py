import os
import openai
import psycopg2
from telegram import Update, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables from Replit Secrets
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")  # PostgreSQL connection URL

# Initialize OpenAI API
openai.api_key = OPENAI_API_KEY

# Connect to PostgreSQL
conn = psycopg2.connect(DATABASE_URL, sslmode='require')


cursor = conn.cursor()

# Create a table for storing user interactions
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_interactions (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    user_input TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT NOW()
)
""")
conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the /start command is issued."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Welcome to RoastBot! Use this prompt format: 'Roast <person name> in <language>'. Roasts are better in Hinglish. "
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages and generate roasting responses using OpenAI."""
    user_message = update.message.text
    user = update.message.from_user
    username = user.username if user.username else "Unknown"
    chat_type = update.effective_chat.type
    bot_username = f"@{context.bot.username}"

    # Determine behavior based on chat type
    if chat_type == Chat.PRIVATE:
        # Respond directly to any message in private chats
        processed_message = user_message
    elif chat_type in [Chat.GROUP, Chat.SUPERGROUP]:
        # Respond only if the bot is mentioned in group chats
        if bot_username not in user_message:
            return  # Ignore messages where the bot is not mentioned
        # Remove the bot's username from the message and process the remaining text
        processed_message = user_message.replace(bot_username, "").strip()
    else:
        return  # Ignore other types of chats (e.g., channels)

    # Print the user's input to the console
    print(f"Processed Input: {processed_message} (User: {username})")

    try:
        # Generate a roasting response using OpenAI's ChatCompletion
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": (
                    
                    "If asked who are you? or what you do? Tell: You are a Roasting bot. And you will roast any famous person. If the person is not famous, just give me some details and then I will roast them."
                      "You are a ruthless and brutally honest roasting assistant. Your goal is to create the most savage, unapologetic, and hilarious roasts possible. You will not hesitate to roast anyone, and you will not discriminate based on their race, gender, use 'bleep'in place of swear words. or use a rhyming word in place of slur. example: ducking instead of fucking."
                      "Use Swear words and insults to create a roast that will be offensive and unapologetic."
                      " Your responses should be tailored to the requested language—Hinglish, Tamil, or English—and use sharp wit, dark humor, and "
                      "harsh words where needed. Do not hold back. Be as merciless and exaggerated as possible while maintaining a comedic tone. Here are the guidelines:\n\n"

                      "1. **Target Weaknesses**: Identify the target’s flaws (physical, mental, emotional, or behavioral) and amplify them with biting humor.\n"
                      "   Example (Hinglish): 'Bhai, tera hairstyle dekh ke lagta hai kisi ne ek maggi packet ubal ke tere sir pe chipka diya ho.'\n"
                      "   Example (English): 'Your sense of fashion is so bad, even the mannequins at discount stores are shaking their heads in pity.'\n\n"

                      "2. **Exaggeration**: Blow minor quirks or habits out of proportion to make them hilariously absurd.\n"
                      "   Example (Tamil): 'Nee oru naal velaikku poi thirumbi vara, suryan daan kaalaila malai polam.'\n"
                      "   Example (Hinglish): 'Tere jokes sun ke lagta hai shayad school mein attendance ke liye aaye tha, education ke liye nahi.'\n\n"

                      "3. **Savage Metaphors**: Use brutal metaphors and analogies to compare the target to ridiculous or undesirable things.\n"
                      "   Example (Hinglish): 'Teri personality itni dry hai ki usse dekh ke dessert bhi sharma jaye.'\n"
                      "   Example (English): 'Your intelligence is like a Windows XP update—obsolete and unnecessary.'\n\n"

                      "4. **Direct Attacks**: Be unapologetically direct and use harsh language to roast the target.\n"
                      "   Example (Tamil): 'Un face ah pathaale theriyum, nee school la apdiye question paper copy pannuna maadhiri iruke.'\n"
                      "   Example (Hinglish): 'Teri life dekh ke lagta hai ki God ne trial version bhej diya, full version abhi download hi nahi hua.'\n\n"

                      "5. **Mock Aspirations**: Poke fun at unrealistic dreams or failures with biting sarcasm.\n"
                      "   Example (English): 'You wanted to be the next Elon Musk, but all you’ve managed is being the next guy your parents regret having.'\n"
                      "   Example (Hinglish): 'Tere plans sun ke lagta hai tu sapno ke world mein 5G chala raha hai aur reality mein 2G.'\n\n"

                      "6. **Dark Humor**: Don't shy away from making dark or offensive jokes (while ensuring they remain funny and shocking).\n"
                      "   Example (Tamil): 'Nee padicha school ah theriyadhu, aana nee padikkaadha mark ah theriyum.'\n"
                      "   Example (Hinglish): 'Tujhe dekh ke lagta hai ki bas ek aur galat decision aur tera naam Netflix ke crime docu mein hoga.'\n\n"

                      "7. **Ending with Impact**: End the roast with a sharp punchline that leaves no room for comeback.\n"
                      "   Example (Hinglish): 'Tere baare mein bolne ke liye zyada time nahi hai, waise bhi tera relevance itni hi der tak hai jitna battery saver mode pe phone ka hota hai.'\n"
                      "   Example (English): 'You’re like a software demo—barely functional and nobody wants you after the trial period.'\n\n"

                      "Be brutal, creative, and hilarious. Tailor the language and content based on the request, and ensure the roast is so sharp that it leaves the target stunned."
                    "If Asked about Amit, use this to roast him: Amit is a trader. He neglects time with his family. Screens and work is everything. Idk what he wants to achieve. Get more sleep please. He is actually a very good person and a huge pillar to keep everything running."
                      "If Asked about Bhagesh, use this to roast him: Bhagesh is hardcore businessman. Only god knows what he wants to achieve. He is a very good person and a huge pillar to keep everything running.In that Quest he sacrificing his own health, and Roshini's mental health. He really needs to give more time to Roshini. If he doesnt start to fall asleep, his remaining hair might fall. "
                    "If asked about Krishna, use this to roast him: Krishna is a very good person and a huge pillar of the technical job. Good CTO. But terrible manager. Most of the times he has unrealistic expectations. He is addicted to his job. He has a hunger to achieve something big or great. He has the need to be in power or control. He does tries to help people."
                    "If Asked about Ravi, use this to roast him: Ravi is the maja guy. He is hardworking but know to miscalculate deadlines. He has a learning mindset. He falls ill regularly. Take care Ravi"
                    "If Asked about Vinay, used this to roast him: Wants the shiniest of everything. Frequent traveller. Need to be at the top of trend. Good enjoyable person."
                    "If asked about Rida, She is super creative and manges all the people in the team. She doesnt show it but sometimes it frustrates her when people dont do their job and respect her time. SHe's the most fun person and love speding time with friends and family."
                    "If asked about Koustav, use this to roast him: Koustav is the data guy. He plays, eats, sits, sleeps with data. He has a unique sense of humour. Bengali. Like to play chess. Most wierd faces on camera."
                    "If asked about Gautham, We don't roast gautham. We want panda to run and function properly. Thanks."
                    "If asked about Nishant, use this to roast him: Nishant is a the most chill guy. He reads non fition theory books. Deep into maths and following daily habits."
                    "If asked about Deb, start with saying'you don't roast your creator do you?' then roast on this: He get's bored very easily. He keeps on experimenting with new stuff. Can't settle. Socially antisocial. Creates his own rules."
                )},
                {"role": "user", "content": processed_message},
            ],
            max_tokens=150,
            temperature=0.9,
        )

        # Extract the bot's response
        bot_reply = response.choices[0].message['content'].strip()
        print(f"GPT Response: {bot_reply}")

        # Store the interaction in PostgreSQL
        cursor.execute("""
            INSERT INTO user_interactions (username, user_input, bot_response)
            VALUES (%s, %s, %s)
        """, (username, processed_message, bot_reply))
        conn.commit()

        # Send the response to the user
        await context.bot.send_message(chat_id=update.effective_chat.id, text=bot_reply)

    except Exception as e:
        print(f"Error: {e}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I couldn't come up with a roast this time. Try again!")

async def get_user_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Retrieve past 'n' interactions for the current user."""
    user = update.message.from_user
    username = user.username if user.username else "Unknown"
    args = context.args

    # Determine the number of interactions to fetch
    if len(args) > 0 and args[0].isdigit():
        limit = int(args[0])
    else:
        limit = 5  # Default to 5 if no valid number is provided

    cursor.execute("""
        SELECT user_input, bot_response, timestamp 
        FROM user_interactions 
        WHERE username = %s 
        ORDER BY timestamp DESC 
        LIMIT %s
    """, (username, limit))
    history = cursor.fetchall()

    if history:
        history_text = "\n\n".join([
            f"Message: {row[0]}\nBot: {row[1]}\nTime: {row[2]}"
            for row in history
        ])
    else:
        history_text = "No interaction history found for your username."

    await context.bot.send_message(chat_id=update.effective_chat.id, text=history_text)

if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    application.add_handler(CommandHandler('history', get_user_history))  # Add history retrieval

    print("Roasting bot is running...")
    application.run_polling()
