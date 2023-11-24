# gpt
> Talk to ChatGPT in your server. Supports per-server custom prompts.

## Setup
1. Add the repo if you haven't already: `repo add teatowel-cogs https://github.com/towelsh/red-cogs`
2. Install the cog: `cog install teatowel-cogs gpt`
3. Load the cog: `load gpt`
4. Set up your API key...
   - Go to [OpenAI's developer page](https://platform.openai.com/api-keys) and create a new API key.
   - Go back to Discord and run `set api`
   - On the modal window, set the service to `openai`, and set keys and tokens to `api sk-YOURAPIKEY`

If you want to setup a custom prompt, run `setprompt <prompt>`.

## Commands
Once you have done the initial setup, server members can use the `chat <message>` command to talk to the bot, ping it in chat, or reply to one of its messages.
| **Command**        | **Description**                                                    |
|--------------------|--------------------------------------------------------------------|
| chat <message>     | Send a message to ChatGPT                                          |
| setprompt <prompt> | **[admin only]** Sets the prompt to ChatGPT for the current server |
| getprompt          | **[admin only]** Gets the prompt to ChatGPT for the current server |
