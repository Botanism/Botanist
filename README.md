<p align="center">
  <img width="512" height="512" src="https://raw.githubusercontent.com/NotaSmartDev/assets/master/Balance-2-512.png">
</p>

# Forebot

This program is a Discord bot which is basically a mod to the real time messaging platform. It is built using discord.py API which offers full compatibility to the official Discord API.

This bot is a collection of several commands and suite of commands. They are regrouped under several extensions which can be loaded, updated and disabled on the fly, without ever having to take the bot off line. This allows one to stay use only the functions he wishes and keep them updated without any penalties.

## Development history

I ([@NotaSmartDev](https://github.com/NotaSmartDev)) started building this bot at the end of April 2019 using discord.py API. This bot was first made with the intent to make my discord server more powerful and alive. I had only created it a few days ago but I had realized that I would need additional tools to be able to fulfill all of the plans I had for this server. I had already started making a [bot](https://github.com/organic-bots/LazyFactorian) which serves as an interface to factorio's resources. I thus started building a bot that would enable me to easily manage a scalable server which would contain all of my future bots and would serve as a platform for all my creations.

After the very first version I got some help of a friend of mine. Together we made the bot evolve so that it could join the ranks of other servers. Indeed I had started to realize that the bot, however simple, may be useful to others.

## Commands

### Getting started

Here is an exhaustive list of all extensions and the commands they provide. This list is kept up to date with the latest updates.

Those commands are sometimes regrouped under a **group**. This means that a command belonging to a **group** will only be recognized if the **group**'s name is appended before the command. For example the command `ls` of group `ext` needs to be called like this: `ext ls`.

To prevent abuse a **clearance** system is included with the bot. This allows servers to limit the use of certain commands to select group of members. One member can possess multiple roles (ie: levels of clearance). The implemented level of clearances are listed & described in the following table in order of magnitude:

| Clearance     | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| *             | this represents the wildcard and mean everyone can use the command. No matter their roles |
| runner        | this role is assigned to only one member: the one with the `RUNNER_ID`. This is defined in the `settings.py` file and should represent the ID of the user responsible for the bot. It is also the only cross-server role. |
| owner         | this role is automatically assigned to every server owner. It is however server-specific. It gives this member supremacy over all members in his/her server. |
| administrator | this role gives access to all server commands except the bot configuration ones |
| manager       | this role gives access to message management, warnings issues and other server moderation commands |



### Reference

#### Defaults

A suite of commands always activated which handle extension management. This cannot be unloaded as it is part of the core of the bot and is required for live updates.
| Group | Command  |   Arguments   |                         Description                          | Clearance |
| ----- | :------: | :-----------: | :----------------------------------------------------------: | --------- |
| `ext` |  `add`   | `<extension>` | loads the  specified `<extension>` bot extension. If the command fails the bot will continue to run without the extension. | runner    |
| `ext` |   `rm`   | `<extension>` | removes the  specified `<extension>` bot extension. If the command fails the bot will continue to run with the extension. | runner    |
| `ext` | `reload` | `<extension>` | reloads the  specified `<extension>` bot extension. If the command fails the extension will stay unloaded | runner    |
| `ext` |   `ls`   |               | lists all *active* extensions. Enabled extensions which are not running anymore (ie: if they crashed unexpectedly) are not listed. | runner    |



#### Poll

This suite of commands provides automatic poll creation. A poll is an embed message sent by the bot to specified channels. Every user can react to the poll to show their opinion regarding the interrogation submitted by the poll. With each reaction, the poll's color will change to give everyone a quick visual feedback of all members' opinion. A poll is generated from a user's message. Currently it only supports messages from a `poll` channel. However it is planned to improve this to allow one to create a poll using a dedicated command. Same goes for poll editing which is yet unsupported. To palliate to this you can remove your poll if you consider it was malformed.

| Group  | Command | Arguments  |                         Description                          | Clearance |
| ------ | :-----: | :--------: | :----------------------------------------------------------: | --------- |
| `poll` |  `rm`   | `<msg_id>` | if the user is the author of the poll with the `<msg_id>` message, the bot deletes the specified poll. | *         |



#### Embedding

This extension allow nay user to send a message as an embed. The color of the embed is defined by the user's role color.

- `embed` `<msg>`: Deletes the message sent and transforms into an embed. The message is `<msg>` parameter which takes unlimited arguments.
| Group | Command | Arguments |                         Description                          | Clearance |
| ----- | :-----: | :-------: | :----------------------------------------------------------: | --------- |
|       | `embed` |     *     | converts all arguments which form the user's message into a new embed one. Markdown is supported, including named links | *         |



#### Bot Essentials

This extension contains some of the most basic managing commands and should almost always be enabled.


| Group |  Command   | Arguments |                         Description                          | Clearance |
| ----- | :--------: | :-------: | :----------------------------------------------------------: | --------- |
|       |   `ping`   |           |   replies with the rounded latency of the message transfer   | *         |
|       | `shutdown` |           |                 shuts down the bot properly                  | runner    |
|       |  `clear`   |  `<nbr>`  | deletes the specified `<nbr>` number of messages in the current channel; chronologically | manager   |



#### Slapping

Allows moderators to give quick and light warnings to disrespectful members. By slapping a member he gets notified of his misbehavior and knows who did it. Both the administrator and the user can see his/her slap count. The slap count is also cross-server.

| Group | Command  |     Arguments      |                         Description                          | Clearance |
| ----- | :------: | :----------------: | :----------------------------------------------------------: | --------- |
|       |  `slap`  |     `<member>`     |        slaps the specified `<member>` member one time        | manager   |
|       | `pardon` | `<member>` `<nbr>` | slaps the specified `<member>` member `<nbr>` number of time(s). If `<nbr>` is unspecified, pardons the member of all his slaps. Member can be a mention, a user id or just the string of the name of the member. | manager   |



#### Role 

Allows moderators to add and remove roles to members.

| Group  | Command |      Arguments       |                         Description                          | Clearance |
| ------ | :-----: | :------------------: | :----------------------------------------------------------: | --------- |
| `role` |  `add`  | `<member>` `<roles>` | adds the specified `<roles>` roles from the `<member>` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member | manager   |
| `role` |  `rm`   | `<member>` `<roles>` | removes the specified `<roles>` roles from the `<member>` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member | manager   |



#### Config

Allows the owner of a server to configure the behavior of the bot.

| Group | Command |   Arguments   |                         Description                          | Clearance |
| ----- | :-----: | :-----------: | :----------------------------------------------------------: | --------- |
| `cfg` | `init`  |               | starts full configuration of the bot in a new, restricted, channel | owner     |
| `cfg` |  `chg`  | `<extension>` | starts the configuration of the `<extension>` extension. This is done in a new, restricted, channel | owner     |