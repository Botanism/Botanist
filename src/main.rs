mod commands;
mod utils;

use db_adapter::guild::{GuildConfig, GuildConfigBuilder};
use db_adapter::{establish_connection, PgPool};
use poise::PrefixFrameworkOptions;

use std::{collections::HashSet, env};

use crate::utils::*;
use poise::{
    serenity::{
        async_trait,
        http::Http,
        model::{event::ResumedEvent, gateway::Ready, guild::Guild},
        prelude::*,
    },
    ErrorContext,
};

use tracing::{error, info};
use tracing_subscriber::{EnvFilter, FmtSubscriber};

//Shared data contained in the Context
pub struct GlobalData {
    pub pool: PgPool,
}

struct DBPool;
impl TypeMapKey for DBPool {
    type Value = PgPool;
}

//Context type passed to every command
pub type Context<'a> = poise::Context<'a, GlobalData, BotError>;
pub type Result<T> = std::result::Result<T, BotError>;

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    //sent when a a guild's data is sent to us (one)
    async fn guild_create(
        &self,
        ctx: poise::serenity::prelude::Context,
        guild: Guild,
        is_new: bool,
    ) {
        if is_new {
            let data = ctx.data.read().await;
            let conn = &data.get::<DBPool>().unwrap();
            GuildConfig::new(*conn, GuildConfigBuilder::new(guild.id))
                .await
                .unwrap();
        }
    }
    async fn ready(&self, _: poise::serenity::prelude::Context, ready: Ready) {
        info!("Connected as {}", ready.user.name);
    }

    async fn resume(&self, _: poise::serenity::prelude::Context, _: ResumedEvent) {
        info!("Connection resumed");
    }
}

async fn on_error<'a>(err_ctx: ErrorContext<'_, GlobalData, BotError>, error: BotError) {
    error!("{:?}", error);
    use poise::ErrorContext::*;
    let ctx = match err_ctx {
        Command(ctx) => ctx.ctx(),
        _ => unimplemented!(),
    };

    report_error(ctx, error).await
}

/// Show this help menu
#[poise::command(prefix_command, track_edits, slash_command)]
async fn help(
    ctx: Context<'_>,
    #[description = "Specific command to show help about"] command: Option<String>,
) -> Result<()> {
    poise::builtins::help(
        ctx,
        command.as_deref(),
        "Made with love by Toude#6601",
        poise::builtins::HelpResponseMode::Ephemeral,
    )
    .await?;
    Ok(())
}

/// Register application commands in this guild or globally
///
/// Run with no arguments to register in guild, run with argument "global" to register globally.
#[poise::command(prefix_command, hide_in_help)]
async fn register(ctx: Context<'_>, #[flag] global: bool) -> Result<()> {
    poise::builtins::register_application_commands(ctx, global).await?;

    Ok(())
}

#[tokio::main]
async fn main() {
    // This will load the environment variables located at `./.env`, relative to
    dotenv::dotenv().expect("Failed to load .env file");

    // Initialize the logger to use environment variables.
    //
    // In this case, a good default is setting the environment variable
    // `RUST_LOG` to debug`.
    let subscriber = FmtSubscriber::builder()
        .with_env_filter(EnvFilter::from_default_env())
        .finish();

    tracing::subscriber::set_global_default(subscriber).expect("Failed to start the logger");

    let token = std::env::var("DISCORD_TOKEN").expect("Expected a token in the environment");
    //TODO: is this the right way to do it?
    let http = Http::new_with_token(&token);
    // We fetch the bot's owners and id
    let (owners, bot_id) = match http.get_current_application_info().await {
        Ok(info) => {
            let mut owners = HashSet::new();
            if let Some(team) = info.team {
                owners.insert(team.owner_user_id);
            } else {
                owners.insert(info.owner.id);
            }

            (owners, info.id)
        }
        Err(why) => panic!("Could not access application info: {:?}", why),
    };

    let mut framework_builder = poise::Framework::<GlobalData, BotError>::build()
        .token(token)
        .user_data_setup(move |_ctx, _ready, _framework| {
            Box::pin(async move {
                Ok(GlobalData {
                    pool: establish_connection().await,
                })
            })
        })
        .options(poise::FrameworkOptions {
            // configure framework here
            prefix_options: PrefixFrameworkOptions {
                prefix: Some(
                    env::var("DISCORD_PREFIX").expect("Expected a prefix in the environment"),
                ),

                ..Default::default()
            },
            owners,
            on_error: |error, ctx| Box::pin(on_error(ctx, error)),
            ..Default::default()
        });

    framework_builder = {
        use commands::misc::{clear, ping, provoke_error};
        add_commands!(
            framework_builder,
            help,
            register,
            //clear,
            ping,
            provoke_error
        )
    };

    let framework = framework_builder.build().await.unwrap();

    dbg!(env::var("DISCORD_PREFIX").expect("Expected a prefix in the environment"));

    //running the bot until an error occurs
    if let Err(why) = framework.clone().start().await {
        error!("Client error: {:?}", why);
    }

    //halting the bot through INTERRUPT
    let shard_manager = framework.shard_manager();
    tokio::spawn(async move {
        tokio::signal::ctrl_c()
            .await
            .expect("Could not register ctrl+c handler");
        shard_manager.lock().await.shutdown_all().await;
    });
}

#[macro_export]
macro_rules! add_commands {
    ($framework_builder:ident, $($command:path),*) => {{
        $($framework_builder = $framework_builder.command($command(), |f| f);)*
        $framework_builder
    }};
}
