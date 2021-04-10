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
    channel: &Channel,
    error: &BotError<'a, 'b>,
) -> () {
    let mut embed = CreateEmbed::default();
    embed
        .color(16720951)
        .description(error.description)
        .title(match &error.kind {
            None => "UnexpectedError",
            Some(kind) => stringify!(kind),
        });

    if let Some(msg) = error.origin {
        embed.timestamp(&msg.timestamp);
        embed.url(msg.link());
        let cause_user = &msg.author;
        embed.footer(|f| {
            f.text(format!("caused by {:#}", cause_user.name)).icon_url(
                cause_user
                    .avatar_url()
                    .unwrap_or(cause_user.default_avatar_url()),
            )
        });
    };

    if let Some(kind) = &error.kind {
        embed.field("❓ How to fix this", format!("{:#}", kind), false);
    };

    embed.field("🐛 Bug report", String::from("[GitHub](https://github.com/Botanism/Botanist/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BREPORTED+BUG%5D) | [Official Server](https://discord.gg/mpGM5cg)"), false);

    channel.id().send_message(ctx, |m| m.set_embed(embed)).await;
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
}

impl Display for BotErrorKind {
    fn fmt(&self, fmt: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        match self {
            BotErrorKind::EnvironmentError => write!(fmt, "The bot was incorrectly configured by its owner. Please contact a bot administrator so that they can fix this ASAP!"),
        }
    }
}
