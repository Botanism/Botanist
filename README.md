<p align="center">
  <img width="512" height="512" src="https://raw.githubusercontent.com/s0lst1ce/assets/master/sunflower_logo_1.png">
</p>

# Botanist

This program is a Discord bot which is basically a mod to the real time messaging platform. It is built using discord.py API which offers full compatibility to the official Discord API.

​	This bot is a collection of several commands and suite of commands. They are regrouped under several extensions which can be loaded, updated and disabled on the fly, without ever having to take the bot off line. This allows one to stay use only the functions he wishes and keep them updated without any penalties.

## Development history

I ([@s0lst1ce](https://github.com/s0lst1ce)) started building this bot at the end of April 2019 using discord.py API. This bot was first made with the intent to make my discord server more powerful and alive. I had only created it a few days ago but I had realized that I would need additional tools to be able to fulfill all of the plans I had for this server. I had already started making a [bot](https://github.com/organic-bots/LazyFactorian) which serves as an interface to factorio's resources. I thus started building a bot that would enable me to easily manage a scalable server which would contain all of my future bots and would serve as a platform for all my creations.

​	After the very first version I got some help of a friend of mine. Together we made the bot evolve so that it could join the ranks of other servers. Indeed I had started to realize that the bot, however simple, may be useful to others.

## Contributing

If you want to contribute that would be awesome ! We would love that :smile: !

So to help you out, here are some tips to get you going: [CONTRIBUTING.md](https://github.com/s0lst1ce/ForeBot/blob/master/CONTRIBUTING.md).

## Commands

### Getting started

Here is an exhaustive list of all extensions and the commands they provide. This list is kept up to date with the latest updates. Some commands can only be ran in a server (ie: you can't have roles in a DM). They are also all case sensitive. To make you message a command it must start with the set `PREFIX`. By default this is set to `::`. This means that if you want to call the command `slaps`, you have to enter `::slaps`. The prefix is not mentioned in the following reference.

​	Those commands are sometimes regrouped under a **group**. This means that a command belonging to a **group** will only be recognized if the **group**'s name is appended before the command. For example the command `ls` of group `ext` needs to be called like this: `ext ls`.

​	To prevent abuse a **clearance** system is included with the bot. This allows servers to limit the use of certain commands to select group of members. One member can possess multiple roles (ie: levels of clearance). The implemented level of clearances are listed & described in the following table in order of magnitude:

| Clearance     | Description                                                  |
| ------------- | ------------------------------------------------------------ |
| *             | this represents the wildcard and means everyone can use the command. No matter their roles |
| runner        | this role is assigned to only one member: the one with the [`RUNNER_ID`](https://github.com/organic-bots/ForeBot/blob/master/settings.py#15). This is defined in the `settings.py` file and should represent the ID of the user responsible for the bot. It is also the only cross-server role. |
| owner         | this role is automatically assigned to every server owner. It is however server-specific. It gives this member supremacy over all members in his/her server. |
| administrator | this role gives access to all server commands except the bot configuration ones |
| manager       | this role gives access to message management, warnings issues and other server moderation commands |

​	Arguments (aka: parameters) are referenced in `<` & `>` in this reference although using those symbols isn't necessary when using the commands.  Some arguments are optional. If it's the case they are preceded by a `*`. Otherwise the command's list of required arguments is to be  like this: `<arg1>` `<arg2>`.  This can also be blank when the command doesn't require any argument.

 Sometimes commands require a `*` argument. This means that the argument length is unlimited. It can range from 0 to 2000 characters (the maximum allowed by discord).

Finally arguments which are not `*` but comprises spaces need to be put in quotes like this: `"this is one argument only"`. Else each "word" will be considered a different argument. If the argument count doesn't exactly match then the command will fail. Also the arguments order matters.





### Reference

#### Defaults

A suite of commands always activated which handle extension management. This cannot be unloaded as it is part of the core of the bot and is required for live updates.

| Group | Command  |   Arguments   |                         Description                          | Clearance |
| ----- | :------: | :-----------: | :----------------------------------------------------------: | --------- |
| `ext` |  `add`   | `<extension>` | loads the  specified `<extension>` bot extension. If the command fails the bot will continue to run without the extension. | runner    |
| `ext` |   `rm`   | `<extension>` | removes the  specified `<extension>` bot extension. If the command fails the bot will continue to run with the extension. | runner    |
| `ext` | `reload` | `<extension>` | reloads the  specified `<extension>` bot extension. If the command fails the extension will stay unloaded | runner    |
| `ext` |   `ls`   |               |  returns an embed with all the extensions and their status   | runner    |



#### Poll

This suite of commands provides automatic poll creation. A poll is an embed message sent by the bot to specified channels. Every user can react to the poll to show their opinion regarding the interrogation submitted by the poll. With each reaction, the poll's color will change to give everyone a quick visual feedback of all members' opinion. A poll is generated from a user's message. Currently it only supports messages from a `poll` channel. However it is planned to improve this to allow one to create a poll using a dedicated command. Same goes for poll editing which is yet unsupported. To palliate to this you can remove your poll if you consider it was malformed. Polls can also be deleted when reacting with the `:x:` emoji.

| Group  | Command | Arguments  |                         Description                          | Clearance |
| ------ | :-----: | :--------: | :----------------------------------------------------------: | --------- |
| `poll` |  `rm`   | `<msg_id>` | if the user is the author of the poll with the `<msg_id>` message, the bot deletes the specified poll. | *         |



#### Embedding

This extension allows any user to send a message as an embed. The color of the embed is defined by the user's role color.

| Group | Command | Arguments |                         Description                          | Clearance |
| ----- | :-----: | :-------: | :----------------------------------------------------------: | --------- |
|       | `embed` |     *     | converts all arguments which form the user's message into a new embed one. Markdown is supported, including named links | *         |



#### Bot Essentials

This extension contains some of the most basic managing commands and should almost always be enabled.


| Group |  Command   | Arguments |                         Description                          | Clearance |
| :---: | :--------: | :-------: | :----------------------------------------------------------: | :-------: |
|       |   `ping`   |           |   replies with the rounded latency of the message transfer   |     *     |
|       | `shutdown` |           |                 shuts down the bot properly                  |  runner   |
|       |  `clear`   |  `<nbr>`  | deletes the specified `<nbr>` number of messages in the current channel; chronologically |  manager  |
|       |  `status`  |           | returns some statistics and info about the server and its members |     *     |



#### Slapping

Allows moderators to give quick and light warnings to disrespectful members. By slapping a member he gets notified of his misbehavior and knows who did it. Both the administrator and the user can see his/her slap count. The slap count is also cross-server.

| Group |  Command  |      Arguments      |                         Description                          | Clearance |
| ----- | :-------: | :-----------------: | :----------------------------------------------------------: | :-------: |
|       |  `slap`   |    `<member>`, *    | slaps the specified `<member>` member one time. The other arguments will form the optional reason for the slap. |  manager  |
|       | `forgive` | `<member>` *`<nbr>` | slaps the specified `<member>` member `<nbr>` number of time(s). If `<nbr>` is unspecified, pardons the member of all his slaps. Member can be a mention, a user id or just the string of the name of the member. |  manager  |
|       |  `slaps`  |          *          | returns an embed with a list of all slapped members and their slap count. If arguments are given they must represent members or their ids/name. If so detailed info will be returned only of those members. It gives access to the slapping log. |  manager  |



#### Role 

Allows moderators to add and remove roles to members.

| Group  | Command |      Arguments       |                         Description                          |   Clearance   |
| ------ | :-----: | :------------------: | :----------------------------------------------------------: | :-----------: |
| `role` |  `add`  | `<member>` `<roles>` | adds the specified `<roles>` roles from the `<member>` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member | administrator |
| `role` |  `rm`   | `<member>` `<roles>` | removes the specified `<roles>` roles from the `<member>` member (roles mustn't be empty). Member can be a mention, a user id or just the string of the name of the member | administrator |



#### Config

Allows the owner of a server to configure the behavior of the bot.

| Group | Command |   Arguments   |                         Description                          | Clearance |
| ----- | :-----: | :-----------: | :----------------------------------------------------------: | --------- |
|       | `init`  |               | starts full configuration of the bot in a new, restricted, channel | owner     |
|       |  `chg`  | `<extension>` | **DEPRECATED**<br />starts the configuration of the `<extension>` extension. This is done in a new, restricted, channel | owner     |



#### Development

Allows the developers to update the bot and notify all server owners of the changes. It also facilitates bug fixing by providing an easy way to retrieve the log.

| Group | Command  | Arguments |                         Description                          | Clearance |
| :---: | :------: | :-------: | :----------------------------------------------------------: | --------- |
|       | `update` |     *     | sends an update message to all users who own a server of which the bot is a member. The given arguments will be transformed into the message sent to the server owners. A default message is sent if none is provided. This can be modified in `settings.py`. | owner     |
|       |  `log`   |           |                  returns the bot's log file                  | owner     |
|       |  `dev`   |           | sends the development server URL to the author of the message |           |



#### Time

Gives several time-related commands to ease organization. For now this only includes a remind function but an event planner is in the works.

| Group | Command  | Arguments |                         Description                          | Clearance |
| ----- | :------: | :-------: | :----------------------------------------------------------: | --------- |
|       | `remind` |     *     | returns the specified message after the specified amount of time. To precise the delay before sending the message use the following format: `1d 15h 6m 01s` where `d` stands for days, `h` for hours, `m` for minutes and `s` for seconds. The numbers preceding them must be integers and represent the number of units to wait for (be it days, hours, minutes or seconds). All other words given as argument will form the message's content and will be sent in PM to the user after the specified delay has elapsed. | *         |



#### Todo *In development* 

Allows moderators to make a to-do list  in one or more channels. It's also possible to make types for the to-do's, to assign a member to a to-do and to make a copy of the to-do in a public or in a other channel. If the to-do is deleted the replica will also be deleted. For all the command where arguments are split with : `;` you must respect those.

| Group  |   Command    |                          Arguments                           |                         Description                          | Clearance |
| ------ | :----------: | :----------------------------------------------------------: | :----------------------------------------------------------: | :-------: |
| `todo` |    `add`     | `<to-do_content>` `<to-do_type>;<assigned member/false>` `<repost_channel/false>` | adds the to-do in the selected channel (see `todo channel` command) . A color will be used for the embeds if the to-do type exist. The member can be mention or just wrote normally, he will be mention in both case. The channel can be a mention or can be wrote manually, he will be write as mentioned is both case. |     *     |
| `todo` | `removetype` |                        `<type_name>`                         |                       removes the type                       |     *     |
| `todo` | `listtypes`  |                        `<type_name>`                         |                      list created types                      |     *     |
| `todo` |  `addtype`   |                   `<type_name>` `<color>`                    |                  adds a type for the to-dos                  |     *     |
| `todo` |  `channel`   |                                                              |          select the channel for the future to-do's           |     *     |

