# Forebot

This program is a Discord bot which is basically a mod to the real time messaging platform. It is built using discord.py API which offers full compatibility to the official Discord API.

This bot is a collection of several commands and suite of commands. They are regrouped under several extensions which can be loaded, updated and disabled on the fly, without ever having to take the bot off line. This allows one to stay use only the functions he wishes and keep them updated without any penalties.

### Development history

[I](https://github.com/NotaSmartDev) (@NotaSmartDev) started building this bot at the end of April 2019 using discord.py API. This bot was first made with the intent to make my discord server more powerful and alive. I had only created it a few days ago but I had realized that I would need additional tools to be able to fulfill all of the plans I had for this server. I had already started making a [bot](https://github.com/organic-bots/LazyFactorian) which serves as an interface to factorio's resources. I thus started building a bot that would enable me to easily manage a scalable server which would contain all of my future bots and would serve as a platform for all my creations.

After the very first version I got some help of a friend of mine. Together we made the bot evolve so that it could join the ranks of other servers. Indeed I had started to realize that the bot, however simple, may be useful to others.

### Commands

Here is an exhaustive list of all extensions and the commands they provide. This list is kept up to date with the latest updates.

#### Poll: `poll`

This suite of commands provides automatic poll creation. A poll is an embed message sent by the bot to specified channels. Every user can react to the poll to show their opinion regarding the interrogation submitted by the poll. With each reaction, the poll's color will change to give everyone a quick visual feedback of all members' opinion. A poll is generated from a user's message. Currently it only supports messages from a `poll` channel. However it is planned to improve this to allow one to create a poll using a dedicated command. Same goes for poll editing which is yet unsupported. To palliate to this you can remove your poll if you consider it was malformed.

- `rm`  `<msg_id>`: if the user is the author of the poll with the `<msg_id>` message, the bot deletes the specified poll.



#### Embedding: 

This extension allow nay user to send a message as an embed. The color of the embed is defined by the user's role color.

- `embed` `<msg>`: Deletes the message sent and transforms into an embed. The message is `<msg>` parameter which takes unlimited arguments.



#### Bot Essentials

This extension contains some of the most basic managing commands and should almost always be enabled.

- `ping`: replies with the rounded latency of the message transfer
- `shutdown`: shuts down the bot. Restricted to the user with `RUNNER_ID`
- `clear` `<nbr>` : deletes the specified `<nbr>` number of messages in the current channel. chronogically.



#### Slapping

Allows administrators to give quick and light warnings to disrespectful members. By slapping a member he gets notified of his misbehavior and knows who did it. Both the administrator and the user can see his/her slap count. The slap count is also cross-server.

- `slap` `<member>`: slaps the specified `<member>` member one time.
- `pardon` `<member>` `<nbr>` : slaps the specified `<member>` member `<nbr>` number of time(s). If `<nbr>` is unspecified, pardons the member of all his slaps. Member can be a mention, a user id or just the string of the name of the member.



#### Role

Allows moderators to add and remove roles to members.

- `add` `<member>` `<roles>`: adds the specified `<roles>` roles from the `<member>` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member.
- `rm` `<member>` `<roles>`: removes the specified `<roles>` roles from the `<member>` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member.