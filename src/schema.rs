table! {
    guilds (id) {
        id -> Unsigned<Bigint>,
        welcome_message -> Nullable<Varchar>,
        goodbye_message -> Nullable<Varchar>,
        advertise -> Nullable<Bool>,
        admin_chan -> Nullable<Unsigned<Bigint>>,
        poll_chans -> Nullable<Text>,
        priv_manager -> Nullable<Text>,
        priv_admin -> Nullable<Text>,
        priv_event -> Nullable<Text>,
    }
}

table! {
    slaps (message_id) {
        message_id -> Unsigned<Bigint>,
        guild_id -> Nullable<Unsigned<Bigint>>,
        chan_id -> Nullable<Unsigned<Bigint>>,
        reason -> Nullable<Varchar>,
    }
}

allow_tables_to_appear_in_same_query!(
    guilds,
    slaps,
);
