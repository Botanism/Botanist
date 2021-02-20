-- Your SQL goes here
create table guilds (
    id bigint(64) unsigned primary key,
    welcome_message varchar(2048),
    goodbye_message varchar(2048),
    advertise tinyint(1),
    admin_chan bigint(64) unsigned,
    poll_chans text,
    priv_manager text,
    priv_admin text,
    priv_event text
);

create table slaps (
    message_id bigint(64) unsigned primary key,
    guild_id bigint(64) unsigned,
    chan_id bigint(64) unsigned,
    reason varchar(2048)
);