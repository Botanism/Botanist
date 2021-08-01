use crate::utils::*;
use chrono::offset::Utc;
use serenity::framework::standard::{
    macros::{command, group},
    ArgError, Args, CommandResult,
};
use serenity::futures::StreamExt;
use serenity::model::prelude::*;
use serenity::model::user::OnlineStatus;
use serenity::prelude::*;
use serenity::utils::Parse;
use std::collections::HashMap;
use std::fmt::Display;
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::info;
#[group]
#[commands(ping, provoke_error, clear, status)]
struct Misc;

#[command]
// Limit command usage to guilds.
#[only_in(guilds)]
async fn ping(ctx: &Context, msg: &Message) -> CommandResult {
    msg.channel_id.say(&ctx.http, "Pong!").await?;

    Ok(())
}

#[command]
async fn provoke_error(ctx: &Context, msg: &Message) -> CommandResult {
    report_error(
        ctx,
        &msg.channel_id,
        &BotError::new(
            "the dev is dumb",
            Some(BotErrorKind::EnvironmentError),
            Some(&msg),
        ),
    )
    .await;
    Ok(())
}

#[command]
#[aliases(clean)]
#[min_args(1)]
async fn clear(ctx: &Context, msg: &Message, mut args: Args) -> CommandResult {
    //upper limit?
    let number = match args.parse::<u64>() {
        Ok(number) => {
            args.advance();
            Some(number)
        }
        Err(err) => match err {
            //no upper limit or the number was not correctly formed
            ArgError::Parse(_) => None,
            ArgError::Eos => {
                //since we have `#[min_args(1)]`
                unreachable!()
            }
            _ => unreachable!(),
        },
    };

    //deletion with only an upper limit
    /*if number.is_some() && args.remaining() == 0 {
        return Ok(bulk_delete(ctx, &msg.channel_id, {
            let mut limit = number.unwrap();
            let mut messages = Vec::with_capacity(limit as usize);
            while limit > 0 {
                let chunk = 100.min(limit);
                limit -= chunk;
                messages.append(
                    &mut msg
                        .channel_id
                        .messages(ctx, |history| history.limit(chunk))
                        .await?,
                )
            }
            messages
        })
        .await?);
    }*/

    //duration criteria?
    let since = if args.remaining() > 0 {
        match parse_duration(args.current().unwrap()) {
            Ok(duration) => {
                args.advance();
                Some(duration)
            }
            //not having a duration by now doesn't mean the inputed arguments were wrong
            //there can still be a combination of amount & members
            Err(_err) => None,
        }
    } else {
        None
    };

    //member criteria?
    let mut members: Vec<UserId> = Vec::with_capacity(args.remaining());
    while args.remaining() > 0 {
        members.push(
            match Parse::parse(ctx, msg, args.current().unwrap()).await {
                Ok(m) => m,
                Err(parse_err) => {
                    report_error(
                        ctx,
                        &msg.channel_id,
                        &BotError::new(
                            format!(
                                "{:#} cannot be understood as a member of this server.",
                                args.current().unwrap()
                            )
                            .as_str(),
                            Some(BotErrorKind::ModelParsingError),
                            Some(msg),
                        ),
                    )
                    .await;
                    info!("Couldn't correclty parse {:?}", args.raw());
                    return Err(From::from(BotanistError::SerenityUserIdParseError(
                        parse_err,
                    )));
                }
            },
        );
        args.advance();
    }

    //argument parsing is done -> we select the messages to be deleted
    let mut messages: Vec<Message> = Vec::new();
    let mut history = msg.channel_id.messages_iter(ctx).boxed();
    let mut limit = if let Some(amount) = number {
        if !members.is_empty() && !members.contains(&msg.author.id) {
            amount
        } else {
            amount + 1
        }
    } else {
        u64::MAX
    };
    let time_cap = if let Some(dur) = since {
        Some(
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("time went backward")
                - dur,
        )
    } else {
        None
    };

    while let Some(message_result) = history.next().await {
        match message_result {
            Ok(message) => {
                if limit <= 0 {
                    break;
                }
                if !members.is_empty() && !members.contains(&message.author.id) {
                    continue;
                }
                if time_cap.is_some() {
                    //I don't think we could have negative values for the timestamp here
                    if (message.timestamp.timestamp() as u64) < time_cap.unwrap().as_secs() {
                        break;
                    }
                }
                if Utc::now()
                    .signed_duration_since(message.timestamp)
                    .num_seconds()
                    >= TWO_WEEKS
                {
                    dbg!("the message was over two weeks old so we manually delete it");
                    if let Err(err) = message.delete(ctx).await {
                        report_error(
                            ctx,
                            &msg.channel_id,
                            &BotError::new(
                                "Missing permissions to delete messages in this channel",
                                Some(BotErrorKind::MissingPermissions),
                                Some(&msg),
                            ),
                        )
                        .await;
                        info!(
                            "missing permissions to delete messages in {:?}",
                            &msg.channel_id
                        );
                        info!("{}", err);
                        return Err(From::from(err));
                    };
                } else {
                    messages.push(message);
                }

                limit -= 1;
            }
            Err(_) => (),
        }
    }

    info!("trying to delete {:?} messages", messages.len());
    match bulk_delete(ctx, &msg.channel_id, messages).await {
        Ok(_) => return Ok(()),
        Err(err) => {
            report_error(
                ctx,
                &msg.channel_id,
                &BotError::new(
                    "Missing permissions to delete messages in this channel",
                    Some(BotErrorKind::MissingPermissions),
                    Some(&msg),
                ),
            )
            .await;
            info!(
                "missing permissions to delete messages in {:?}",
                &msg.channel_id
            );
            info!("{:?}", err);
            return Err(From::from(BotanistError::Serenity(err)));
        }
    };
}

