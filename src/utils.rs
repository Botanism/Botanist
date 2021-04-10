use diesel::{backend::Backend, prelude::*};

pub fn parse_ids(text: &str) -> Vec<u64> {
    text.as_bytes()
        .chunks_exact(64)
        .map(|seq| {
            u64::from_str_radix(std::str::from_utf8(seq).expect("u64 sequence incorrect"), 2)
                .unwrap()
        })
        .collect()
}

#[derive(Debug, Queryable)]
pub struct GuildConfig {
    pub id: u64,
    pub welcome_message: String,
    pub goodbye_message: String,
    pub advertise: bool,
    pub admin_chan: u64,
    #[diesel(deserialize_as = "IdList")]
    pub poll_chans: Vec<u64>,
    #[diesel(deserialize_as = "IdList")]
    pub priv_manager: Vec<u64>,
    #[diesel(deserialize_as = "IdList")]
    pub priv_admin: Vec<u64>,
    #[diesel(deserialize_as = "IdList")]
    pub priv_event: Vec<u64>,
}

#[derive(Debug, Queryable)]
pub struct SlapRecord {
    pub message_id: u64,
    pub guild_id: u64,
    pub chan_id: u64,
    reason: String,
}

pub struct IdList(Vec<u64>);

impl Into<Vec<u64>> for IdList {
    fn into(self) -> Vec<u64> {
        self.0
    }
}

impl<DB, ST> Queryable<ST, DB> for IdList
where
    DB: Backend,
    String: Queryable<ST, DB>,
{
    type Row = <String as Queryable<ST, DB>>::Row;

    fn build(row: Self::Row) -> Self {
        IdList(parse_ids(&String::build(row)))
    }
}
