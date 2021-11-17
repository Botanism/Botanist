use crate::{utils::*, Context, Result};
use chrono::offset::Utc;
use poise::{
    command,
    serenity::{
        futures::StreamExt,
        model::{
            channel::Message,
            id::{ChannelId, UserId},
        },
        utils::ArgumentConvert,
    },
};
use std::time::{SystemTime, UNIX_EPOCH};
use tracing::info;

/// TODO: remove
/// this is only supposed to be used to test out error reporting
#[command(slash_command)]
pub async fn provoke_error(_ctx: Context<'_>) -> Result<()> {
    Err(BotError::EnvironmentError)
}

/// Check if the bot is online and responsive
#[command(slash_command)]
pub async fn ping(ctx: Context<'_>) -> Result<()> {
    // Limit command usage to guilds.
    in_guild!(ctx)?;

    ctx.say("Pong!").await?;

    Ok(())
}

#[command(slash_command, aliases("clean"))]
//#[min_args(1)]
/// Delete messages from the current channel
/// filters can be mixed as desired
pub async fn clear(
    ctx: Context<'_>,
    #[description = "The maximum number of messages to delete"] number: Option<u64>,
    #[description = "The maximum age of the messages to be deleted. All messages more recent than the date given that also meet the other filters will be deleted"]
    since: Option<String>,
    // TODO: find a way to support multiple users
    #[description = "Only delete messages from these members"] who: Option<UserId>,
) -> Result<()> {
    //duration criteria?
    let since = since.map(|str| parse_duration(str)).transpose()?;

    //member criteria?
    let mut members: Vec<UserId> = Vec::new();
    if let Some(member) = who {
        members.push(member)
    }
    /*while args.remaining() > 0 {
        members.push(ArgumentConvert::convert(ctx, msg, args.current().unwrap()).await?);
        args.advance();
    }*/

    //argument parsing is done -> we select the messages to be deleted
    let mut messages: Vec<Message> = Vec::new();
    let mut history = ctx.channel_id().messages_iter(ctx.discord()).boxed();
    let mut limit = if let Some(amount) = number {
        if !members.is_empty() && !members.contains(&ctx.author().id) {
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
                    message.delete(ctx.discord()).await?
                } else {
                    messages.push(message);
                }

                limit -= 1;
            }
            Err(_) => (),
        }
    }

    info!("trying to delete {:?} messages", messages.len());
    bulk_delete(ctx, &ctx.channel_id(), messages).await
}

//bulks deletes messages, even if there are more than 100
//because of this the only possible error is missing permissions to delete the msgs
async fn bulk_delete(ctx: Context<'_>, chan: &ChannelId, messages: Vec<Message>) -> Result<()> {
    if messages.is_empty() {
        return Ok(());
    } else {
        for chunk in messages.chunks(100) {
            chan.delete_messages(ctx.discord(), chunk).await?;
        }
    }

    Ok(())
}
