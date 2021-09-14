use async_trait::async_trait;
use serenity::prelude::*;

#[async_trait]
///Used for command groups that need to be configured for each server.
///The whole process is done through the `config` function.
pub trait Configurable {
    ///This handles the configuration of the extension within discord.
    async fn config(ctx: &Context) -> SerenityError;
}

pub struct IsConfigured {
    pub poll: bool,
    pub slaps: bool,
}

impl Default for IsConfigured {
    fn default() -> Self {
        IsConfigured {
            poll: false,
            slaps: false,
        }
    }
}