//bulks deletes messages, even if there are more than 100
//because of this the only possible error is missing permissions to delete the msgs
async fn bulk_delete(
    ctx: &Context,
    chan: &ChannelId,
    messages: Vec<Message>,
) -> Result<(), SerenityError> {
    if messages.is_empty() {
        return Ok(());
    } else {
        for chunk in messages.chunks(100) {
            chan.delete_messages(ctx, chunk).await?;
        }
    }

    Ok(())
}

struct MembersStatus {
    online: usize,
    dnd: usize,
    idle: usize,
    offline: usize,
}

impl MembersStatus {
    fn new(online: usize, dnd: usize, idle: usize, offline: usize) -> MembersStatus {
        MembersStatus {
            online,
            dnd,
            idle,
            offline,
        }
    }
}

impl Display for MembersStatus {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        let max = self.online.max(self.dnd.max(self.idle.max(self.offline)));
        write!(f, "**{:<width$}**🟢 online\n", self.online, width = max)?;
        write!(f, "**{:<width$}**🟠 idle \n", self.idle, width = max)?;
        write!(f, "**{:<width$}**🔴 dnd\n", self.dnd, width = max)?;
        write!(f, "**{:<width$}**⚪ offline\n", self.offline, width = max)
    }
}

impl From<&HashMap<UserId, Presence>> for MembersStatus {
    fn from(map: &HashMap<UserId, Presence>) -> Self {
        let mut online = 0;
        let mut idle = 0;
        let mut dnd = 0;
        let mut offline = 0;
        dbg!(&map);
        for (_, presence) in map.iter() {
            match presence.status {
                OnlineStatus::Online => online += 1,
                OnlineStatus::Idle => idle += 1,
                OnlineStatus::DoNotDisturb => dnd += 1,
                OnlineStatus::Offline => offline += 1,
                OnlineStatus::Invisible => offline += 1,
                _ => (), //discord may add new statuses without notice
            }
        }
        MembersStatus::new(online, dnd, idle, offline)
    }
}

#[command]
#[only_in(guilds)]
async fn status(ctx: &Context, msg: &Message) -> CommandResult {
    let guild = msg.guild(ctx).await.expect("missing guild in cache");
    let owned_name = guild.owner_id.to_user(ctx).await.unwrap();
    //we deduce the age of the guild through its id (snowflake)
    let creation_date = guild.id.created_at();
    let mut roles = String::new();
    for (role_id, _) in &guild.roles {
        roles.push_str(role_id.mention().to_string().as_str())
    }
    let members = MembersStatus::from(&guild.presences);
    msg.channel_id
        .send_message(ctx, |m| {
            m.embed(|e| {
                e.color(7506394).description(format!(
                    "{:#} is owned by {:#} and was created on {:#}. Since then {:#} members joined.",
                    guild.name, owned_name, creation_date, guild.member_count
                )).field("Roles", roles, true).field("Members", members, true); if let Some(url) = guild.icon_url(){e.thumbnail(url);};
                 e
            })
        })
        .await?;
    Ok(())
}
