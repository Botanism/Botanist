use crate::Context;
use poise::{
    serenity::{builder::CreateEmbed, model::prelude::*, prelude::SerenityError},
    ArgumentParseError, SlashArgError,
};
use std::fmt::Display;
use std::time::Duration;
use tracing::{debug, error, info};

///Two weeks in seconds
pub const TWO_WEEKS: i64 = 1209600;
//Error handler
//Logs the error and sends an embed error report on discord
pub async fn report_error(ctx: Context<'_>, error: BotError) -> () {
    debug!(
        "The error report {:?} was sent in {:?}",
        error,
        ctx.channel_id()
    );

    // /!\ I CURRENTLY BUILD THE EMBED TWICE BECAUSE OF A LIMITATION OF POISE
    let mut embed = CreateEmbed::default();
    embed
        .color(16720951)
        //.description()
        .title(&error.pretty_name());

    let cause_user: Option<&User> = None;

    embed.timestamp(ctx.created_at());
    //embed.url(msg.link()); currently removed because it doesn't link correctly
    let cause_user = ctx.author();
    embed.footer(|f| {
        f.text(format!("caused by {:#}", cause_user.name)).icon_url(
            cause_user
                .avatar_url()
                .unwrap_or(cause_user.default_avatar_url()),
        )
    });

    embed.field("❓ How to fix this", format!("{:#}", error), false);

    embed.field("🐛 Bug report", String::from("[GitHub](https://github.com/Botanism/Botanist/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BREPORTED+BUG%5D) | [Official Server](https://discord.gg/mpGM5cg)"), false);
    //we send the created embed in the channel where the error occured, if possible
    match ctx
        .send(|r| {
            r.embed(|e| {
                *e = embed.clone();
                e
            })
        })
        .await
    {
        Ok(_) => (),
        Err(SerenityError::Http(_)) => {
            info!(
                "couldn't report error in channel {:?} because of missing permissions",
                ctx.channel_id()
            );
            error_report_fallback(ctx, cause_user, embed).await;
        }
        Err(SerenityError::Model(ModelError::MessageTooLong(excess))) => {
            error!("CRITICAL: error embed was too long by {:?}", excess)
        }
        _ => unimplemented!(),
    }
}

//used if the bot couldn't report an error through the channel of origin
//since it's a fallback it mustn't fail, however actual delivery may fail for network error reasons
//or if the user has blocked DMs
//may one day be merged with error_report if BotError gains a dm:bool attribute
async fn error_report_fallback(ctx: Context<'_>, culprit: &User, embed: CreateEmbed) {
    //since we couldn't send the error in the channel we try to do so in DM
    match culprit
        .dm(ctx.discord(), |m| {
            m.set_embed(embed).content(format!(
                "We couldn't report the error in {:#} so we're doing it here!",
                ctx.channel_id().mention()
            ))
        })
        .await
    {
        Err(_) => error!("Fallback error reporting failed because the DM couldn't be sent"),
        Ok(_) => (),
    }
}

//occurs only with `parse_duration` when the given string cannot be parsed
#[derive(Debug)]
pub struct DurationParseError {
    pub source: String,
}
impl Display for DurationParseError {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        write!(f, "Could not parse {:#} as a duration.", self.source)
    }
}
impl std::error::Error for DurationParseError {}

impl BotError {
    pub fn pretty_name(&self) -> &'static str {
        match self {
            BotError::EnvironmentError => "Misconfigured",
            BotError::IncorrectNumberOfArgs => "Incorrect number of arguments provided",
            BotError::UnexpectedError => "UNEXPECTED",
            BotError::DurationParseError(_) => "Not a duration",
            BotError::ModelParsingError => "Unrecognized datum type",
            BotError::MissingPermissions => "Botanist lacks permissions",
            _ => "Unknown error occured!",
        }
    }
}

