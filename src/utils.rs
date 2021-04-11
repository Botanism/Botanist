use serenity::{
    builder::{CreateEmbed, CreateEmbedFooter},
    framework::standard::{
        macros::{command, group},
        CommandError, DispatchError,
    },
    model::prelude::*,
    prelude::*,
};
use std::fmt::Display;
use tracing::{error, info};

//Error handler for bot
//Logs the error and sends an embed error report on discord
//if it succeeds in doing so it returns a command error that can be returned by the command which issued the
//original error. Otherwise a DispatchError is created if report_error failed
pub async fn report_error<'a, 'b>(
    ctx: &Context,
    channel: &ChannelId,
    error: &BotError<'a, 'b>,
) -> () {
    let mut embed = CreateEmbed::default();
    embed
        .color(16720951)
        .description(error.description)
        .title(match &error.kind {
            None => "UnexpectedError",
            Some(kind) => "An error occured",
        });

    let cause_user: Option<&User> = None;
    if let Some(msg) = error.origin {
        embed.timestamp(&msg.timestamp);
        //embed.url(msg.link()); currently removed because it doesn't link correctly
        let cause_user = Some(&msg.author);
        embed.footer(|f| {
            f.text(format!("caused by {:#}", cause_user.unwrap().name))
                .icon_url(
                    cause_user
                        .unwrap()
                        .avatar_url()
                        .unwrap_or(cause_user.unwrap().default_avatar_url()),
                )
        });
    };

    if let Some(kind) = &error.kind {
        embed.field("❓ How to fix this", format!("{:#}", kind), false);
    };

    embed.field("🐛 Bug report", String::from("[GitHub](https://github.com/Botanism/Botanist/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BREPORTED+BUG%5D) | [Official Server](https://discord.gg/mpGM5cg)"), false);
    //we send the created embed in the channel where the error occured, if possible
    match channel
        .send_message(ctx, |m| m.set_embed(embed.clone()))
        .await
    {
        Ok(_) => (),
        Err(SerenityError::Http(_)) => {
            info!(
                "couldn't report error in {:?} because of missing permissions",
                channel
            );
            error_report_fallback(ctx, channel, cause_user, embed).await;
        }
        Err(SerenityError::Model(ModelError::MessageTooLong(excess))) => {
            error!("CRITICAL: error embed was too long by {:?}", excess)
        }
        _ => unimplemented!(),
    }
}

//used if the bot couldn't report an error through the channel of origin
//since it's a fallback it mustn't fail, however acttuall delivery may for network error reasons
//or if the user has blocked DMs
//may one day be merged with error_report if BotError gains a dm:bool attribute
async fn error_report_fallback(
    ctx: &Context,
    chan: &ChannelId,
    culprit: Option<&User>,
    embed: CreateEmbed,
) {
    match culprit {
        None => info!("Could not determine a user that caused the issue, can't fallback to DM error reporting"),
        //since we couldn't send the error in the channel we try to do so in DM
        Some(user) => match user.dm(ctx, |m|m.set_embed(embed).content(format!("We couldn't report the error in {:#} so we're doing it here!", chan.mention()))).await {
            Err(_) => error!("Fallback error reporting failed because the DM couldn't be sent"),
            Ok(_) => (),
        }
    }
}

pub struct BotError<'a, 'b> {
    description: &'a str,
    //optionally provide additional information on this kind of error
    kind: Option<BotErrorKind>,
    //sometimes the error doesn't originate from a specific message or command -> None
    origin: Option<&'b Message>,
}

impl<'a, 'b> BotError<'a, 'b> {
    pub fn new(
        description: &'a str,
        kind: Option<BotErrorKind>,
        origin: Option<&'b Message>,
    ) -> BotError<'a, 'b> {
        BotError {
            description,
            kind,
            origin,
        }
    }
}

pub enum BotErrorKind {
    EnvironmentError,
    IncorrectNumberOfArgs,
    UnexpectedError,
}

impl Display for BotErrorKind {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        match self {
            EnvironmentError => write!(f, "The bot was incorrectly configured by its owner. Please contact a bot administrator so that they can fix this ASAP!"),
            IncorrectNumberOfArgs => write!(f, "You called a command but provided an incorrect number of arguments. Consult the online documentation or type `::help <command>` to know which arguments are expected. If you think you've provided the right number of arguments make sure they are separated by a valid delimiter. For arguments containing space(s), surround them with quotes: `:: <command> \"arg with spaces\"`"),
        }
    }
}
