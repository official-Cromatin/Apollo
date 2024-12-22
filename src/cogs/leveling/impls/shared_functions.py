import discord

class Shared_Functions:
    # General used methods
    @staticmethod
    async def edit_message(channel:discord.TextChannel | int, message_id:int, embed:discord.Embed = ..., view:discord.ui.View = ...) -> discord.Message:
        """Edits the embed and view of the message in the provided channel, returns the edited message"""
        message = channel.get_partial_message(message_id)

        # Check which values are provided
        kwargs = {}
        if embed is not ...:
            kwargs['embed'] = embed
        if view is not ...:
            kwargs['view'] = view
        return await message.edit(**kwargs)

    # Methods used to generate components for the "setup" view (setup_impl)
    @staticmethod
    def get_main_embed(channel_id:int, default_multiplier:float, minimum_threshold:int, maximum_experience:int) -> discord.Embed:
        return discord.Embed(
            title = f"Current configuration for obtaining experience in <#{channel_id}> channel",
            description = (
                "**__Configuration for this channel:__**\n"
                f"- Multiplier, being multiplied by the length of the message: `{default_multiplier}`\n"
                f"- Threshold above which the user is rewarded: `{minimum_threshold}`\n"
                f"- Limit for the maximum amount of receivable experience: `{maximum_experience}`\n"
                "-# Important: The amount of gained experience is calculated by multiplying the message length by the multiplier"
            )
        )
    
    @staticmethod
    def get_main_view() -> discord.ui.View:
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = "Configure channel", style = discord.ButtonStyle.blurple, custom_id = "lvls.main.conf"))
        view.add_item(discord.ui.Button(label = "Copy settings from channel", style = discord.ButtonStyle.blurple, custom_id = "lvls.main.copy"))
        return view
    
    @staticmethod
    async def update_main_message(channel:discord.TextChannel, message_id:int, channel_id:int, default_multiplier:float, minimum_threshold:int, maximum_experience:int):
        """Updated the provided message of the main view"""
        embed = __class__.get_main_embed(channel_id, default_multiplier, minimum_threshold, maximum_experience)
        view = __class__.get_main_view()
        message = await __class__.edit_message(channel, message_id, embed, view)
        
    # Methods used to generate components for the "configure" view (configure_impl)
    @staticmethod
    def get_configure_embed(default_multiplier:float, minimum_threshold:int, maximum_experience:int) -> discord.Embed:
        """Creates and returns the embed, embedding the provided values"""
        embed = discord.Embed(
            title = "Editing the configuration",
            description = (
                "**__Configuration for this channel:__**\n"
                f"- Multiplier, being multiplied by the length of the message: `{default_multiplier}`\n"
                f"- Threshold above which the user is rewarded: `{minimum_threshold}`\n"
                f"- Limit for the maximum amount of receivable experience: `{maximum_experience}`\n"
                "-# Important: The amount of gained experience is calculated by multiplying the message length by the multiplier"
            )
        )
        embed.set_footer(text = "Use the '/leveling configure' command to edit the values")
        return embed
    
    @staticmethod
    def get_configurate_view(default_multiplier:float, minimum_threshold:int, maximum_experience:int) -> discord.ui.View:
        """Returns the view, depending on the provided values, the "Save" Button will be disabled until all values are not None"""
        save_disabled = any(value is None for value in [default_multiplier, minimum_threshold, maximum_experience])
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label = "Save", custom_id = "lvls.conf.save", style = discord.ButtonStyle.green, disabled = save_disabled))
        view.add_item(discord.ui.Button(label = "Discard", custom_id = "lvls.conf.disc", style = discord.ButtonStyle.red))
        return view
    
    @staticmethod
    async def update_edit_message(channel:discord.TextChannel, message_id:int, default_multiplier:float, minimum_threshold:int, maximum_experience:int):
        embed = __class__.get_configure_embed(default_multiplier, minimum_threshold, maximum_experience)
        view = __class__.get_configurate_view(default_multiplier, minimum_threshold, maximum_experience)
        await __class__.edit_message(channel, message_id, embed, view)
    

async def setup(bot):
    pass
