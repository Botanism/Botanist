mod checks;
mod commands;
mod db;
mod utils;

use std::borrow::Cow;
use std::{collections::HashSet, env, sync::Arc};

use sqlx::{query, MySqlPool};

use serenity::{
    async_trait,
    client::bridge::gateway::ShardManager,
    framework::{
        standard::{macros::hook, DispatchError},
        StandardFramework,
    },
    http::{CacheHttp, Http},
    model::{
        channel::Message,
        event::ResumedEvent,
        gateway::Ready,
        guild::{Guild, Member},
        id::{GuildId, UserId},
    },
    prelude::*,
};

use tracing::{error, info};
use tracing_subscriber::{EnvFilter, FmtSubscriber};

use commands::{dev::*, misc::*};
use db::insert_new_guild;
pub struct ShardManagerContainer;

impl TypeMapKey for ShardManagerContainer {
    type Value = Arc<Mutex<ShardManager>>;
}

pub struct BotId(UserId);

impl TypeMapKey for BotId {
    type Value = BotId;
}

pub struct DBConn(MySqlPool);

impl TypeMapKey for DBConn {
    type Value = DBConn;
}

struct Handler;

#[async_trait]
impl EventHandler for Handler {
    //sent when a a guild's data is sent to us (one)
    async fn guild_create(&self, ctx: Context, guild: Guild, is_new: bool) {
        if is_new {
            //move data access into its own block to free access sooner
            let data = ctx.data.read().await;
            let conn = &data.get::<DBConn>().unwrap().0;
            insert_new_guild(&conn, guild.id).await;
        }
    }
    async fn ready(&self, _: Context, ready: Ready) {
        info!("Connected as {}", ready.user.name);
    }

    async fn resume(&self, _: Context, _: ResumedEvent) {
        info!("Connection resumed");
    }
}

//used if the bot couldn't report an error to a user by replying to it
//since it's a fallback it mustn't fail, however acttuall delivery may for network error reasons
//or if the user has blocked DMs
async fn error_report_fallback<Cause: std::fmt::Display>(
    ctx: &Context,
    msg: &Message,
    reason: &Cause,
) {
    //link to the channel
    let chan_name = match msg.channel_id.to_channel(ctx).await {
        Ok(chan) => Cow::Owned(chan.mention().to_string()),
        Err(_) => Cow::Borrowed("an unknown channel"),
    };
    match msg
        .author
        .dm(ctx, |m| {
            m.content(format!(
                "Could not report error in {}\nOriginal error:\t {}",
                chan_name, reason
            ))
        })
        .await
    {
        Err(_) => error!("Fallback error reporting failed because the DM couldn't be sent"),
        _ => (),
    }
}

//reporting an error tthat occured during a command call to the user
async fn report_error<Cause: std::fmt::Display>(ctx: &Context, msg: &Message, cause: Cause) {
    match msg.reply_ping(ctx, &cause).await {
        Err(_) => error_report_fallback(ctx, msg, &cause).await,
        Ok(_) => (),
    }
}

#[hook]
async fn dispatch_error_hook(ctx: &Context, msg: &Message, error: DispatchError) {
    match error {
        DispatchError::CheckFailed(_, reason) => report_error(ctx, msg, reason).await,
        DispatchError::OnlyForOwners => {
            report_error(ctx, msg, "You need `owner` privilege to run this.").await
        }
        _ => error!("Unhandled dispatch error {:?}", error),
    };
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

    let token = env::var("DISCORD_TOKEN").expect("Expected a token in the environment");

    let http = Http::new_with_token(&token);

    // We will fetch your bot's owners and id
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

    let prefix = env::var("DISCORD_PREFIX").expect("Expected a prefix in the environment");

    // Create the framework
    let framework = StandardFramework::new()
        .configure(|c| {
            c.owners(owners)
                .prefix(prefix.as_str())
                .on_mention(Some(bot_id))
                .with_whitespace(true)
        })
        .on_dispatch_error(dispatch_error_hook)
        .group(&DEVELOPMENT_GROUP)
        .group(&MISC_GROUP);

    let mut client = Client::builder(&token)
        .framework(framework)
        .event_handler(Handler)
        .await
        .expect("Err creating client");

    //DB setup
    let db_url = env::var("DATABASE_URL").expect("`DATABASE_URL` is not set");
    let pool = MySqlPool::connect(&db_url)
        .await
        .expect("Could not establish DB connection");

    {
        let mut data = client.data.write().await;
        data.insert::<ShardManagerContainer>(client.shard_manager.clone());
        data.insert::<BotId>(BotId(bot_id));
        data.insert::<DBConn>(DBConn(pool));
    }

    let shard_manager = client.shard_manager.clone();

    tokio::spawn(async move {
        tokio::signal::ctrl_c()
            .await
            .expect("Could not register ctrl+c handler");
        shard_manager.lock().await.shutdown_all().await;
    });

    if let Err(why) = client.start().await {
        error!("Client error: {:?}", why);
    }
}
