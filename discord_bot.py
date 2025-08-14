import discord

def do_menu(lst, title="Make a choice."):
    print(title + "\n")

    if len(lst) < 1:
        print("No options provided.")
        quit()

    for i in range(len(lst)):
        print(i+1, ". ", lst[i], sep="")

    print()

    while True:
        user_choice = input("Enter choice item number: ")

        try:
            user_choice = int(user_choice)
        except ValueError:
            print("Please enter an integer value.")
            continue

        if user_choice in range(1, len(lst)+1):
            user_choice = lst[user_choice-1]
            print("You chose ", user_choice, ".\n", sep="")
            return user_choice
        print("Please enter a choice in range of the options given.")

def read_kv_file(filename):
    with open(filename, 'r') as file:
        tokens_dict = {}
        for line in file:
            line = line.split("=")
            if len(line) != 2:
                print("File", filename, "is not organized in `NAME=TOKEN` lines format.")
                quit()
            tokens_dict[line[0]] = line[1]
        return tokens_dict

class DiscordBot:
    def __init__(self):
        self.choose_token()

        self.intents = discord.Intents.default()
        self.intents.guilds = True
        self.intents.message_content = True
        self.client = discord.Client(intents=self.intents)   

        # async functions
        self.message_function = None
        self.quit_function = None

    def start(self):
        self.client.run(self.token)

    def choose_token(self):
        tokens_dict = read_kv_file("tokens.txt")
        choice = do_menu(list(tokens_dict.keys()), title="Choose a bot to use.")
        self.token = tokens_dict[choice]

    async def choose_guild(self):
        guild_dict = {}

        for guild in self.client.guilds:
            guild_dict[guild.name] = guild.id

        self.guild = self.client.get_guild(guild_dict[do_menu(list(guild_dict.keys()), "Choose a channel to target.")])
        await self.choose_channel()

    async def react(self):
        msg = await self.target_message()
        reaction = input("Enter your reaction: ")
        await msg.add_reaction(reaction)
        try:
            await msg.add_reaction(reaction)
        except discord.errors.HTTPException:
            print("Invalid input.\n")

    async def custom_react(self):
        msg = await self.target_message()
        reaction = "<:" + input("Sticker name: ") + ":" + input("Sticker ID: ") + ">"
        try:
            await msg.add_reaction(reaction)
        except discord.errors.HTTPException:
            print("Invalid input.\n")

    async def target_message(self):
        limit = 10
        messages = {}
        async for msg in self.channel.history(limit=limit):
            messages[msg.author.display_name + ": " + msg.content] = msg
        return messages[do_menu(list(messages.keys()), "Choose a message to target.")]

    async def send_message(self):
        msg = input("Enter a message: ")
        if not msg:
            print("Cancelling send.")
            return
        await self.channel.send(msg)

    async def message_reply(self):
        reply_to = await self.target_message()
        content = input("Enter your reply: ")
        if not content:
            print("Cancelling send.")
            return
        await reply_to.reply(content)

    async def quit(self):
        self.online = False
        await self.client.close()
        print("Bot is offline.")
        quit()

    async def choose_action(self):
        actions = {"Send message": self.send_message, 
                   "Reply to a message": self.message_reply,
                   "React to a message": self.react,
                   "React with a sticker": self.custom_react,
                   "Change channel (" + str(self.channel.name) + ")": self.choose_channel, 
                   "Change server (" + str(self.guild.name) + ")": self.choose_guild, "Quit": self.quit}

        choice = do_menu(list(actions.keys()), "Choose an action.")

        await actions[choice]()

    async def choose_channel(self):
        channels = {}
        for channel in self.guild.channels:
            channels[channel.name] = channel.id
        self.channel = self.client.get_channel(channels[do_menu(list(channels.keys()), "Choose a channel to target.")])

bot = DiscordBot()

@bot.client.event
async def on_ready():
    print("Bot is online.")

    await bot.choose_guild()

    while True:
        await bot.choose_action()

bot.start()