impl Display for BotError {
    fn fmt(&self, f: &mut core::fmt::Formatter) -> Result<(), core::fmt::Error> {
        write!(f, "{}", match self {
            BotError::EnvironmentError => "The bot was incorrectly configured by its owner. Please contact a bot administrator so that they can fix this ASAP!",
            BotError::IncorrectNumberOfArgs => "You called a command but provided an incorrect number of arguments. Consult the online documentation or type `::help <command>` to know which arguments are expected. If you think you've provided the right number of arguments make sure they are separated by a valid delimiter. For arguments containing space(s), surround them with quotes: `:: <command> \"arg with spaces\"`",
            BotError::UnexpectedError => "This error is not covered. It is either undocumented or comes from an unforseen series of events. Either way this is a bug. **Please report it!**",
            BotError::DurationParseError(_) => "A duration was expected as an argument but what you provided was invalid. The correct syntax for duations is `00d00h00m00s` where `00` stands for any valid number. As for the letters they're shorts for `day`, `hour`, `minute` and `second` respectively. They can be both lowercase and uppercase.",
            BotError::ModelParsingError => "This error occurs when a command expects a role/member/channel but something that could not be understood as such was provided. The bot uses multiple methods to interpolate the channel/role/member. You can use it's ID, mention directly, or use the name. The latter may fail if the name is ambiguous.",
            BotError::MissingPermissions => "The bot lacks the required permissions for this command in this channel. Please contact a server admin so that they can fix this. ",
            _ => "Unknown error occured!",
        })
    }
}

//Top-level error enum for the bot (which name is Botanist).
//allows us to use custom errors alongside serenity's ones
#[derive(Debug)]
pub enum BotError {
    EnvironmentError,
    IncorrectNumberOfArgs,
    UnexpectedError,
    ModelParsingError,
    MissingPermissions,
    DurationParseError(DurationParseError),
    PoiseError(Box<dyn std::error::Error + Send + Sync>),
    Serenity(SerenityError),
    SerenityUserIdParseError(poise::serenity::model::misc::UserIdParseError),
}
impl std::error::Error for BotError {}

impl From<SlashArgError> for BotError {
    fn from(err: SlashArgError) -> Self {
        BotError::PoiseError(Box::new(err))
    }
}

impl From<SerenityError> for BotError {
    fn from(err: SerenityError) -> Self {
        BotError::Serenity(err)
    }
}

//somehow this error is not part of `SerenityError`
impl From<poise::serenity::model::misc::UserIdParseError> for BotError {
    fn from(err: poise::serenity::model::misc::UserIdParseError) -> Self {
        BotError::SerenityUserIdParseError(err)
    }
}

impl From<DurationParseError> for BotError {
    fn from(err: DurationParseError) -> Self {
        BotError::DurationParseError(err)
    }
}

impl From<ArgumentParseError> for BotError {
    fn from(err: ArgumentParseError) -> Self {
        BotError::PoiseError(Box::new(err))
    }
}

///Parses a String into a duration using its own convention.
///XdYhZmAs would be parsed a duration of X days Y hours
///Z minutes and A seconds
pub fn parse_duration<S: AsRef<str>>(string: S) -> Result<Duration, DurationParseError> {
    const TIME_IDENTIFIERS: [char; 4] = ['d', 'h', 'm', 's'];
    const TIME_VALUES: [u64; 4] = [86400, 3600, 60, 1];

    let mut total: u64 = 0;

    let (mut start, mut stop): (usize, usize) = (0, 0);
    let mut value: String;
    let mut ident = 0;

    for character in string.as_ref().chars() {
        if character.is_ascii_digit() {
            stop += 1;
        } else {
            value = string.as_ref()[start..stop].to_string();
            if value.is_empty() {
                return Err(DurationParseError {
                    source: string.as_ref().to_string(),
                });
            } else {
                start = stop + 1;
                stop = start;
                total += value.parse::<u64>().unwrap() * TIME_VALUES[ident];
                value.clear();
                ident = match TIME_IDENTIFIERS
                    .iter()
                    //we currently use the char 'Z' to denote a missing lowercase version of a char.
                    //indeed if this happends it means the char is not an ASCII letter and 'Z' will fail to match
                    .position(|short| short == &character.to_lowercase().next().unwrap_or('Z'))
                {
                    Some(index) => index,
                    None => {
                        return Err(DurationParseError {
                            source: string.as_ref().to_string(),
                        })
                    }
                };
            }
        }
    }

    Ok(Duration::from_secs(total))
}

///Used in commands that must only be ran in a guild
// TODO: change the error to something more expressive
// TODO: make this into a poise check https://kangalioo.github.io/poise/master/poise/struct.ApplicationCommandOptions.html#structfield.check
#[macro_export]
macro_rules! in_guild {
    ($ctx:ident) => {
        if $ctx.guild_id().is_none() {
            Err(poise::serenity::Error::Other("not in guild"))
        } else {
            Ok(())
        }
    };
}

#[allow(unused_imports)]
pub(crate) use in_guild;
